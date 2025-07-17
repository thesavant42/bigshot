#!/bin/bash
"""
Production deployment script for BigShot
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Requirements check completed."
}

# Validate environment configuration
validate_environment() {
    print_status "Validating environment configuration..."
    
    if [ ! -f .env ]; then
        print_error "Environment file (.env) not found. Please create it from .env.example"
        exit 1
    fi
    
    # Check required environment variables
    source .env
    
    required_vars=("POSTGRES_PASSWORD" "JWT_SECRET_KEY")
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "Required environment variable $var is not set in .env file"
            exit 1
        fi
    done
    
    print_status "Environment validation completed."
}

# Create necessary directories and files
setup_production_environment() {
    print_status "Setting up production environment..."
    
    # Create directories
    mkdir -p logs/nginx
    mkdir -p instance
    mkdir -p backups
    mkdir -p ssl
    mkdir -p monitoring
    
    # Create monitoring configuration
    create_monitoring_config
    
    print_status "Production environment setup completed."
}

# Create monitoring configuration
create_monitoring_config() {
    print_status "Creating monitoring configuration..."
    
    # Prometheus configuration
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'bigshot-backend'
    static_configs:
      - targets: ['backend:5000']
    metrics_path: '/api/v1/metrics'
    scrape_interval: 30s

  - job_name: 'bigshot-frontend'
    static_configs:
      - targets: ['frontend:80']
    metrics_path: '/health'
    scrape_interval: 60s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['database:5432']
    scrape_interval: 30s
EOF

    # Grafana datasource configuration
    mkdir -p monitoring/grafana/datasources
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    print_status "Monitoring configuration created."
}

# Build and deploy
deploy_production() {
    print_status "Building and deploying production environment..."
    
    # Build images
    print_status "Building Docker images..."
    docker-compose -f docker-compose.prod.yml build
    
    # Start services
    print_status "Starting production services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Show service status
    docker-compose -f docker-compose.prod.yml ps
    
    print_status "Production deployment completed!"
    print_status "Services:"
    print_status "  - Frontend: http://localhost"
    print_status "  - Backend API: http://localhost:5000"
    print_status "  - Database: localhost:5432"
    print_status "  - Redis: localhost:6379"
    print_status "  - Prometheus: http://localhost:9090"
    print_status "  - Grafana: http://localhost:3000"
    print_status ""
    print_status "To stop: docker-compose -f docker-compose.prod.yml down"
    print_status "To view logs: docker-compose -f docker-compose.prod.yml logs -f"
}

# Update deployment
update_deployment() {
    print_status "Updating production deployment..."
    
    # Pull latest images
    docker-compose -f docker-compose.prod.yml pull
    
    # Rebuild custom images
    docker-compose -f docker-compose.prod.yml build
    
    # Restart services
    docker-compose -f docker-compose.prod.yml up -d
    
    print_status "Deployment update completed!"
}

# Backup before deployment
backup_before_deployment() {
    print_status "Creating backup before deployment..."
    
    # Create backup directory with timestamp
    backup_dir="backups/pre-deployment-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup database
    docker-compose -f docker-compose.prod.yml exec -T database pg_dump -U bigshot bigshot > "$backup_dir/database_backup.sql"
    
    # Backup Redis data
    docker-compose -f docker-compose.prod.yml exec -T redis redis-cli BGSAVE
    docker cp $(docker-compose -f docker-compose.prod.yml ps -q redis):/data/dump.rdb "$backup_dir/redis_backup.rdb"
    
    print_status "Backup created in $backup_dir"
}

# Main deployment function
main() {
    print_status "Starting BigShot production deployment..."
    
    check_requirements
    validate_environment
    setup_production_environment
    
    # Ask user what they want to do
    echo ""
    echo "What would you like to do?"
    echo "1) Full deployment (new installation)"
    echo "2) Update existing deployment"
    echo "3) Backup and deploy"
    echo ""
    read -p "Enter your choice [1-3]: " choice
    
    case $choice in
        1)
            deploy_production
            ;;
        2)
            update_deployment
            ;;
        3)
            backup_before_deployment
            deploy_production
            ;;
        *)
            print_error "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
    
    print_status "Production deployment completed successfully!"
}

# Run main function
main "$@"