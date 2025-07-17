#!/bin/bash
"""
Database restore script for BigShot
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
COMPOSE_FILE="docker-compose.yml"
BACKUP_FILE=""
FORCE_RESTORE=false

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
        --file)
            BACKUP_FILE="$2"
            shift 2
            ;;
        --force)
            FORCE_RESTORE=true
            shift
            ;;
        --list)
            list_backups
            exit 0
            ;;
        --help)
            echo "Usage: $0 [--dev|--prod] --file backup_file [--force]"
            echo ""
            echo "Options:"
            echo "  --dev     Use development environment"
            echo "  --prod    Use production environment"
            echo "  --file    Backup file to restore (required)"
            echo "  --force   Force restore without confirmation"
            echo "  --list    List available backups"
            echo "  --help    Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# List available backups
list_backups() {
    print_status "Available backups:"
    
    if [ -d "$BACKUP_DIR" ]; then
        ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null | while read -r line; do
            echo "  $line"
        done
    else
        print_warning "No backup directory found"
    fi
}

# Validate backup file
validate_backup_file() {
    if [ -z "$BACKUP_FILE" ]; then
        print_error "Backup file is required. Use --file option."
        exit 1
    fi
    
    local backup_path
    if [[ "$BACKUP_FILE" == /* ]]; then
        backup_path="$BACKUP_FILE"
    else
        backup_path="${BACKUP_DIR}/${BACKUP_FILE}"
    fi
    
    if [ ! -f "$backup_path" ]; then
        print_error "Backup file not found: $backup_path"
        exit 1
    fi
    
    echo "$backup_path"
}

# Extract backup
extract_backup() {
    local backup_path=$1
    local extract_dir="${BACKUP_DIR}/restore_$(date +%Y%m%d_%H%M%S)"
    
    print_status "Extracting backup..."
    
    mkdir -p "$extract_dir"
    tar -xzf "$backup_path" -C "$extract_dir"
    
    # Find the extracted directory
    local extracted_dir=$(find "$extract_dir" -maxdepth 1 -type d | grep -v "^${extract_dir}$" | head -1)
    
    if [ -z "$extracted_dir" ]; then
        print_error "Failed to extract backup"
        exit 1
    fi
    
    echo "$extracted_dir"
}

# Verify backup contents
verify_backup() {
    local backup_dir=$1
    
    print_status "Verifying backup contents..."
    
    # Check for manifest file
    if [ ! -f "${backup_dir}/backup_manifest.json" ]; then
        print_warning "Backup manifest not found. This might be an older backup."
    else
        print_status "Backup manifest found"
        cat "${backup_dir}/backup_manifest.json"
    fi
    
    # Check for database backup
    if [ ! -f "${backup_dir}/database_backup.sql" ]; then
        print_error "Database backup file not found"
        exit 1
    fi
    
    # Check for Redis backup
    if [ ! -f "${backup_dir}/redis_backup.rdb" ]; then
        print_warning "Redis backup file not found"
    fi
    
    print_status "Backup verification completed"
}

# Restore database
restore_database() {
    local backup_dir=$1
    
    print_status "Restoring PostgreSQL database..."
    
    # Get database container name
    local db_container=$(docker-compose -f "$COMPOSE_FILE" ps -q database)
    
    if [ -z "$db_container" ]; then
        print_error "Database container not found. Make sure the environment is running."
        exit 1
    fi
    
    # Restore database
    docker exec -i "$db_container" psql -U bigshot -d bigshot < "${backup_dir}/database_backup.sql"
    
    if [ $? -eq 0 ]; then
        print_status "Database restore completed"
    else
        print_error "Database restore failed"
        exit 1
    fi
}

# Restore Redis data
restore_redis() {
    local backup_dir=$1
    
    if [ ! -f "${backup_dir}/redis_backup.rdb" ]; then
        print_warning "Redis backup not found, skipping Redis restore"
        return 0
    fi
    
    print_status "Restoring Redis data..."
    
    # Get Redis container name
    local redis_container=$(docker-compose -f "$COMPOSE_FILE" ps -q redis)
    
    if [ -z "$redis_container" ]; then
        print_error "Redis container not found. Make sure the environment is running."
        exit 1
    fi
    
    # Stop Redis service temporarily
    docker-compose -f "$COMPOSE_FILE" stop redis
    
    # Copy backup file to Redis container
    docker cp "${backup_dir}/redis_backup.rdb" "${redis_container}:/data/dump.rdb"
    
    # Restart Redis service
    docker-compose -f "$COMPOSE_FILE" start redis
    
    if [ $? -eq 0 ]; then
        print_status "Redis restore completed"
    else
        print_error "Redis restore failed"
        exit 1
    fi
}

# Restore application files
restore_application_files() {
    local backup_dir=$1
    
    print_status "Restoring application files..."
    
    # Restore instance directory
    if [ -d "${backup_dir}/instance" ]; then
        if [ -d "instance" ]; then
            mv instance "instance.backup.$(date +%Y%m%d_%H%M%S)"
        fi
        cp -r "${backup_dir}/instance" instance
        print_status "Instance files restored"
    fi
    
    # Restore environment configuration
    if [ -f "${backup_dir}/.env" ]; then
        if [ -f ".env" ]; then
            mv .env ".env.backup.$(date +%Y%m%d_%H%M%S)"
        fi
        cp "${backup_dir}/.env" .env
        print_status "Environment configuration restored"
    fi
    
    print_status "Application files restore completed"
}

# Cleanup extracted files
cleanup() {
    local extract_dir=$1
    
    print_status "Cleaning up temporary files..."
    rm -rf "$extract_dir"
    print_status "Cleanup completed"
}

# Main restore function
main() {
    print_status "Starting BigShot restore process..."
    print_status "Environment: $COMPOSE_FILE"
    print_status "Backup file: $BACKUP_FILE"
    
    # Validate backup file
    backup_path=$(validate_backup_file)
    
    # Check if environment is running
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_error "Environment is not running. Please start it first."
        exit 1
    fi
    
    # Warning about data loss
    if [ "$FORCE_RESTORE" = false ]; then
        print_warning "This will overwrite existing data!"
        read -p "Are you sure you want to continue? [y/N]: " confirm
        
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            print_status "Restore cancelled."
            exit 0
        fi
    fi
    
    # Extract backup
    extract_dir=$(extract_backup "$backup_path")
    
    # Find the actual backup directory
    backup_dir=$(find "$extract_dir" -type d -name "bigshot_backup_*" | head -1)
    if [ -z "$backup_dir" ]; then
        backup_dir="$extract_dir"
    fi
    
    # Verify backup contents
    verify_backup "$backup_dir"
    
    # Perform restore
    restore_database "$backup_dir"
    restore_redis "$backup_dir"
    restore_application_files "$backup_dir"
    
    # Cleanup
    cleanup "$extract_dir"
    
    print_status "Restore completed successfully!"
    print_status "Please restart the environment for changes to take effect."
}

# Run main function
main "$@"