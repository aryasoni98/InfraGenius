#!/bin/bash
# Local Production Setup Script
# Sets up a production-like environment on your local machine

set -e

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
║            DevOps/SRE MCP Server                             ║
║         Local Production Environment Setup                   ║
║                                                              ║
║  This will create a production-like environment locally     ║
║  with Docker, Kubernetes, monitoring, and all services      ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check system requirements
check_system_requirements() {
    log "Checking system requirements..."
    
    # Check if running on macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        warning "This script is optimized for macOS. Some adjustments may be needed for other systems."
    fi
    
    # Check available resources
    TOTAL_RAM=$(sysctl -n hw.memsize)
    RAM_GB=$((TOTAL_RAM / 1024 / 1024 / 1024))
    
    if [ $RAM_GB -lt 16 ]; then
        warning "Recommended: 16GB+ RAM for optimal performance. You have ${RAM_GB}GB."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        success "System has ${RAM_GB}GB RAM - sufficient for production setup"
    fi
    
    # Check disk space
    AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "${AVAILABLE_SPACE%.*}" -lt 20 ]; then
        error "Need at least 20GB free disk space. Available: ${AVAILABLE_SPACE}GB"
    fi
    
    success "System requirements check passed"
}

# Install required tools
install_tools() {
    log "Installing required tools..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        log "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        success "Homebrew already installed"
    fi
    
    # List of required tools
    TOOLS=(
        "docker"
        "kubectl"
        "helm"
        "k3d"
        "redis"
        "postgresql@15"
        "jq"
        "yq"
    )
    
    for tool in "${TOOLS[@]}"; do
        if ! brew list "$tool" &> /dev/null; then
            log "Installing $tool..."
            brew install "$tool"
        else
            success "$tool already installed"
        fi
    done
    
    # Start Docker if not running
    if ! docker info &> /dev/null; then
        log "Starting Docker..."
        open -a Docker
        
        # Wait for Docker to start
        while ! docker info &> /dev/null; do
            log "Waiting for Docker to start..."
            sleep 5
        done
    fi
    
    success "All required tools installed"
}

# Setup local Kubernetes cluster
setup_kubernetes() {
    log "Setting up local Kubernetes cluster with k3d..."
    
    CLUSTER_NAME="mcp-production-local"
    
    # Check if cluster already exists
    if k3d cluster list | grep -q "$CLUSTER_NAME"; then
        warning "Cluster $CLUSTER_NAME already exists"
        read -p "Delete and recreate? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            k3d cluster delete "$CLUSTER_NAME"
        else
            success "Using existing cluster"
            return
        fi
    fi
    
    # Create k3d cluster with production-like configuration
    k3d cluster create "$CLUSTER_NAME" \
        --agents 2 \
        --port "8080:80@loadbalancer" \
        --port "8443:443@loadbalancer" \
        --k3s-arg "--disable=traefik@server:0" \
        --registry-create "mcp-registry.localhost:5000" \
        --volume "/tmp/k3d-mcp-storage:/var/lib/rancher/k3s/storage@all"
    
    # Wait for cluster to be ready
    kubectl wait --for=condition=ready nodes --all --timeout=300s
    
    success "Kubernetes cluster created successfully"
}

# Setup local databases
setup_databases() {
    log "Setting up local databases..."
    
    # Start PostgreSQL
    if ! brew services list | grep postgresql@15 | grep -q started; then
        log "Starting PostgreSQL..."
        brew services start postgresql@15
        sleep 5
    else
        success "PostgreSQL already running"
    fi
    
    # Create database and user
    log "Creating MCP database..."
    psql postgres -c "CREATE DATABASE mcpserver;" 2>/dev/null || log "Database mcpserver already exists"
    psql postgres -c "CREATE USER mcpuser WITH PASSWORD 'mcppass123';" 2>/dev/null || log "User mcpuser already exists"
    psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE mcpserver TO mcpuser;" 2>/dev/null
    
    # Start Redis
    if ! brew services list | grep redis | grep -q started; then
        log "Starting Redis..."
        brew services start redis
        sleep 3
    else
        success "Redis already running"
    fi
    
    # Test connections
    psql "postgresql://mcpuser:mcppass123@localhost:5432/mcpserver" -c "SELECT version();" > /dev/null
    redis-cli ping > /dev/null
    
    success "Databases setup and running"
}

# Build production Docker image
build_docker_image() {
    log "Building production Docker image..."
    
    # Create production Dockerfile
    cat > Dockerfile.production << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "server.py"]
EOF

    # Build the image
    docker build -f Dockerfile.production -t mcp-server:production .
    
    # Tag for local registry
    docker tag mcp-server:production localhost:5000/mcp-server:production
    docker push localhost:5000/mcp-server:production
    
    success "Production Docker image built and pushed to local registry"
}

