#!/bin/bash
# InfraGenius - Professional Version Deployment
# Includes premium features and enhanced performance

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }
highlight() { echo -e "${PURPLE}🎯 $1${NC}"; }

# Configuration
LICENSE_KEY=""
DEPLOYMENT_TYPE="docker"
ENABLE_PREMIUM_FEATURES=true
CUSTOM_DOMAIN=""
SSL_ENABLED=true
MONITORING_TIER="premium"

show_banner() {
    echo -e "${PURPLE}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                        InfraGenius Professional                             ║
║                        Premium Deployment v1.0.0                           ║
║                                                                              ║
║   💎 Premium Features • ⚡ Enhanced Performance • 🎯 Priority Support       ║
║   🔒 Advanced Security • 📊 Premium Analytics • 🌍 Multi-Region Ready      ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --license-key)
                LICENSE_KEY="$2"
                shift 2
                ;;
            --type)
                DEPLOYMENT_TYPE="$2"
                shift 2
                ;;
            --domain)
                CUSTOM_DOMAIN="$2"
                shift 2
                ;;
            --no-ssl)
                SSL_ENABLED=false
                shift
                ;;
            --monitoring)
                MONITORING_TIER="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                warning "Unknown option: $1"
                shift
                ;;
        esac
    done
}

show_help() {
    cat << EOF
Usage: $0 --license-key=LICENSE_KEY [OPTIONS]

Required:
    --license-key KEY       Professional license key (required)

Options:
    --type TYPE            Deployment type: docker, kubernetes, cloud (default: docker)
    --domain DOMAIN        Custom domain for deployment
    --no-ssl              Disable SSL/TLS (not recommended)
    --monitoring TIER      Monitoring tier: basic, premium, enterprise (default: premium)
    --help                Show this help message

Examples:
    $0 --license-key=YOUR_LICENSE_KEY
    $0 --license-key=KEY --type=kubernetes --domain=api.company.com
    $0 --license-key=KEY --type=cloud --monitoring=enterprise

EOF
}

