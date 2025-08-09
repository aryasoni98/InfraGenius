#!/bin/bash
# AWS Deployment Script for DevOps/SRE MCP Server
# Deploys the complete infrastructure using Terraform and Kubernetes

set -e

# Configuration
PROJECT_NAME="devops-sre-mcp"
AWS_REGION="us-east-1"
CLUSTER_NAME="${PROJECT_NAME}-cluster"
NAMESPACE="mcp-server"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        error "AWS CLI not found. Please install it first."
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        error "kubectl not found. Please install it first."
    fi
    
    # Check terraform
    if ! command -v terraform &> /dev/null; then
        error "Terraform not found. Please install it first."
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        error "Helm not found. Please install it first."
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured. Run 'aws configure' first."
    fi
    
    success "All prerequisites met"
}

# Create Terraform configuration
create_terraform_config() {
    log "Creating Terraform configuration..."
    
    mkdir -p terraform/aws
    
    cat > terraform/aws/main.tf << 'EOF'
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "${var.project_name}-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = true
  enable_dns_hostnames = true
  enable_dns_support = true
  
  tags = {
    Environment = var.environment
    Project = var.project_name
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = var.cluster_name
  cluster_version = "1.28"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  cluster_endpoint_public_access = true
  cluster_endpoint_private_access = true
  
  # Node groups
  eks_managed_node_groups = {
    main = {
      instance_types = ["t3.medium"]
      min_size     = 2
      max_size     = 10
      desired_size = 3
      
      k8s_labels = {
        Environment = var.environment
        NodeGroup = "main"
      }
    }
    
    gpu = {
      instance_types = ["g4dn.xlarge"]
      min_size     = 1
      max_size     = 3
      desired_size = 1
      
      k8s_labels = {
        Environment = var.environment
        NodeGroup = "gpu"
        WorkloadType = "gpu"
      }
      
      taints = {
        gpu = {
          key    = "nvidia.com/gpu"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
    }
  }
  
  tags = {
    Environment = var.environment
    Project = var.project_name
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier = "${var.project_name}-postgres"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type         = "gp2"
  storage_encrypted    = true
  
  db_name  = "mcpserver"
  username = "mcpuser"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Sun:04:00-Sun:05:00"
  
  skip_final_snapshot = var.environment == "dev"
  deletion_protection = var.environment == "prod"
  
  tags = {
    Environment = var.environment
    Project = var.project_name
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = module.vpc.private_subnets
  
  tags = {
    Name = "${var.project_name} DB subnet group"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-cache-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.project_name}-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
  
  tags = {
    Environment = var.environment
    Project = var.project_name
  }
}

# Security Groups
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "redis" {
  name_prefix = "${var.project_name}-redis"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = module.vpc.public_subnets
  
  enable_deletion_protection = var.environment == "prod"
  
  tags = {
    Environment = var.environment
    Project = var.project_name
  }
}

resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-alb"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
EOF

    cat > terraform/aws/variables.tf << 'EOF'
variable "project_name" {
  description = "Project name"
  type        = string
  default     = "devops-sre-mcp"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "devops-sre-mcp-cluster"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
EOF

    cat > terraform/aws/outputs.tf << 'EOF'
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "load_balancer_dns" {
  description = "Load balancer DNS name"
  value       = aws_lb.main.dns_name
}
EOF

    success "Terraform configuration created"
}

# Deploy infrastructure
deploy_infrastructure() {
    log "Deploying infrastructure with Terraform..."
    
    cd terraform/aws
    
    # Generate random password for database
    DB_PASSWORD=$(openssl rand -base64 32)
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan -var="db_password=${DB_PASSWORD}"
    
    # Apply configuration
    terraform apply -var="db_password=${DB_PASSWORD}" -auto-approve
    
    # Save outputs
    terraform output -json > ../../terraform_outputs.json
    
    cd ../..
    
    success "Infrastructure deployed successfully"
}

# Configure kubectl
configure_kubectl() {
    log "Configuring kubectl..."
    
    aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME
    
    # Test connection
    kubectl cluster-info
    
    success "kubectl configured"
}

# Create Kubernetes manifests
create_k8s_manifests() {
    log "Creating Kubernetes manifests..."
    
    mkdir -p k8s/aws
    
    # Namespace
    cat > k8s/aws/namespace.yaml << EOF
apiVersion: v1
kind: Namespace
metadata:
  name: $NAMESPACE
  labels:
    name: $NAMESPACE
EOF

    # ConfigMap
    cat > k8s/aws/configmap.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-server-config
  namespace: $NAMESPACE
data:
  config.json: |
    {
      "server": {
        "name": "DevOps SRE Platform MCP Server",
        "version": "1.0.0",
        "host": "0.0.0.0",
        "port": 8000,
        "environment": "production"
      },
      "ollama": {
        "model": "gpt-oss:latest",
        "base_url": "http://ollama-service:11434",
        "timeout": 300
      },
      "database": {
        "url": "postgresql://mcpuser:password@postgres-service:5432/mcpserver"
      },
      "redis": {
        "url": "redis://redis-service:6379"
      },
      "domains": {
        "devops": {"enabled": true},
        "sre": {"enabled": true},
        "cloud": {"enabled": true},
        "platform": {"enabled": true}
      }
    }
EOF

    # MCP Server Deployment
    cat > k8s/aws/mcp-server.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  namespace: $NAMESPACE
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: devops-sre-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: CONFIG_PATH
          value: /config/config.json
        - name: ENVIRONMENT
          value: production
        volumeMounts:
        - name: config
          mountPath: /config
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: mcp-server-config
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server-service
  namespace: $NAMESPACE
spec:
  selector:
    app: mcp-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
EOF

    # Ollama Deployment
    cat > k8s/aws/ollama.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      nodeSelector:
        WorkloadType: gpu
      tolerations:
      - key: nvidia.com/gpu
        operator: Equal
        value: "true"
        effect: NoSchedule
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        env:
        - name: OLLAMA_HOST
          value: "0.0.0.0"
        resources:
          requests:
            nvidia.com/gpu: 1
            cpu: 2000m
            memory: 8Gi
          limits:
            nvidia.com/gpu: 1
            cpu: 4000m
            memory: 16Gi
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama
      volumes:
      - name: ollama-data
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: ollama-service
  namespace: $NAMESPACE
spec:
  selector:
    app: ollama
  ports:
  - protocol: TCP
    port: 11434
    targetPort: 11434
  type: ClusterIP
EOF

    # Ingress
    cat > k8s/aws/ingress.yaml << EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-server-ingress
  namespace: $NAMESPACE
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/healthcheck-path: /health
spec:
  rules:
  - host: api.devops-mcp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-server-service
            port:
              number: 80
EOF

    success "Kubernetes manifests created"
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    log "Deploying to Kubernetes..."
    
    # Install AWS Load Balancer Controller
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName=$CLUSTER_NAME \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller
    
    # Install NVIDIA device plugin
    kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.1/nvidia-device-plugin.yml
    
    # Deploy application
    kubectl apply -f k8s/aws/namespace.yaml
    kubectl apply -f k8s/aws/configmap.yaml
    kubectl apply -f k8s/aws/mcp-server.yaml
    kubectl apply -f k8s/aws/ollama.yaml
    kubectl apply -f k8s/aws/ingress.yaml
    
    # Wait for deployments
    kubectl wait --for=condition=available --timeout=300s deployment/mcp-server -n $NAMESPACE
    kubectl wait --for=condition=available --timeout=600s deployment/ollama -n $NAMESPACE
    
    success "Application deployed to Kubernetes"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Install Prometheus and Grafana using Helm
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set grafana.adminPassword=admin123
    
    success "Monitoring setup complete"
}

# Main deployment function
main() {
    log "Starting AWS deployment for DevOps/SRE MCP Server"
    log "=================================================="
    
    check_prerequisites
    create_terraform_config
    deploy_infrastructure
    configure_kubectl
    create_k8s_manifests
    deploy_to_kubernetes
    setup_monitoring
    
    success "🎉 AWS deployment completed successfully!"
    log ""
    log "Next steps:"
    log "1. Update DNS to point to the load balancer"
    log "2. Configure SSL certificates"
    log "3. Set up monitoring alerts"
    log "4. Run load tests"
    log ""
    log "Access your application:"
    log "- API: http://$(kubectl get ingress mcp-server-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')"
    log "- Grafana: kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
    log ""
    
    # Show cost estimate
    log "💰 Estimated monthly cost: ~$800-1000"
    log "   - EKS cluster: $200"
    log "   - GPU instance: $600"
    log "   - RDS: $80"
    log "   - Other services: $120"
}

# Run deployment
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
