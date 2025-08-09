#!/bin/bash
# Quick Deploy Script - Phase 1 Lean Deployment
# Optimized for cost-effectiveness and rapid deployment

set -e

PROJECT_NAME="devops-sre-mcp"
REGION="us-east-1"
ENVIRONMENT="production"
SIZE="small"  # Cost-optimized

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

show_banner() {
    echo -e "${GREEN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║               DevOps/SRE MCP Server                          ║
║              Quick Deploy - Phase 1                         ║
║         Cost-Optimized Production Deployment                ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    local missing_tools=()
    
    command -v aws >/dev/null 2>&1 || missing_tools+=("aws-cli")
    command -v kubectl >/dev/null 2>&1 || missing_tools+=("kubectl")
    command -v helm >/dev/null 2>&1 || missing_tools+=("helm")
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        error "Missing tools: ${missing_tools[*]}. Please install them first."
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        error "AWS credentials not configured. Run 'aws configure' first."
    fi
    
    success "All prerequisites met"
}

# Create cost-optimized Terraform config
create_lean_terraform() {
    log "Creating cost-optimized Terraform configuration..."
    
    mkdir -p terraform/lean
    
    cat > terraform/lean/main.tf << 'EOF'
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC - Minimal setup
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "${var.project_name}-vpc"
    Environment = "lean-production"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public Subnets (2 AZs for HA)
resource "aws_subnet" "public" {
  count = 2
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${var.project_name}-public-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count = 2
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "${var.project_name}-private-${count.index + 1}"
  }
}

# NAT Gateway (single for cost optimization)
resource "aws_eip" "nat" {
  domain = "vpc"
  tags = { Name = "${var.project_name}-nat-eip" }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  
  tags = { Name = "${var.project_name}-nat" }
  depends_on = [aws_internet_gateway.main]
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = { Name = "${var.project_name}-public-rt" }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }
  
  tags = { Name = "${var.project_name}-private-rt" }
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count = 2
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = 2
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# EKS Cluster - Cost Optimized
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.28"
  
  vpc_config {
    subnet_ids              = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
    endpoint_private_access = true
    endpoint_public_access  = true
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_service_policy,
  ]
  
  tags = {
    Environment = "lean-production"
  }
}

# EKS Node Group - Small instances
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "main-nodes"
  node_role_arn   = aws_iam_role.eks_node_group.arn
  subnet_ids      = aws_subnet.private[*].id
  
  instance_types = ["t3.small"]
  capacity_type  = "SPOT"  # Cost optimization
  
  scaling_config {
    desired_size = 2
    max_size     = 4
    min_size     = 1
  }
  
  update_config {
    max_unavailable = 1
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]
  
  tags = {
    Environment = "lean-production"
  }
}

# GPU Node Group - Single instance
resource "aws_eks_node_group" "gpu" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "gpu-nodes"
  node_role_arn   = aws_iam_role.eks_node_group.arn
  subnet_ids      = aws_subnet.private[*].id
  
  instance_types = ["g4dn.large"]  # Smaller GPU instance
  capacity_type  = "ON_DEMAND"
  
  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 0  # Can scale to 0 for cost savings
  }
  
  taint {
    key    = "nvidia.com/gpu"
    value  = "true"
    effect = "NO_SCHEDULE"
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]
  
  tags = {
    Environment = "lean-production"
    WorkloadType = "gpu"
  }
}

# RDS - Micro instance
resource "aws_db_instance" "postgres" {
  identifier = "${var.project_name}-db"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 50
  storage_type         = "gp2"
  storage_encrypted    = true
  
  db_name  = "mcpserver"
  username = "mcpuser"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 3  # Reduced for cost
  backup_window          = "03:00-04:00"
  maintenance_window     = "Sun:04:00-Sun:05:00"
  
  skip_final_snapshot = true  # For lean deployment
  deletion_protection = false
  
  tags = {
    Environment = "lean-production"
  }
}