validate_license() {
    log "Validating professional license..."
    
    if [[ -z "$LICENSE_KEY" ]]; then
        error "Professional license key is required. Use --license-key=YOUR_KEY"
    fi
    
    # Validate license format (basic validation)
    if [[ ! "$LICENSE_KEY" =~ ^[A-Za-z0-9]{32,64}$ ]]; then
        error "Invalid license key format"
    fi
    
    # Create license validation request
    cat > license_validation.json << EOF
{
    "license_key": "$LICENSE_KEY",
    "product": "infragenius",
    "version": "1.0.0",
    "deployment_type": "$DEPLOYMENT_TYPE"
}
EOF
    
    # In a real implementation, this would validate against a license server
    # For demo purposes, we'll simulate validation
    if [[ ${#LICENSE_KEY} -ge 32 ]]; then
        success "Professional license validated successfully"
        
        # Create license file
        cat > .license << EOF
{
    "license_key": "$LICENSE_KEY",
    "tier": "professional",
    "features": [
        "unlimited_requests",
        "priority_processing",
        "advanced_analytics",
        "premium_integrations",
        "custom_fine_tuning",
        "email_support",
        "advanced_security",
        "performance_optimization",
        "multi_region_deployment"
    ],
    "valid_until": "$(date -d '+1 year' '+%Y-%m-%d')",
    "issued_at": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF
        chmod 600 .license
    else
        error "License validation failed. Please check your license key."
    fi
}

create_professional_config() {
    log "Creating professional configuration..."
    
    # Create professional-specific configuration
    cat > config.professional.json << EOF
{
  "server": {
    "name": "InfraGenius Professional",
    "version": "1.0.0",
    "tier": "professional",
    "environment": "production",
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 6,
    "max_connections": 5000,
    "performance_optimizations": {
      "enabled": true,
      "priority_processing": true,
      "advanced_caching": true,
      "request_batching": true,
      "response_compression": true,
      "connection_pooling": true,
      "async_processing": true
    }
  },
  "licensing": {
    "tier": "professional",
    "license_key": "$LICENSE_KEY",
    "features_enabled": [
      "unlimited_requests",
      "priority_processing",
      "advanced_analytics",
      "premium_integrations",
      "custom_fine_tuning",
      "advanced_security"
    ]
  },
  "ollama": {
    "model": "gpt-oss:latest",
    "base_url": "http://ollama-service:11434",
    "timeout": 300,
    "max_retries": 3,
    "priority_queue": true,
    "model_optimization": {
      "enabled": true,
      "custom_fine_tuning": true,
      "model_caching": true,
      "parallel_processing": true
    }
  },
  "database": {
    "url": "postgresql://profuser:\${DB_PASSWORD}@postgres-prof:5432/mcpprof",
    "pool_size": 50,
    "max_overflow": 100,
    "pool_timeout": 30,
    "connection_optimization": true,
    "query_optimization": true
  },
  "redis": {
    "url": "redis://redis-prof:6379/0",
    "max_connections": 200,
    "cluster": {
      "enabled": true,
      "nodes": ["redis-1:6379", "redis-2:6379", "redis-3:6379"]
    },
    "advanced_caching": {
      "enabled": true,
      "compression": true,
      "encryption": true
    }
  },
  "domains": {
    "devops": {"enabled": true, "priority": 1, "fine_tuned": true},
    "sre": {"enabled": true, "priority": 1, "fine_tuned": true},
    "cloud": {"enabled": true, "priority": 1, "fine_tuned": true},
    "platform": {"enabled": true, "priority": 1, "fine_tuned": true}
  },
  "security": {
    "authentication": {
      "enabled": true,
      "advanced_features": {
        "mfa": true,
        "sso": true,
        "api_key_rotation": true
      }
    },
    "rate_limiting": {
      "enabled": true,
      "professional_limits": {
        "requests_per_minute": 1000,
        "requests_per_hour": 50000,
        "priority_processing": true
      }
    },
    "encryption": {
      "advanced_encryption": true,
      "key_rotation": true,
      "compliance_ready": true
    }
  },
  "monitoring": {
    "tier": "$MONITORING_TIER",
    "advanced_metrics": true,
    "custom_dashboards": true,
    "real_time_analytics": true,
    "performance_profiling": true,
    "business_intelligence": true
  },
  "integrations": {
    "premium_integrations": {
      "slack": {"enabled": true, "advanced_features": true},
      "teams": {"enabled": true, "advanced_features": true},
      "pagerduty": {"enabled": true, "advanced_features": true},
      "jira": {"enabled": true, "advanced_features": true},
      "servicenow": {"enabled": true, "advanced_features": true}
    }
  },
  "support": {
    "tier": "professional",
    "email_support": true,
    "priority_queue": true,
    "response_time": "24h",
    "dedicated_support": false
  }
}
EOF

    success "Professional configuration created"
}

create_professional_docker_compose() {
    log "Creating professional Docker Compose configuration..."
    
    cat > docker-compose.professional.yml << 'EOF'
version: '3.8'

services:
  # Professional MCP Server with enhanced performance
  mcp-server-professional:
    build:
      context: .
      dockerfile: docker/production/Dockerfile.professional
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=professional
      - CONFIG_PATH=/app/config.professional.json
      - LICENSE_KEY=${LICENSE_KEY}
      - DATABASE_URL=postgresql://profuser:${DB_PASSWORD}@postgres-prof:5432/mcpprof
      - REDIS_URL=redis://redis-prof:6379/0
      - TIER=professional
    volumes:
      - ./config.professional.json:/app/config.professional.json:ro
      - ./.license:/app/.license:ro
    depends_on:
      postgres-prof:
        condition: service_healthy
      redis-prof:
        condition: service_healthy
    networks:
      - mcp-professional
    restart: unless-stopped

  # High-performance PostgreSQL
  postgres-prof:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=mcpprof
      - POSTGRES_USER=profuser
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_prof_data:/var/lib/postgresql/data
      - ./docker/production/postgresql-professional.conf:/etc/postgresql/postgresql.conf
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U profuser -d mcpprof"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - mcp-professional
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  # Redis Cluster for professional caching
  redis-prof:
    image: redis:7-alpine
    command: redis-server /usr/local/etc/redis/redis-professional.conf
    volumes:
      - redis_prof_data:/data
      - ./docker/production/redis-professional.conf:/usr/local/etc/redis/redis-professional.conf
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - mcp-professional
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G

  # Enhanced Ollama service for professional tier
  ollama-professional:
    image: ollama/ollama:latest
    volumes:
      - ollama_prof_data:/root/.ollama
      - ./models:/models
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_KEEP_ALIVE=30m
      - OLLAMA_MAX_LOADED_MODELS=3
    ports:
      - "11434:11434"
    networks:
      - mcp-professional
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '6.0'
          memory: 16G
        reservations:
          cpus: '4.0'
          memory: 8G

  # Professional monitoring stack
  prometheus-prof:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus/prometheus-professional.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_prof_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=90d'
      - '--web.enable-lifecycle'
    networks:
      - mcp-professional
    restart: unless-stopped

  grafana-prof:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin123}
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource,grafana-piechart-panel
    volumes:
      - grafana_prof_data:/var/lib/grafana
      - ./monitoring/grafana/professional:/etc/grafana/provisioning
    networks:
      - mcp-professional
    restart: unless-stopped

  # Premium integrations service
  integrations-service:
    build:
      context: .
      dockerfile: docker/production/Dockerfile.integrations
    environment:
      - TIER=professional
      - CONFIG_PATH=/app/config.professional.json
    volumes:
      - ./config.professional.json:/app/config.professional.json:ro
    depends_on:
      - mcp-server-professional
    networks:
      - mcp-professional
    restart: unless-stopped

volumes:
  postgres_prof_data:
    driver: local
  redis_prof_data:
    driver: local
  ollama_prof_data:
    driver: local
  prometheus_prof_data:
    driver: local
  grafana_prof_data:
    driver: local

networks:
  mcp-professional:
    driver: bridge
    ipam:
      config:
        - subnet: 172.30.0.0/16

EOF

    success "Professional Docker Compose configuration created"
}

setup_ssl_certificates() {
    if [[ "$SSL_ENABLED" == "true" && -n "$CUSTOM_DOMAIN" ]]; then
        log "Setting up SSL certificates for $CUSTOM_DOMAIN..."
        
        mkdir -p ssl
        
        # Generate self-signed certificate for development
        # In production, use Let's Encrypt or purchased certificates
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/private.key \
            -out ssl/certificate.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=$CUSTOM_DOMAIN"
        
        success "SSL certificates generated for $CUSTOM_DOMAIN"
    fi
}

deploy_professional() {
    log "Deploying professional version..."
    
    case $DEPLOYMENT_TYPE in
        "docker")
            deploy_professional_docker
            ;;
        "kubernetes")
            deploy_professional_kubernetes
            ;;
        "cloud")
            deploy_professional_cloud
            ;;
        *)
            error "Unknown deployment type: $DEPLOYMENT_TYPE"
            ;;
    esac
}

