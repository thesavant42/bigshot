# BigShot Maintenance Guide

This guide covers routine maintenance procedures to ensure optimal performance, security, and reliability of the BigShot platform.

## Table of Contents

1. [Maintenance Overview](#maintenance-overview)
2. [Daily Maintenance](#daily-maintenance)
3. [Weekly Maintenance](#weekly-maintenance)
4. [Monthly Maintenance](#monthly-maintenance)
5. [Quarterly Maintenance](#quarterly-maintenance)
6. [Performance Optimization](#performance-optimization)
7. [Security Maintenance](#security-maintenance)
8. [Backup Maintenance](#backup-maintenance)
9. [Database Maintenance](#database-maintenance)
10. [System Updates](#system-updates)
11. [Monitoring and Alerting](#monitoring-and-alerting)
12. [Emergency Procedures](#emergency-procedures)

## Maintenance Overview

### Maintenance Philosophy
- **Proactive**: Address issues before they become problems
- **Scheduled**: Regular maintenance windows with minimal disruption
- **Documented**: All maintenance activities are logged
- **Tested**: Changes are tested in development first
- **Monitored**: Continuous monitoring during and after maintenance

### Maintenance Schedule
- **Daily**: Health checks, log review, backup verification
- **Weekly**: Security updates, performance review, capacity planning
- **Monthly**: System updates, optimization, security audit
- **Quarterly**: Major updates, disaster recovery testing, architecture review

## Daily Maintenance

### Morning Checklist (Start of Business Day)

#### 1. System Health Check
```bash
# Check overall system health
curl -s http://localhost:5000/api/v1/health | jq '.'

# Check detailed health status
curl -s -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/v1/health/detailed | jq '.'

# Verify all services are running
docker-compose ps
```

#### 2. Resource Monitoring
```bash
# Check system resources
docker stats --no-stream

# Check disk usage
df -h

# Check memory usage
free -h

# Check system load
uptime
```

#### 3. Log Review
```bash
# Check for errors in application logs
tail -100 logs/app.log | grep -i error

# Check nginx access logs for anomalies
tail -100 logs/nginx/access.log | grep -E "(4[0-9][0-9]|5[0-9][0-9])"

# Check database logs
docker-compose logs database | tail -50 | grep -i error
```

#### 4. Backup Verification
```bash
# Check backup status
curl -s -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/v1/backup/status | jq '.'

# Verify last backup timestamp
ls -la backups/ | head -10

# Check backup integrity (sample)
tar -tzf backups/$(ls -t backups/ | head -1) > /dev/null && echo "Backup OK" || echo "Backup corrupted"
```

### Evening Checklist (End of Business Day)

#### 1. Performance Review
```bash
# Check system metrics
curl -s http://localhost:5000/api/v1/metrics | jq '.'

# Check database performance
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins + n_tup_upd + n_tup_del as modifications,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables 
ORDER BY modifications DESC 
LIMIT 10;
"
```

#### 2. Job Queue Status
```bash
# Check Celery worker status
docker-compose exec backend python -c "
from celery_app import celery_app
inspect = celery_app.control.inspect()
print('Active tasks:', inspect.active())
print('Scheduled tasks:', inspect.scheduled())
print('Worker stats:', inspect.stats())
"
```

#### 3. Security Review
```bash
# Check recent login attempts
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT username, login_time, ip_address, success 
FROM login_attempts 
WHERE login_time > NOW() - INTERVAL '24 hours'
ORDER BY login_time DESC 
LIMIT 20;
"

# Check for suspicious activities
grep -i "failed\|error\|warning" logs/app.log | grep $(date +%Y-%m-%d)
```

## Weekly Maintenance

### Week Start (Monday)

#### 1. System Updates
```bash
# Update system packages
sudo apt update && sudo apt list --upgradable

# Check for Docker updates
docker version
docker-compose version

# Check for Python package updates
pip list --outdated

# Check for Node.js package updates
cd frontend && npm outdated
```

#### 2. Security Updates
```bash
# Check for security updates
sudo apt list --upgradable | grep -i security

# Update security packages
sudo apt update && sudo apt upgrade -y

# Check Docker security advisories
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasecurity/trivy image bigshot_backend:latest
```

#### 3. Performance Analysis
```bash
# Analyze database performance
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    query,
    calls,
    total_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
"

# Check slow queries
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
WHERE mean_time > 100
ORDER BY mean_time DESC 
LIMIT 10;
"
```

### Week End (Friday)

#### 1. Weekly Backup
```bash
# Create weekly backup
./scripts/backup.sh --prod --name "weekly-$(date +%Y%m%d)"

# Verify backup integrity
tar -tzf backups/weekly-$(date +%Y%m%d).tar.gz > /dev/null && echo "Backup OK"

# Archive old backups
find backups/ -name "bigshot_backup_*.tar.gz" -mtime +30 -delete
```

#### 2. Capacity Planning
```bash
# Check growth trends
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;
"

# Check disk usage trends
df -h >> logs/disk_usage_$(date +%Y%m).log
```

#### 3. Log Rotation
```bash
# Rotate logs
sudo logrotate -f /etc/logrotate.d/bigshot

# Compress old logs
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;

# Clean up old compressed logs
find logs/ -name "*.gz" -mtime +30 -delete
```

## Monthly Maintenance

### Month Start

#### 1. System Optimization
```bash
# Database optimization
docker-compose exec database psql -U bigshot -d bigshot -c "
VACUUM ANALYZE;
REINDEX DATABASE bigshot;
"

# Check database statistics
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    (n_dead_tup::float / NULLIF(n_live_tup + n_dead_tup, 0)) * 100 as dead_percentage
FROM pg_stat_user_tables 
WHERE n_dead_tup > 0
ORDER BY dead_percentage DESC;
"

# Redis optimization
docker-compose exec redis redis-cli BGREWRITEAOF
```

#### 2. Security Audit
```bash
# Check for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasecurity/trivy image bigshot_backend:latest

# Review user accounts
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    username,
    email,
    last_login,
    created_at,
    is_active
FROM users 
ORDER BY last_login DESC;
"

# Check SSL certificate expiration
openssl x509 -in ssl/cert.pem -text -noout | grep "Not After"
```

#### 3. Performance Tuning
```bash
# Analyze query performance
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    query,
    calls,
    total_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 20;
"

# Check index usage
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
"
```

### Month End

#### 1. Monthly Reports
```bash
# Generate usage report
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    COUNT(*) as total_domains,
    COUNT(CASE WHEN created_at >= date_trunc('month', CURRENT_DATE) THEN 1 END) as domains_this_month,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_domains
FROM domains;
"

# Job statistics
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    job_type,
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_duration_seconds
FROM jobs 
WHERE created_at >= date_trunc('month', CURRENT_DATE)
GROUP BY job_type;
"
```

#### 2. Archive Old Data
```bash
# Archive old jobs
docker-compose exec database psql -U bigshot -d bigshot -c "
CREATE TABLE IF NOT EXISTS jobs_archive (LIKE jobs INCLUDING ALL);
INSERT INTO jobs_archive SELECT * FROM jobs WHERE created_at < NOW() - INTERVAL '3 months';
DELETE FROM jobs WHERE created_at < NOW() - INTERVAL '3 months';
"

# Archive old logs
mkdir -p archive/$(date +%Y%m)
mv logs/*.log.gz archive/$(date +%Y%m)/ 2>/dev/null || true
```

## Quarterly Maintenance

### Quarter Start

#### 1. Major Updates
```bash
# Update base images
docker pull python:3.12-slim
docker pull node:18-alpine
docker pull postgres:15
docker pull redis:7-alpine

# Rebuild images
docker-compose build --no-cache

# Test in development environment
docker-compose -f docker-compose.dev.yml up -d
# Run tests
docker-compose -f docker-compose.dev.yml exec backend python -m pytest tests/
```

#### 2. Disaster Recovery Testing
```bash
# Test backup restoration
./scripts/restore_backup.sh --dev --file latest_backup.tar.gz

# Test failover procedures
# Document results and update procedures
```

#### 3. Architecture Review
```bash
# Review system architecture
# Check for performance bottlenecks
# Plan for scaling needs
# Update documentation
```

### Quarter End

#### 1. Performance Review
```bash
# Generate quarterly performance report
# Analyze growth trends
# Plan capacity improvements
# Update monitoring thresholds
```

#### 2. Security Review
```bash
# Review access controls
# Update security policies
# Rotate secrets and certificates
# Update security documentation
```

## Performance Optimization

### Database Optimization

#### Query Performance
```bash
# Identify slow queries
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
WHERE mean_time > 100
ORDER BY total_time DESC 
LIMIT 10;
"

# Optimize slow queries
# Add indexes where needed
# Rewrite inefficient queries
```

#### Index Optimization
```bash
# Check index usage
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE idx_scan = 0
ORDER BY idx_tup_read DESC;
"

# Remove unused indexes
# Add missing indexes
```

### Application Performance

#### Memory Optimization
```bash
# Monitor memory usage
docker stats --no-stream

# Optimize Python memory usage
docker-compose exec backend python -c "
import gc
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'Memory percent: {process.memory_percent():.2f}%')
print(f'GC collections: {gc.get_stats()}')
"
```

#### Cache Optimization
```bash
# Monitor Redis performance
docker-compose exec redis redis-cli INFO stats
docker-compose exec redis redis-cli INFO memory

# Optimize cache keys
docker-compose exec redis redis-cli --bigkeys

# Monitor cache hit rates
docker-compose exec redis redis-cli INFO stats | grep keyspace
```

## Security Maintenance

### SSL Certificate Management

#### Certificate Renewal
```bash
# Check certificate expiration
openssl x509 -in ssl/cert.pem -text -noout | grep "Not After"

# Renew Let's Encrypt certificate
sudo certbot renew --dry-run
sudo certbot renew

# Update certificate in containers
docker-compose restart frontend
```

### Security Updates

#### System Security
```bash
# Update security packages
sudo apt update && sudo apt upgrade -y

# Check for security advisories
sudo apt list --upgradable | grep -i security

# Update Docker security
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasecurity/trivy image bigshot_backend:latest
```

#### Application Security
```bash
# Update Python packages
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Update Node.js packages
cd frontend && npm audit fix
```

## Backup Maintenance

### Backup Verification

#### Daily Backup Check
```bash
# Verify backup existence
ls -la backups/ | head -5

# Check backup integrity
tar -tzf backups/$(ls -t backups/ | head -1) > /dev/null && echo "Backup OK" || echo "Backup corrupted"

# Test backup restoration (monthly)
./scripts/restore_backup.sh --dev --file latest_backup.tar.gz
```

#### Backup Cleanup
```bash
# Remove old backups
find backups/ -name "*.tar.gz" -mtime +30 -delete

# Archive important backups
mkdir -p archive/backups/$(date +%Y%m)
mv backups/weekly-*.tar.gz archive/backups/$(date +%Y%m)/ 2>/dev/null || true
```

### Backup Strategy Review

#### Monthly Review
- Verify backup frequency meets RTO/RPO requirements
- Test backup restoration procedures
- Review backup storage capacity
- Update backup documentation

## Database Maintenance

### Regular Maintenance

#### Weekly Database Tasks
```bash
# Update statistics
docker-compose exec database psql -U bigshot -d bigshot -c "ANALYZE;"

# Check for bloat
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    (n_dead_tup::float / NULLIF(n_live_tup + n_dead_tup, 0)) * 100 as dead_percentage
FROM pg_stat_user_tables 
WHERE n_dead_tup > 0
ORDER BY dead_percentage DESC;
"

# Vacuum if needed
docker-compose exec database psql -U bigshot -d bigshot -c "VACUUM ANALYZE;"
```

#### Monthly Database Tasks
```bash
# Reindex database
docker-compose exec database psql -U bigshot -d bigshot -c "REINDEX DATABASE bigshot;"

# Check database size
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    pg_size_pretty(pg_database_size('bigshot')) as database_size,
    pg_size_pretty(pg_total_relation_size('domains')) as domains_table_size,
    pg_size_pretty(pg_total_relation_size('jobs')) as jobs_table_size;
"

# Archive old data
docker-compose exec database psql -U bigshot -d bigshot -c "
DELETE FROM jobs WHERE created_at < NOW() - INTERVAL '6 months' AND status = 'completed';
"
```

## System Updates

### Update Procedure

#### 1. Pre-Update Preparation
```bash
# Create backup
./scripts/backup.sh --prod --name "pre-update-$(date +%Y%m%d)"

# Test in development
git pull origin main
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
```

#### 2. Update Process
```bash
# Update production
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verify update
curl -s http://localhost:5000/api/v1/health | jq '.'
```

#### 3. Post-Update Verification
```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# Check application functionality
# Run smoke tests
# Monitor logs for errors
```

## Monitoring and Alerting

### Monitoring Setup

#### Key Metrics to Monitor
- System resources (CPU, memory, disk)
- Database performance
- Application response times
- Error rates
- Security events

#### Alerting Rules
```bash
# Setup alerts for:
# - High CPU usage (>80%)
# - High memory usage (>90%)
# - Disk space low (<10%)
# - Database connection failures
# - Application errors
```

### Log Monitoring

#### Log Analysis
```bash
# Daily log review
grep -i error logs/app.log | tail -20
grep -i warning logs/app.log | tail -20

# Security log review
grep -i "failed login\|security\|unauthorized" logs/app.log | tail -10
```

## Emergency Procedures

### System Failure

#### 1. Immediate Response
```bash
# Check system status
docker-compose ps

# Check system resources
docker stats --no-stream
df -h
free -h

# Check service logs
docker-compose logs --tail=50
```

#### 2. Service Recovery
```bash
# Restart failed services
docker-compose restart service_name

# Full system restart if needed
docker-compose down && docker-compose up -d

# Restore from backup if needed
./scripts/restore_backup.sh --prod --file latest_backup.tar.gz
```

### Security Incident

#### 1. Immediate Actions
```bash
# Check for security events
grep -i "security\|unauthorized\|failed login" logs/app.log

# Review recent access
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT * FROM login_attempts 
WHERE login_time > NOW() - INTERVAL '1 hour'
ORDER BY login_time DESC;
"

# Block suspicious IPs if needed
# Update firewall rules
```

#### 2. Investigation
```bash
# Collect evidence
tar -czf incident_logs_$(date +%Y%m%d_%H%M).tar.gz logs/

# Review system changes
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT * FROM audit_log 
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
"
```

### Data Loss Recovery

#### 1. Assess Damage
```bash
# Check database integrity
docker-compose exec database psql -U bigshot -d bigshot -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables;
"
```

#### 2. Recovery Process
```bash
# Restore from most recent backup
./scripts/restore_backup.sh --prod --file latest_backup.tar.gz

# Verify data integrity
# Check for missing data
# Restore from earlier backup if needed
```

## Maintenance Documentation

### Maintenance Log

Keep a log of all maintenance activities:
- Date and time
- Activities performed
- Results and observations
- Any issues encountered
- Follow-up actions needed

### Maintenance Schedule

Update maintenance schedules based on:
- System performance
- Security requirements
- Business needs
- Regulatory compliance

For questions or support, please refer to the troubleshooting guide or contact the development team.