# ElastiCache - Micro instance
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
    Environment = "lean-production"
  }
}

# Required data sources and remaining resources...
data "aws_availability_zones" "available" {
  state = "available"
}

# IAM Roles (abbreviated for space)
resource "aws_iam_role" "eks_cluster" {
  name = "${var.project_name}-eks-cluster-role"
  
  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })
}

resource "aws_iam_role" "eks_node_group" {
  name = "${var.project_name}-eks-node-group-role"
  
  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })
}

# IAM Policy Attachments
resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_iam_role_policy_attachment" "eks_service_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_group.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_group.name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_group.name
}

# Security Groups and Subnet Groups
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
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
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
EOF

    # Variables file
    cat > terraform/lean/variables.tf << 'EOF'
variable "project_name" {
  default = "devops-sre-mcp"
}

variable "aws_region" {
  default = "us-east-1"
}

variable "cluster_name" {
  default = "devops-sre-mcp-cluster"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
EOF

    # Outputs
    cat > terraform/lean/outputs.tf << 'EOF'
output "cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}

output "cluster_name" {
  value = aws_eks_cluster.main.name
}

output "database_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}
EOF

    success "Lean Terraform configuration created"
}

# Deploy lean infrastructure
deploy_lean_infrastructure() {
    log "Deploying cost-optimized infrastructure..."
    
    cd terraform/lean
    
    # Generate secure password
    DB_PASSWORD=$(openssl rand -base64 16)
    echo "Database password: $DB_PASSWORD" > ../../.db_password
    chmod 600 ../../.db_password
    
    terraform init
    terraform plan -var="db_password=${DB_PASSWORD}"
    
    warning "About to deploy infrastructure. Estimated cost: ~$450/month"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply -var="db_password=${DB_PASSWORD}" -auto-approve
        terraform output -json > ../../terraform_outputs.json
        success "Infrastructure deployed successfully"
    else
        warning "Deployment cancelled"
        exit 0
    fi
    
    cd ../..
}

# Configure kubectl for EKS
configure_kubectl() {
    log "Configuring kubectl for EKS..."
    
    CLUSTER_NAME=$(cat terraform_outputs.json | jq -r '.cluster_name.value')
    aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME
    
    kubectl cluster-info
    success "kubectl configured"
}

# Create lean Kubernetes manifests
create_lean_k8s() {
    log "Creating lean Kubernetes manifests..."
    
    mkdir -p k8s/lean
    
    # Namespace
    cat > k8s/lean/namespace.yaml << 'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: mcp-server
  labels:
    name: mcp-server
EOF

    # ConfigMap with lean configuration
    cat > k8s/lean/configmap.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-server-config
  namespace: mcp-server
data:
  config.json: |
    {
      "server": {
        "name": "DevOps SRE MCP Server - Lean",
        "version": "1.0.0",
        "host": "0.0.0.0",
        "port": 8000,
        "environment": "lean-production"
      },
      "ollama": {
        "model": "gpt-oss:latest",
        "base_url": "http://ollama-service:11434",
        "timeout": 120
      },
      "performance": {
        "cache_enabled": true,
        "compression_enabled": true,
        "auto_scaling": true
      },
      "domains": {
        "devops": {"enabled": true},
        "sre": {"enabled": true},
        "cloud": {"enabled": true},
        "platform": {"enabled": true}
      }
    }
EOF

    # MCP Server deployment - lean configuration
    cat > k8s/lean/mcp-server.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  namespace: mcp-server
spec:
  replicas: 2
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
          value: lean-production
        volumeMounts:
        - name: config
          mountPath: /config
        resources:
          requests:
            cpu: 200m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 2Gi
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
  namespace: mcp-server
spec:
  selector:
    app: mcp-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-server-hpa
  namespace: mcp-server
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-server
  minReplicas: 2
  maxReplicas: 6
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
EOF

    # Ollama deployment - single instance
    cat > k8s/lean/ollama.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: mcp-server
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
        - name: OLLAMA_KEEP_ALIVE
          value: "5m"  # Auto-unload models after 5min
        resources:
          requests:
            nvidia.com/gpu: 1
            cpu: 1000m
            memory: 4Gi
          limits:
            nvidia.com/gpu: 1
            cpu: 2000m
            memory: 8Gi
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
  namespace: mcp-server
spec:
  selector:
    app: ollama
  ports:
  - protocol: TCP
    port: 11434
    targetPort: 11434
  type: ClusterIP
EOF

    # Simple ingress for cost optimization
    cat > k8s/lean/ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-server-ingress
  namespace: mcp-server
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/healthcheck-path: /health
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}]'
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-server-service
            port:
              number: 80
