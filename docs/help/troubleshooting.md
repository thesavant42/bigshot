# BigShot Troubleshooting Guide

This guide provides solutions for common issues encountered when deploying and running BigShot.

## Table of Contents

1. [General Troubleshooting](#general-troubleshooting)
2. [Installation Issues](#installation-issues)
3. [Service Startup Problems](#service-startup-problems)
4. [Database Issues](#database-issues)
5. [Redis Issues](#redis-issues)
6. [Network and Connectivity](#network-and-connectivity)
7. [Performance Issues](#performance-issues)
8. [Frontend Issues](#frontend-issues)
9. [Authentication Problems](#authentication-problems)
10. [Backup and Recovery Issues](#backup-and-recovery-issues)
11. [Monitoring and Logging](#monitoring-and-logging)
12. [Docker and Container Issues](#docker-and-container-issues)

## General Troubleshooting

### Before You Start

1. **Check System Requirements**
   - Ensure you have Docker 20.10+ and Docker Compose 2.0+
   - Verify you have sufficient disk space (20GB minimum)
   - Check RAM availability (4GB minimum, 8GB recommended)

2. **Verify Environment**
   ```bash
   # Check Docker version
   docker --version
   docker-compose --version
   
   # Check Docker daemon
   sudo systemctl status docker
   
   # Check disk space
   df -h
   
   # Check memory
   free -h
   ```

3. **Review Logs First**
   ```bash
   # Check all service logs
   docker-compose logs
   
   # Check specific service
   docker-compose logs backend
   
   # Follow logs in real-time
   docker-compose logs -f
   ```

### Basic Diagnostic Commands

```bash
# Check service status
docker-compose ps

# Check system resources
docker stats

# Check network connectivity
docker network ls
docker network inspect bigshot_network

# Check volumes
docker volume ls
docker volume inspect bigshot_postgres_data
```

## Installation Issues

### Docker Installation Problems

#### Permission Denied
```bash
# Error: permission denied while trying to connect to Docker daemon
sudo usermod -aG docker $USER
# Logout and login again
```

#### Docker Service Not Running
```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

#### Docker Compose Not Found
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Repository Clone Issues

#### Permission Denied (publickey)
```bash
# Use HTTPS instead of SSH
git clone https://github.com/thesavant42/bigshot.git

# Or setup SSH keys
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
cat ~/.ssh/id_rsa.pub
# Add to GitHub SSH keys
```

#### Git Not Installed
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install git

# macOS
brew install git

# Or download from https://git-scm.com/
```

## Service Startup Problems

### Container Fails to Start

#### Check Container Status
```bash
# List all containers
docker ps -a

# Check specific container
docker inspect container_name

# Check container logs
docker logs container_name
```

#### Port Already in Use
```bash
# Error: port is already allocated
# Find process using port
sudo lsof -i :5000
sudo netstat -tulpn | grep :5000

# Kill process
sudo kill -9 PID

# Or use different port in docker-compose.yml
```

#### Environment File Missing
```bash
# Create .env file
cp .env.example .env

# Edit with appropriate values
nano .env
```

### Database Container Issues

#### Database Won't Start
```bash
# Check database logs
docker-compose logs database

# Common issues:
# 1. Data directory permissions
sudo chown -R 999:999 postgres_data/

# 2. Port conflict
# Change port in docker-compose.yml

# 3. Invalid configuration
# Check postgresql.conf settings
```

#### Database Connection Refused
```bash
# Check if database is running
docker-compose exec database pg_isready -U bigshot

# Check database logs
docker-compose logs database

# Wait for database to initialize
# First startup can take 30-60 seconds
```

### Redis Container Issues

#### Redis Won't Start
```bash
# Check Redis logs
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis configuration
docker-compose exec redis redis-cli CONFIG GET "*"
```

#### Redis Memory Issues
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli INFO memory

# Increase memory limit in docker-compose.yml
# Or enable Redis memory optimization
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Backend Container Issues

#### Flask App Won't Start
```bash
# Check backend logs
docker-compose logs backend

# Common issues:
# 1. Python import errors
# 2. Database connection issues
# 3. Missing environment variables
# 4. Port conflicts

# Restart backend service
docker-compose restart backend
```

#### Celery Worker Issues
```bash
# Check Celery logs
docker-compose logs celery

# Test Celery connectivity
docker-compose exec backend python -c "from celery_app import celery_app; print(celery_app.control.inspect().active())"

# Restart Celery worker
docker-compose restart celery
```

## Database Issues

### Connection Problems

#### Database Connection Timeout
```bash
# Check database container
docker-compose ps database

# Check database logs
docker-compose logs database

# Test connection
docker-compose exec database psql -U bigshot -d bigshot -c "SELECT 1;"

# Check connection pool
docker-compose exec backend python -c "from app import db; print(db.engine.pool.status())"
```

#### Authentication Failed
```bash
# Check database credentials
docker-compose exec database psql -U bigshot -d bigshot

# Reset database password
docker-compose exec database psql -U postgres -c "ALTER USER bigshot PASSWORD 'new_password';"

# Update .env file with new password
```

### Database Performance Issues

#### Slow Queries
```bash
# Enable query logging
docker-compose exec database psql -U bigshot -d bigshot -c "ALTER DATABASE bigshot SET log_statement = 'all';"

# Check slow queries
docker-compose exec database psql -U bigshot -d bigshot -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Analyze query performance
docker-compose exec database psql -U bigshot -d bigshot -c "EXPLAIN ANALYZE SELECT * FROM domains;"
```

#### Database Locks
```bash
# Check for locks
docker-compose exec database psql -U bigshot -d bigshot -c "SELECT * FROM pg_locks WHERE NOT granted;"

# Kill blocking queries
docker-compose exec database psql -U bigshot -d bigshot -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';"
```

### Data Corruption

#### Database Corruption
```bash
# Check database integrity
docker-compose exec database psql -U bigshot -d bigshot -c "SELECT * FROM pg_stat_database;"

# Reindex database
docker-compose exec database psql -U bigshot -d bigshot -c "REINDEX DATABASE bigshot;"

# Restore from backup
./scripts/restore_backup.sh --prod --file latest_backup.tar.gz
```

## Redis Issues

### Connection Problems

#### Redis Connection Refused
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Test connectivity from backend
docker-compose exec backend python -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"
```

#### Redis Authentication Issues
```bash
# Check Redis configuration
docker-compose exec redis redis-cli CONFIG GET requirepass

# Test authentication
docker-compose exec redis redis-cli -a password ping

# Update Redis password
docker-compose exec redis redis-cli CONFIG SET requirepass "new_password"
```

### Redis Performance Issues

#### High Memory Usage
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli INFO memory

# Check key distribution
docker-compose exec redis redis-cli --bigkeys

# Clear cache if needed
docker-compose exec redis redis-cli FLUSHALL
```

#### Redis Slow Response
```bash
# Check Redis slow log
docker-compose exec redis redis-cli SLOWLOG GET 10

# Monitor Redis operations
docker-compose exec redis redis-cli MONITOR

# Check Redis configuration
docker-compose exec redis redis-cli CONFIG GET "*"
```

## Network and Connectivity

### Container Communication Issues

#### Service Discovery Problems
```bash
# Check Docker network
docker network ls
docker network inspect bigshot_network

# Test connectivity between containers
docker-compose exec backend ping database
docker-compose exec backend ping redis

# Check DNS resolution
docker-compose exec backend nslookup database
```

#### Port Binding Issues
```bash
# Check port usage
sudo netstat -tulpn | grep :5000

# Check Docker port mapping
docker port container_name

# Update port mapping in docker-compose.yml
```

### External API Issues

#### OpenAI API Connection
```bash
# Check OpenAI API key
docker-compose exec backend python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# Test OpenAI connection
docker-compose exec backend python -c "
import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
try:
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=5
    )
    print('OpenAI connection successful')
except Exception as e:
    print(f'OpenAI connection failed: {e}')
"
```

#### External DNS Issues
```bash
# Test DNS resolution
docker-compose exec backend nslookup google.com

# Check DNS configuration
docker-compose exec backend cat /etc/resolv.conf

# Update DNS settings in docker-compose.yml
```

## Performance Issues

### Slow Response Times

#### Database Performance
```bash
# Check database connections
docker-compose exec database psql -U bigshot -d bigshot -c "SELECT count(*) FROM pg_stat_activity;"

# Check query performance
docker-compose exec database psql -U bigshot -d bigshot -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Optimize database
docker-compose exec database psql -U bigshot -d bigshot -c "VACUUM ANALYZE;"
```

#### Redis Performance
```bash
# Check Redis performance
docker-compose exec redis redis-cli --latency

# Monitor Redis operations
docker-compose exec redis redis-cli MONITOR

# Check Redis configuration
docker-compose exec redis redis-cli CONFIG GET "*"
```

#### System Resources
```bash
# Check system resources
docker stats

# Monitor system performance
top
iostat -x 1
```

### Memory Issues

#### Out of Memory
```bash
# Check memory usage
docker stats
free -h

# Check swap usage
swapon -s

# Increase memory limits in docker-compose.yml
# Add swap file if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Memory Leaks
```bash
# Monitor memory usage over time
docker stats --no-stream

# Check for memory leaks in application
docker-compose exec backend python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"

# Restart services to clear memory
docker-compose restart
```

## Frontend Issues

### Build Problems

#### Frontend Build Fails
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend

# Check Node.js version
docker-compose exec frontend node --version

# Clear npm cache
docker-compose exec frontend npm cache clean --force
```

#### TypeScript Errors
```bash
# Check TypeScript compilation
cd frontend
npm run build

# Check TypeScript configuration
cat tsconfig.json

# Update TypeScript dependencies
npm update typescript
```

### Runtime Issues

#### Frontend Not Loading
```bash
# Check frontend service
docker-compose ps frontend

# Check nginx logs
docker-compose logs frontend

# Test frontend connectivity
curl http://localhost/

# Check nginx configuration
docker-compose exec frontend nginx -t
```

#### API Connection Issues
```bash
# Check API connectivity from frontend
curl http://localhost/api/v1/health

# Check nginx proxy configuration
docker-compose exec frontend cat /etc/nginx/nginx.conf

# Test backend connectivity
docker-compose exec frontend wget -q -O - http://backend:5000/api/v1/health
```

## Authentication Problems

### JWT Issues

#### Invalid Token
```bash
# Check JWT secret key
docker-compose exec backend python -c "import os; print(os.getenv('JWT_SECRET_KEY'))"

# Test token generation
docker-compose exec backend python -c "
from flask_jwt_extended import create_access_token
from app import create_app
app = create_app()
with app.app_context():
    token = create_access_token(identity='test')
    print(f'Token: {token}')
"
```

#### Token Expiration
```bash
# Check token expiration settings
docker-compose exec backend python -c "
from app import create_app
app = create_app()
print(f'JWT expires: {app.config.get(\"JWT_ACCESS_TOKEN_EXPIRES\")}')
"

# Update token expiration in configuration
```

### Login Issues

#### Authentication Failed
```bash
# Check user credentials
docker-compose exec database psql -U bigshot -d bigshot -c "SELECT * FROM users;"

# Reset user password
docker-compose exec backend python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        user.set_password('new_password')
        db.session.commit()
        print('Password updated')
"
```

## Backup and Recovery Issues

### Backup Problems

#### Backup Script Fails
```bash
# Check backup script permissions
chmod +x scripts/backup.sh

# Run backup with verbose output
./scripts/backup.sh --prod 2>&1 | tee backup.log

# Check backup directory
ls -la backups/

# Check disk space
df -h
```

#### Database Backup Fails
```bash
# Test database connectivity
docker-compose exec database pg_isready -U bigshot

# Manual database backup
docker-compose exec database pg_dump -U bigshot bigshot > manual_backup.sql

# Check database permissions
docker-compose exec database psql -U bigshot -d bigshot -c "SELECT current_user;"
```

### Recovery Issues

#### Restore Script Fails
```bash
# Check restore script permissions
chmod +x scripts/restore_backup.sh

# List available backups
./scripts/restore_backup.sh --list

# Test backup file integrity
tar -tzf backups/backup_file.tar.gz

# Manual restore
tar -xzf backups/backup_file.tar.gz
docker-compose exec database psql -U bigshot -d bigshot < backup_dir/database_backup.sql
```

## Monitoring and Logging

### Monitoring Issues

#### Prometheus Not Collecting Metrics
```bash
# Check Prometheus configuration
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml

# Test metrics endpoint
curl http://localhost:5000/api/v1/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

#### Grafana Not Working
```bash
# Check Grafana logs
docker-compose logs grafana

# Check Grafana configuration
docker-compose exec grafana cat /etc/grafana/grafana.ini

# Reset Grafana admin password
docker-compose exec grafana grafana-cli admin reset-admin-password newpassword
```

### Logging Issues

#### Logs Not Appearing
```bash
# Check log directory permissions
ls -la logs/

# Check log rotation
sudo logrotate -d /etc/logrotate.d/bigshot

# Check application logging configuration
docker-compose exec backend python -c "
import logging
logger = logging.getLogger()
print(f'Log level: {logger.level}')
print(f'Handlers: {logger.handlers}')
"
```

#### Log Files Too Large
```bash
# Check log file sizes
du -h logs/

# Setup log rotation
sudo nano /etc/logrotate.d/bigshot

# Manual log rotation
sudo logrotate -f /etc/logrotate.d/bigshot
```

## Docker and Container Issues

### Container Management

#### Container Keeps Restarting
```bash
# Check container logs
docker logs container_name

# Check container exit code
docker ps -a

# Disable restart policy temporarily
docker update --restart=no container_name

# Check container resources
docker stats container_name
```

#### Container Out of Disk Space
```bash
# Check Docker disk usage
docker system df

# Clean up unused containers
docker container prune

# Clean up unused images
docker image prune -a

# Clean up unused volumes
docker volume prune

# Clean up everything
docker system prune -a
```

### Image Issues

#### Image Build Fails
```bash
# Check Dockerfile syntax
docker build --no-cache -t test .

# Build with verbose output
docker build --progress=plain -t test .

# Check base image
docker pull python:3.12-slim

# Clear build cache
docker builder prune -a
```

#### Image Too Large
```bash
# Check image size
docker images

# Analyze image layers
docker history image_name

# Use multi-stage builds
# Update Dockerfile with optimizations
```

## Getting Help

### Diagnostic Information

When reporting issues, please provide:

```bash
# System information
uname -a
docker --version
docker-compose --version

# Service status
docker-compose ps

# Recent logs
docker-compose logs --tail=50

# System resources
docker stats --no-stream
df -h
free -h

# Network information
docker network ls
docker network inspect bigshot_network
```

### Support Resources

- **GitHub Issues**: https://github.com/thesavant42/bigshot/issues
- **Documentation**: Check the `/docs` directory
- **Community**: Join the discussion in GitHub Discussions

### Advanced Debugging

For complex issues, enable debug mode:

```bash
# Enable debug logging
export DEBUG=true
docker-compose -f docker-compose.dev.yml up

# Enable SQL logging
export SQL_DEBUG=true

# Enable verbose Docker output
export COMPOSE_VERBOSE=true
docker-compose --verbose up
```

Remember to disable debug mode in production environments for security and performance reasons.