# Create production Kubernetes manifests
create_production_manifests() {
    log "Creating production Kubernetes manifests..."
    
    mkdir -p k8s/local-production
    
    # Namespace
    cat > k8s/local-production/namespace.yaml << 'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: mcp-production
  labels:
    name: mcp-production
    environment: local-production
EOF

    # ConfigMap with production configuration
    cat > k8s/local-production/configmap.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-server-config
  namespace: mcp-production
data:
  config.json: |
    {
      "server": {
        "name": "DevOps SRE Platform MCP Server",
        "version": "1.0.0",
        "host": "0.0.0.0",
        "port": 8000,
        "environment": "local-production",
        "debug": false,
        "performance_optimizations": {
          "enabled": true,
          "cache_size": 1000,
          "compression": true,
          "async_processing": true
        }
      },
      "ollama": {
        "model": "gpt-oss:latest",
        "base_url": "http://ollama-service:11434",
        "timeout": 300,
        "max_retries": 3
      },
      "database": {
        "url": "postgresql://mcpuser:mcppass123@host.k3d.internal:5432/mcpserver",
        "pool_size": 20,
        "max_overflow": 30,
        "pool_timeout": 30
      },
      "redis": {
        "url": "redis://host.k3d.internal:6379/0",
        "max_connections": 50,
        "retry_on_timeout": true
      },
      "domains": {
        "devops": {
          "enabled": true,
          "features": ["ci_cd", "infrastructure", "monitoring", "automation"]
        },
        "sre": {
          "enabled": true,
          "features": ["reliability", "incident_response", "slo_management", "observability"]
        },
        "cloud": {
          "enabled": true,
          "features": ["architecture", "security", "cost_optimization", "migration"]
        },
        "platform": {
          "enabled": true,
          "features": ["developer_experience", "api_design", "self_service"]
        }
      },
      "security": {
        "rate_limiting": {
          "enabled": true,
          "requests_per_minute": 60,
          "burst_size": 10
        },
        "authentication": {
          "jwt_secret": "local-production-secret-change-in-real-production",
          "token_expiry": 3600
        }
      },
      "monitoring": {
        "metrics_enabled": true,
        "health_check_interval": 30,
        "performance_tracking": true
      }
    }
EOF

    # Secrets
    cat > k8s/local-production/secrets.yaml << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: mcp-server-secrets
  namespace: mcp-production
type: Opaque
data:
  jwt-secret: bG9jYWwtcHJvZHVjdGlvbi1zZWNyZXQtY2hhbmdlLWluLXJlYWwtcHJvZHVjdGlvbg==
  db-password: bWNwcGFzczEyMw==
EOF

    # MCP Server Deployment
    cat > k8s/local-production/mcp-server.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  namespace: mcp-production
  labels:
    app: mcp-server
    version: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
        version: production
    spec:
      containers:
      - name: mcp-server
        image: localhost:5000/mcp-server:production
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: CONFIG_PATH
          value: /config/config.json
        - name: ENVIRONMENT
          value: local-production
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: mcp-server-secrets
              key: jwt-secret
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
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30
      volumes:
      - name: config
        configMap:
          name: mcp-server-config
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server-service
  namespace: mcp-production
  labels:
    app: mcp-server
spec:
  selector:
    app: mcp-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    name: http
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-server-hpa
  namespace: mcp-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF

    # Ollama Deployment (if you want to run Ollama locally)
    cat > k8s/local-production/ollama.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: mcp-production
  labels:
    app: ollama
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
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        env:
        - name: OLLAMA_HOST
          value: "0.0.0.0"
        - name: OLLAMA_KEEP_ALIVE
          value: "5m"
        resources:
          requests:
            cpu: 2000m
            memory: 8Gi
          limits:
            cpu: 4000m
            memory: 16Gi
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama
        readinessProbe:
          httpGet:
            path: /
            port: 11434
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: ollama-data
        persistentVolumeClaim:
          claimName: ollama-storage
---
apiVersion: v1
kind: Service
metadata:
  name: ollama-service
  namespace: mcp-production
spec:
  selector:
    app: ollama
  ports:
  - protocol: TCP
    port: 11434
    targetPort: 11434
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ollama-storage
  namespace: mcp-production
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
EOF

    # Ingress
    cat > k8s/local-production/ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-server-ingress
  namespace: mcp-production
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
  - host: mcp-server.local
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

    success "Production Kubernetes manifests created"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring stack..."
    
    # Add Prometheus Helm repository
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    # Install Prometheus and Grafana
    helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set grafana.adminPassword=admin123 \
        --set prometheus.prometheusSpec.retention=7d \
        --set grafana.persistence.enabled=true \
        --set grafana.persistence.size=10Gi
    
    # Wait for monitoring to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n monitoring --timeout=300s
    
    success "Monitoring stack installed"
}

# Setup ingress controller
setup_ingress() {
    log "Setting up NGINX Ingress Controller..."
    
    # Install NGINX Ingress Controller
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
    
    # Wait for ingress controller to be ready
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    
    success "NGINX Ingress Controller installed"
}