EOF

    success "Lean Kubernetes manifests created"
}

# Deploy to Kubernetes
deploy_to_k8s() {
    log "Deploying to Kubernetes..."
    
    # Install AWS Load Balancer Controller
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    
    CLUSTER_NAME=$(cat terraform_outputs.json | jq -r '.cluster_name.value')
    
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName=$CLUSTER_NAME \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller \
        --set region=$REGION
    
    # Install NVIDIA device plugin
    kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.1/nvidia-device-plugin.yml
    
    # Deploy application
    kubectl apply -f k8s/lean/
    
    # Wait for deployments
    kubectl wait --for=condition=available --timeout=300s deployment/mcp-server -n mcp-server
    kubectl wait --for=condition=available --timeout=600s deployment/ollama -n mcp-server
    
    success "Application deployed to Kubernetes"
}

# Setup basic monitoring
setup_basic_monitoring() {
    log "Setting up basic monitoring..."
    
    # Simple monitoring with metrics-server
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    
    success "Basic monitoring setup complete"
}

# Show deployment summary
show_summary() {
    echo -e "${GREEN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                    DEPLOYMENT COMPLETE!                     ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    LOAD_BALANCER=$(kubectl get ingress mcp-server-ingress -n mcp-server -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "Pending...")
    
    log "🎉 Your DevOps/SRE MCP Server is now deployed!"
    log ""
    log "📊 Deployment Summary:"
    log "   Environment: Lean Production"
    log "   Estimated Cost: ~$450/month"
    log "   Break-even: ~36 paid users"
    log ""
    log "🔗 Access URLs:"
    log "   API Endpoint: http://$LOAD_BALANCER"
    log "   Health Check: http://$LOAD_BALANCER/health"
    log ""
    log "📋 Next Steps:"
    log "   1. Set up domain and SSL certificate"
    log "   2. Configure user management and billing"
    log "   3. Start beta testing with 25-50 users"
    log "   4. Monitor costs and performance"
    log ""
    log "🎯 Business Targets:"
    log "   - Month 1: 40 paid users, $2,500/month revenue"
    log "   - Month 3: 100 paid users, $6,250/month revenue"
    log "   - Break-even: 36 paid users"
    log ""
    log "💰 Cost Breakdown:"
    log "   - Compute: ~$150/month"
    log "   - GPU: ~$200/month"
    log "   - Database: ~$25/month"
    log "   - Storage & Network: ~$75/month"
    log ""
    log "🚀 Ready to launch your DevOps/SRE AI platform!"
}

# Cleanup function
cleanup() {
    if [ "$1" = "destroy" ]; then
        warning "Destroying infrastructure..."
        cd terraform/lean
        terraform destroy -auto-approve
        cd ../..
        rm -rf terraform/lean k8s/lean
        success "Infrastructure destroyed"
    fi
}

# Main function
main() {
    show_banner
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_lean_terraform
            deploy_lean_infrastructure
            configure_kubectl
            create_lean_k8s
            deploy_to_k8s
            setup_basic_monitoring
            show_summary
            ;;
        "destroy")
            cleanup destroy
            ;;
        *)
            echo "Usage: $0 [deploy|destroy]"
            exit 1
            ;;
    esac
}

# Run the script
main "$@"