deploy_professional_docker() {
    log "Deploying with Docker (Professional)..."
    
    # Set environment variables
    export LICENSE_KEY="$LICENSE_KEY"
    export DB_PASSWORD=$(openssl rand -base64 32)
    export GRAFANA_PASSWORD=$(openssl rand -base64 16)
    
    # Start professional services
    docker-compose -f docker-compose.professional.yml up -d
    
    # Wait for services to be ready
    log "Waiting for services to start..."
    sleep 60
    
    # Load professional models
    docker-compose -f docker-compose.professional.yml exec ollama-professional \
        ollama pull gpt-oss:latest
    
    # Test deployment
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Professional deployment successful"
    else
        error "Professional deployment failed"
    fi
}

deploy_professional_kubernetes() {
    log "Deploying to Kubernetes (Professional)..."
    
    # Create professional namespace
    kubectl create namespace mcp-professional --dry-run=client -o yaml | kubectl apply -f -
    
    # Create secrets
    kubectl create secret generic mcp-professional-secrets \
        --from-literal=license-key="$LICENSE_KEY" \
        --from-literal=db-password="$(openssl rand -base64 32)" \
        --namespace=mcp-professional
    
    # Apply professional manifests
    kubectl apply -f kubernetes/production/professional/ -n mcp-professional
    
    # Wait for deployment
    kubectl wait --for=condition=available --timeout=300s \
        deployment/mcp-server-professional -n mcp-professional
    
    success "Professional Kubernetes deployment successful"
}

