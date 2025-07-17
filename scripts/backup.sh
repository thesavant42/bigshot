#!/bin/bash
"""
Database backup script for BigShot
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

# Configuration
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="bigshot_backup_${TIMESTAMP}"
COMPOSE_FILE="docker-compose.yml"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            COMPOSE_FILE="docker-compose.dev.yml"
            shift
            ;;
        --prod)
            COMPOSE_FILE="docker-compose.prod.yml"
            shift
            ;;
        --name)
            BACKUP_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--dev|--prod] [--name backup_name]"
            echo ""
            echo "Options:"
            echo "  --dev     Use development environment"
            echo "  --prod    Use production environment"
            echo "  --name    Custom backup name (default: bigshot_backup_TIMESTAMP)"
            echo "  --help    Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create backup directory
create_backup_directory() {
    local backup_path="${BACKUP_DIR}/${BACKUP_NAME}"
    mkdir -p "$backup_path"
    echo "$backup_path"
}

# Backup database
backup_database() {
    local backup_path=$1
    
    print_status "Backing up PostgreSQL database..."
    
    # Get database container name
    local db_container=$(docker-compose -f "$COMPOSE_FILE" ps -q database)
    
    if [ -z "$db_container" ]; then
        print_error "Database container not found. Make sure the environment is running."
        exit 1
    fi
    
    # Create database backup
    docker exec "$db_container" pg_dump -U bigshot -d bigshot --clean --if-exists > "${backup_path}/database_backup.sql"
    
    if [ $? -eq 0 ]; then
        print_status "Database backup completed: ${backup_path}/database_backup.sql"
    else
        print_error "Database backup failed"
        exit 1
    fi
}

# Backup Redis data
backup_redis() {
    local backup_path=$1
    
    print_status "Backing up Redis data..."
    
    # Get Redis container name
    local redis_container=$(docker-compose -f "$COMPOSE_FILE" ps -q redis)
    
    if [ -z "$redis_container" ]; then
        print_error "Redis container not found. Make sure the environment is running."
        exit 1
    fi
    
    # Create Redis backup
    docker exec "$redis_container" redis-cli BGSAVE
    sleep 5  # Wait for background save to complete
    
    # Copy dump file
    docker cp "${redis_container}:/data/dump.rdb" "${backup_path}/redis_backup.rdb"
    
    if [ $? -eq 0 ]; then
        print_status "Redis backup completed: ${backup_path}/redis_backup.rdb"
    else
        print_error "Redis backup failed"
        exit 1
    fi
}

# Backup application files
backup_application_files() {
    local backup_path=$1
    
    print_status "Backing up application files..."
    
    # Backup instance directory
    if [ -d "instance" ]; then
        cp -r instance "${backup_path}/instance"
        print_status "Instance files backed up"
    fi
    
    # Backup logs
    if [ -d "logs" ]; then
        cp -r logs "${backup_path}/logs"
        print_status "Log files backed up"
    fi
    
    # Backup configuration
    if [ -f ".env" ]; then
        cp .env "${backup_path}/.env"
        print_status "Environment configuration backed up"
    fi
    
    # Create backup manifest
    cat > "${backup_path}/backup_manifest.json" << EOF
{
    "backup_name": "${BACKUP_NAME}",
    "timestamp": "${TIMESTAMP}",
    "environment": "$(echo $COMPOSE_FILE | cut -d'.' -f2)",
    "components": {
        "database": "database_backup.sql",
        "redis": "redis_backup.rdb",
        "instance": "instance/",
        "logs": "logs/",
        "config": ".env"
    },
    "backup_script_version": "1.0.0"
}
EOF
    
    print_status "Backup manifest created"
}

# Compress backup
compress_backup() {
    local backup_path=$1
    
    print_status "Compressing backup..."
    
    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
    
    if [ $? -eq 0 ]; then
        # Remove uncompressed directory
        rm -rf "$BACKUP_NAME"
        print_status "Backup compressed: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    else
        print_error "Backup compression failed"
        exit 1
    fi
    
    cd - > /dev/null
}

# Calculate backup size
calculate_backup_size() {
    local backup_file="${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    local size=$(du -h "$backup_file" | cut -f1)
    print_status "Backup size: $size"
}

# Main backup function
main() {
    print_status "Starting BigShot backup process..."
    print_status "Environment: $COMPOSE_FILE"
    print_status "Backup name: $BACKUP_NAME"
    
    # Check if environment is running
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_error "Environment is not running. Please start it first."
        exit 1
    fi
    
    # Create backup directory
    backup_path=$(create_backup_directory)
    
    # Perform backups
    backup_database "$backup_path"
    backup_redis "$backup_path"
    backup_application_files "$backup_path"
    
    # Compress backup
    compress_backup "$backup_path"
    
    # Show backup information
    calculate_backup_size
    
    print_status "Backup completed successfully!"
    print_status "Backup location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    print_status "To restore this backup, use: ./scripts/restore_backup.sh --file ${BACKUP_NAME}.tar.gz"
}

# Run main function
main "$@"