# Deploy the application
deploy_application() {
    log "Deploying MCP Server to local production environment..."
    
    # Apply all manifests
    kubectl apply -f k8s/local-production/
    
    # Wait for deployments to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/mcp-server -n mcp-production
    
    # Check if Ollama should be deployed
    read -p "Deploy Ollama locally? (requires 16GB+ RAM) (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl wait --for=condition=available --timeout=600s deployment/ollama -n mcp-production
        
        # Pull and run the model
        log "Pulling gpt-oss:latest model (this may take a while)..."
        kubectl exec -n mcp-production deployment/ollama -- ollama pull gpt-oss:latest
    else
        # Remove Ollama deployment
        kubectl delete -f k8s/local-production/ollama.yaml --ignore-not-found=true
        warning "Ollama not deployed. You'll need to configure external Ollama service."
    fi
    
    success "Application deployed successfully"
}

# Setup local DNS
setup_local_dns() {
    log "Setting up local DNS..."
    
    # Add entries to /etc/hosts
    if ! grep -q "mcp-server.local" /etc/hosts; then
        echo "127.0.0.1 mcp-server.local" | sudo tee -a /etc/hosts
        echo "127.0.0.1 grafana.local" | sudo tee -a /etc/hosts
        echo "127.0.0.1 prometheus.local" | sudo tee -a /etc/hosts
        success "Local DNS entries added to /etc/hosts"
    else
        success "Local DNS entries already exist"
    fi
}

# Show access information
show_access_info() {
    log "Getting service access information..."
    
    # Port forward services in background
    kubectl port-forward -n mcp-production svc/mcp-server-service 8080:80 &
    MCP_PF_PID=$!
    
    kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80 &
    GRAFANA_PF_PID=$!
    
    kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 &
    PROMETHEUS_PF_PID=$!
    
    # Save PIDs for cleanup
    echo "$MCP_PF_PID $GRAFANA_PF_PID $PROMETHEUS_PF_PID" > .port_forward_pids
    
    sleep 5
    
    echo -e "${GREEN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                 LOCAL PRODUCTION SETUP COMPLETE!            ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    log "🎉 Your local production environment is ready!"
    log ""
    log "📊 Service Access URLs:"
    log "   🚀 MCP Server API: http://localhost:8080"
    log "   📈 Grafana Dashboard: http://localhost:3000 (admin/admin123)"
    log "   📊 Prometheus: http://localhost:9090"
    log ""
    log "🔍 Health Checks:"
    log "   Health: http://localhost:8080/health"
    log "   Ready: http://localhost:8080/ready"
    log "   Metrics: http://localhost:8080/metrics"
    log ""
    log "🛠️  Useful Commands:"
    log "   View pods: kubectl get pods -n mcp-production"
    log "   View logs: kubectl logs -f deployment/mcp-server -n mcp-production"
    log "   Scale up: kubectl scale deployment mcp-server --replicas=5 -n mcp-production"
    log "   Check HPA: kubectl get hpa -n mcp-production"
    log ""
    log "💾 Database Connections:"
    log "   PostgreSQL: postgresql://mcpuser:mcppass123@localhost:5432/mcpserver"
    log "   Redis: redis://localhost:6379/0"
    log ""
    log "🧪 Test the API:"
    log "   curl http://localhost:8080/health"
    log "   curl -X POST http://localhost:8080/analyze -H 'Content-Type: application/json' -d '{\"prompt\":\"test\"}'"
    log ""
    log "🔧 Monitoring:"
    log "   - Grafana has pre-configured dashboards for Kubernetes and application metrics"
    log "   - Prometheus is scraping metrics from all services"
    log "   - HPA will auto-scale based on CPU/memory usage"
    log ""
    log "⚠️  To stop port forwarding:"
    log "   kill \$(cat .port_forward_pids)"
}

# Cleanup function
cleanup() {
    log "Cleaning up local production environment..."
    
    # Kill port forwards
    if [ -f .port_forward_pids ]; then
        kill $(cat .port_forward_pids) 2>/dev/null || true
        rm .port_forward_pids
    fi
    
    # Delete Kubernetes resources
    kubectl delete namespace mcp-production --ignore-not-found=true
    helm uninstall prometheus -n monitoring 2>/dev/null || true
    kubectl delete namespace monitoring --ignore-not-found=true
    
    # Stop local databases
    brew services stop postgresql@15
    brew services stop redis
    
    # Delete k3d cluster
    k3d cluster delete mcp-production-local 2>/dev/null || true
    
    # Remove Docker images
    docker rmi mcp-server:production localhost:5000/mcp-server:production 2>/dev/null || true
    
    # Remove /etc/hosts entries
    sudo sed -i '' '/mcp-server.local/d' /etc/hosts
    sudo sed -i '' '/grafana.local/d' /etc/hosts
    sudo sed -i '' '/prometheus.local/d' /etc/hosts
    
    success "Local production environment cleaned up"
}

# Main function
main() {
    show_banner
    
    case "${1:-setup}" in
        "setup")
            check_system_requirements
            install_tools
            setup_kubernetes
            setup_databases
            build_docker_image
            create_production_manifests
            setup_ingress
            setup_monitoring
            deploy_application
            setup_local_dns
            show_access_info
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "Usage: $0 [setup|cleanup]"
            echo ""
            echo "Commands:"
            echo "  setup   - Set up local production environment"
            echo "  cleanup - Clean up and remove all components"
            exit 1
            ;;
    esac
}

# Run the script
main "$@"