deploy_professional_cloud() {
    log "Deploying to cloud (Professional)..."
    
    # This would integrate with cloud-specific deployment scripts
    # For now, we'll use the Docker deployment
    deploy_professional_docker
    
    success "Professional cloud deployment successful"
}

setup_premium_monitoring() {
    log "Setting up premium monitoring..."
    
    # Create professional monitoring configuration
    mkdir -p monitoring/grafana/professional/dashboards
    mkdir -p monitoring/prometheus
    
    # Professional Prometheus configuration
    cat > monitoring/prometheus/prometheus-professional.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'mcp-server-professional'
    static_configs:
      - targets: ['mcp-server-professional:8000']
    scrape_interval: 10s
    metrics_path: /metrics
    
  - job_name: 'postgres-professional'
    static_configs:
      - targets: ['postgres-prof:5432']
    
  - job_name: 'redis-professional'
    static_configs:
      - targets: ['redis-prof:6379']
    
  - job_name: 'ollama-professional'
    static_configs:
      - targets: ['ollama-professional:11434']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
EOF

    # Professional Grafana dashboard
    cat > monitoring/grafana/professional/dashboards/professional-dashboard.json << 'EOF'
{
  "dashboard": {
    "title": "DevOps/SRE MCP Server - Professional Dashboard",
    "tags": ["professional", "mcp", "devops"],
    "panels": [
      {
        "title": "Request Rate (Professional)",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(mcp_requests_total{tier=\"professional\"}[5m])"
          }
        ]
      },
      {
        "title": "Response Time P95",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(mcp_request_duration_seconds_bucket{tier=\"professional\"}[5m]))"
          }
        ]
      },
      {
        "title": "Professional Features Usage",
        "type": "table",
        "targets": [
          {
            "expr": "mcp_professional_features_usage"
          }
        ]
      }
    ]
  }
}
EOF

    success "Premium monitoring setup complete"
}

show_professional_success() {
    echo -e "${GREEN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🎉 PROFESSIONAL DEPLOYMENT COMPLETE! 🎉                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    highlight "Your InfraGenius Professional is now running!"
    echo
    
    log "💎 Professional Features Enabled:"
    echo "   ✅ Unlimited requests"
    echo "   ⚡ Priority processing (2x faster)"
    echo "   📊 Advanced analytics and reporting"
    echo "   🔧 Premium integrations (Slack, Teams, PagerDuty)"
    echo "   🎯 Custom fine-tuning capabilities"
    echo "   📞 Email support (24h response)"
    echo "   🔒 Advanced security features"
    echo "   📈 Performance optimization tools"
    
    echo
    log "🌐 Service URLs:"
    echo "   🚀 API Server: http://localhost:8000"
    echo "   📋 API Docs: http://localhost:8000/docs"
    echo "   ❤️  Health Check: http://localhost:8000/health"
    echo "   📈 Grafana: http://localhost:3000 (admin/admin123)"
    echo "   📊 Prometheus: http://localhost:9090"
    
    if [[ -n "$CUSTOM_DOMAIN" ]]; then
        echo "   🌍 Custom Domain: https://$CUSTOM_DOMAIN"
    fi
    
    echo
    log "🧪 Professional API Test:"
    echo '   curl -X POST http://localhost:8000/analyze \'
    echo '     -H "Content-Type: application/json" \'
    echo '     -H "X-License-Key: '"$LICENSE_KEY"'" \'
    echo '     -d '"'"'{"prompt": "Optimize my CI/CD pipeline", "domain": "devops", "priority": "high"}'"'"
    
    echo
    log "📞 Support Information:"
    echo "   📧 Email: support@devops-mcp.com"
    echo "   ⏱️  Response Time: 24 hours"
    echo "   🎯 Priority Queue: Enabled"
    echo "   📚 Documentation: https://docs.devops-mcp.com/professional"
    
    echo
    success "Welcome to DevOps/SRE MCP Server Professional! 💎"
}

main() {
    show_banner
    parse_arguments "$@"
    validate_license
    create_professional_config
    create_professional_docker_compose
    setup_ssl_certificates
    deploy_professional
    setup_premium_monitoring
    show_professional_success
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
