# BigShot Deployment Guide

This guide covers the deployment, configuration, and maintenance of the BigShot domain reconnaissance platform.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Development Environment](#development-environment)
5. [Production Deployment](#production-deployment)
6. [Configuration Management](#configuration-management)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Backup and Recovery](#backup-and-recovery)
9. [Maintenance Procedures](#maintenance-procedures)
10. [Troubleshooting](#troubleshooting)
11. [Security Considerations](#security-considerations)

## Overview

BigShot is a full-stack domain reconnaissance platform consisting of:
- **Backend**: Flask API with PostgreSQL database, Redis cache, and Celery workers
- **Frontend**: React application with TypeScript and Tailwind CSS
- **Infrastructure**: Docker containers with comprehensive monitoring and backup systems

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- **Memory**: Minimum 4GB RAM (8GB+ recommended for production)
- **Storage**: Minimum 20GB free space
- **Network**: Internet connection for external API integrations

### Required Software

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: For repository cloning
- **Node.js**: Version 16+ (for local development)
- **Python**: Version 3.9+ (for local development)

### Installation

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply docker group membership
```

#### macOS
```bash
# Install Docker Desktop for Mac
# Download from https://www.docker.com/products/docker-desktop/

# Or using Homebrew
brew install docker docker-compose
```

## Quick Start

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/thesavant42/bigshot.git
cd bigshot

# Setup environment
./scripts/setup_dev.sh
```

### Start Development Environment

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Access Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **Database**: localhost:5433 (PostgreSQL)
- **Redis**: localhost:6380

### Stop Development Environment

```bash
./scripts/stop_dev.sh
```

## Development Environment

### Setup Scripts

The development environment includes several automated setup scripts:

#### `scripts/setup_dev.sh`
- Checks system requirements
- Creates necessary directories
- Sets up environment configuration
- Installs dependencies (optional)
- Starts development services

#### `scripts/stop_dev.sh`
- Stops all development services
- Provides cleanup options
- Removes containers and volumes (optional)

### Development Workflow

```bash
# Start development environment
./scripts/setup_dev.sh

# Make code changes
# Backend changes: Files are mounted, restart backend container
# Frontend changes: Hot reload is enabled automatically

# Run tests
docker-compose -f docker-compose.dev.yml exec backend python -m pytest tests/
cd frontend && npm test

# Stop environment
./scripts/stop_dev.sh
```

### Local Development (Without Docker)

```bash
# Backend
pip install -r requirements.txt
export FLASK_ENV=development
python run.py

# Frontend
cd frontend
npm install
npm run dev
```

## Production Deployment

### Environment Configuration

1. **Copy Environment Template**
   ```bash
   cp .env.example .env
   ```

2. **Edit Configuration**
   ```bash
   # Required variables
   POSTGRES_PASSWORD=your_secure_password
   JWT_SECRET_KEY=your_jwt_secret_key
   OPENAI_API_KEY=your_openai_api_key
   
   # Optional variables
   GRAFANA_PASSWORD=your_grafana_password
   ```

### Deployment Options

#### Option 1: Quick Production Deployment

```bash
# Deploy with default settings
./scripts/deploy_prod.sh
```

#### Option 2: Custom Production Deployment

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Monitor deployment
docker-compose -f docker-compose.prod.yml logs -f
```

#### Option 3: Deploy with Backup

```bash
# Create backup before deployment
./scripts/deploy_prod.sh
# Select option 3: "Backup and deploy"
```

### Production Services

After deployment, the following services will be available:

- **Frontend**: http://localhost (port 80)
- **Backend API**: http://localhost:5000
- **Database**: localhost:5432
- **Redis**: localhost:6379
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

### SSL/TLS Configuration

For production deployments with SSL:

1. **Obtain SSL Certificates**
   ```bash
   # Using Let's Encrypt (example)
   sudo apt install certbot
   sudo certbot certonly --standalone -d your-domain.com
   ```

2. **Configure SSL in Docker Compose**
   ```yaml
   # In docker-compose.prod.yml
   frontend:
     volumes:
       - /etc/letsencrypt/live/your-domain.com:/etc/ssl/certs
     ports:
       - "443:443"
   ```

3. **Update Nginx Configuration**
   ```nginx
   # Add SSL configuration to frontend/nginx.conf
   server {
       listen 443 ssl;
       ssl_certificate /etc/ssl/certs/fullchain.pem;
       ssl_certificate_key /etc/ssl/certs/privkey.pem;
       # ... rest of configuration
   }
   ```

### Scaling Production Deployment

#### Horizontal Scaling

```yaml
# Scale specific services
docker-compose -f docker-compose.prod.yml up -d --scale celery=3
docker-compose -f docker-compose.prod.yml up -d --scale backend=2
```

#### Resource Limits

The production configuration includes resource limits:
- **Database**: 1GB memory limit, 512MB reservation
- **Redis**: 512MB memory limit, 256MB reservation
- **Backend**: 1GB memory limit, 512MB reservation
- **Frontend**: 512MB memory limit, 256MB reservation

Adjust these in `docker-compose.prod.yml` based on your requirements.

## Configuration Management

### Environment Variables

#### Database Configuration
```bash
POSTGRES_DB=bigshot
POSTGRES_USER=bigshot
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql://user:pass@host:port/db
```

#### Redis Configuration
```bash
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### Application Configuration
```bash
FLASK_ENV=production
JWT_SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_key
```

### Runtime Configuration

The application includes a web-based configuration management interface:

1. **Access Configuration Panel**
   - Navigate to the Settings tab in the application
   - Requires authentication

2. **Configuration Sections**
   - **General Settings**: Basic application configuration
   - **Security Settings**: Authentication and security options
   - **Database Settings**: Database connection parameters
   - **Redis Settings**: Cache and message broker configuration
   - **External Integrations**: Third-party service settings

3. **Export/Import Configuration**
   ```bash
   # Export current configuration
   curl -H "Authorization: Bearer $TOKEN" \
        http://localhost:5000/api/v1/config/export > config.json
   
   # Import configuration
   curl -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d @config.json \
        http://localhost:5000/api/v1/config/import
   ```

## Monitoring and Logging

### Built-in Monitoring

The application includes comprehensive monitoring capabilities:

#### System Metrics
- **CPU Usage**: Real-time CPU utilization
- **Memory Usage**: Memory consumption and availability
- **Disk Usage**: Storage utilization
- **Network**: Connection statistics

#### Application Metrics
- **Database**: Connection pool, query performance
- **Redis**: Memory usage, connection count
- **Celery**: Active workers, job queue status
- **WebSocket**: Connected clients

#### Health Checks

```bash
# Basic health check
curl http://localhost:5000/api/v1/health

# Detailed health check (requires authentication)
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/v1/health/detailed

# Metrics endpoint
curl http://localhost:5000/api/v1/metrics
```

### Prometheus and Grafana

Production deployments include Prometheus for metrics collection and Grafana for visualization:

#### Accessing Grafana
1. Navigate to http://localhost:3000
2. Login with admin credentials (set via `GRAFANA_PASSWORD`)
3. Default dashboards are automatically configured

#### Custom Dashboards
```bash
# Add custom dashboard configurations
mkdir -p monitoring/grafana/dashboards
# Place JSON dashboard files here
```

### Log Management

#### Log Locations
- **Application Logs**: `logs/app.log`
- **Nginx Logs**: `logs/nginx/access.log`, `logs/nginx/error.log`
- **Database Logs**: Available via `docker logs`

#### Log Rotation
```bash
# Setup log rotation
sudo nano /etc/logrotate.d/bigshot

# Add configuration
/path/to/bigshot/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 www-data www-data
}
```

#### Centralized Logging
For production environments, consider integrating with:
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Fluentd**: Log collection and forwarding
- **Syslog**: System logging infrastructure

## Backup and Recovery

### Automated Backup

The backup system includes comprehensive data protection:

#### Create Backup
```bash
# Development environment
./scripts/backup.sh --dev

# Production environment
./scripts/backup.sh --prod

# Custom backup name
./scripts/backup.sh --prod --name "pre-update-backup"
```

#### Backup Components
- **Database**: PostgreSQL dump with schema and data
- **Redis**: RDB snapshot
- **Application Files**: Instance directory and logs
- **Configuration**: Environment settings
- **Metadata**: Backup manifest with timestamps

### Restore Procedures

#### Restore from Backup
```bash
# List available backups
./scripts/restore_backup.sh --list

# Restore specific backup
./scripts/restore_backup.sh --prod --file backup_name.tar.gz

# Force restore without confirmation
./scripts/restore_backup.sh --prod --file backup_name.tar.gz --force
```

#### Manual Recovery

```bash
# Database recovery
docker-compose -f docker-compose.prod.yml exec database psql -U bigshot -d bigshot < backup.sql

# Redis recovery
docker-compose -f docker-compose.prod.yml stop redis
docker cp backup.rdb container_name:/data/dump.rdb
docker-compose -f docker-compose.prod.yml start redis
```

### Backup Scheduling

#### Cron Job Setup
```bash
# Edit crontab
crontab -e

# Add backup schedule (daily at 2 AM)
0 2 * * * /path/to/bigshot/scripts/backup.sh --prod

# Weekly full backup (Sundays at 3 AM)
0 3 * * 0 /path/to/bigshot/scripts/backup.sh --prod --name "weekly-$(date +%Y%m%d)"
```

#### Backup Monitoring
```bash
# Check backup status via API
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/v1/backup/status
```

### Disaster Recovery

#### Full System Recovery
1. **Prepare New Environment**
   ```bash
   git clone https://github.com/thesavant42/bigshot.git
   cd bigshot
   cp .env.example .env
   # Edit .env with appropriate values
   ```

2. **Restore from Backup**
   ```bash
   # Copy backup files to new environment
   ./scripts/restore_backup.sh --prod --file latest_backup.tar.gz
   ```

3. **Verify Recovery**
   ```bash
   # Check system health
   curl http://localhost:5000/api/v1/health/detailed
   
   # Test functionality
   # Login to application and verify data integrity
   ```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily Tasks
- Monitor system health via dashboard
- Check application logs for errors
- Verify backup completion
- Monitor disk space usage

#### Weekly Tasks
- Update Docker images
- Review security logs
- Optimize database (if needed)
- Check SSL certificate expiration

#### Monthly Tasks
- Update system packages
- Review and rotate logs
- Security audit
- Performance optimization

### System Updates

#### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

#### Update Dependencies
```bash
# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update Node.js dependencies
cd frontend && npm update
```

#### Database Maintenance
```bash
# Database optimization
docker-compose -f docker-compose.prod.yml exec database psql -U bigshot -d bigshot -c "VACUUM ANALYZE;"

# Check database statistics
docker-compose -f docker-compose.prod.yml exec database psql -U bigshot -d bigshot -c "SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del FROM pg_stat_user_tables;"
```

### Security Updates

#### System Security
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker
sudo apt update && sudo apt install docker-ce docker-ce-cli containerd.io

# Check for security vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/src \
  aquasecurity/trivy image bigshot_backend:latest
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service logs
docker-compose -f docker-compose.prod.yml logs service_name

# Check service status
docker-compose -f docker-compose.prod.yml ps

# Restart specific service
docker-compose -f docker-compose.prod.yml restart service_name
```

#### Database Connection Issues
```bash
# Check database connectivity
docker-compose -f docker-compose.prod.yml exec database pg_isready -U bigshot

# Check database logs
docker-compose -f docker-compose.prod.yml logs database

# Reset database connection
docker-compose -f docker-compose.prod.yml restart database backend
```

#### Redis Connection Issues
```bash
# Check Redis connectivity
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Check Redis logs
docker-compose -f docker-compose.prod.yml logs redis

# Clear Redis cache
docker-compose -f docker-compose.prod.yml exec redis redis-cli flushall
```

#### Performance Issues
```bash
# Check system resources
docker stats

# Monitor application metrics
curl http://localhost:5000/api/v1/metrics

# Check database performance
docker-compose -f docker-compose.prod.yml exec database psql -U bigshot -d bigshot -c "SELECT * FROM pg_stat_activity;"
```

### Debugging Tools

#### Application Debug Mode
```bash
# Enable debug mode
docker-compose -f docker-compose.dev.yml up -d

# Check debug logs
docker-compose -f docker-compose.dev.yml logs -f backend
```

#### Database Debugging
```bash
# Connect to database
docker-compose -f docker-compose.prod.yml exec database psql -U bigshot -d bigshot

# Check database queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

#### Network Debugging
```bash
# Check network connectivity
docker network ls
docker network inspect bigshot_prod_network

# Test internal connectivity
docker-compose -f docker-compose.prod.yml exec backend ping database
```

## Security Considerations

### Authentication and Authorization
- JWT tokens with configurable expiration
- Rate limiting on API endpoints
- Secure password hashing
- CORS configuration

### Data Security
- Database encryption at rest
- Sensitive data masking in logs
- SSL/TLS for all communications
- Regular security updates

### Network Security
- Isolated Docker networks
- Firewall configuration
- VPN access for administration
- Regular security audits

### Best Practices
- Change default passwords
- Use environment variables for secrets
- Enable audit logging
- Regular backup testing
- Security monitoring

For additional support, please refer to the project documentation or contact the development team.