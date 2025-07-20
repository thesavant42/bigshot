#!/bin/bash
#
# Docker entrypoint script for BigShot containers.
#
# This script:
# 1. Waits for database to be available
# 2. Checks if the error_message column exists in the jobs table
# 3. Runs migration if needed
# 4. Starts the requested service (backend, celery, etc.)
#
# Usage in Dockerfile:
#     ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
#     CMD ["python", "run.py"]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to wait for database
wait_for_database() {
    log_info "Waiting for database to be available..."
    
    # Extract database info from DATABASE_URL
    if [[ -z "$DATABASE_URL" ]]; then
        log_warn "DATABASE_URL not set, assuming SQLite"
        return 0
    fi
    
    # For PostgreSQL, wait for connection
    if [[ "$DATABASE_URL" =~ postgresql:// ]]; then
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            log_info "Database connection attempt $attempt/$max_attempts"
            
            if python3 -c "
import os
import sys
from sqlalchemy import create_engine, text
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
            "; then
                log_info "Database is ready!"
                return 0
            fi
            
            log_warn "Database not ready, waiting 2 seconds..."
            sleep 2
            ((attempt++))
        done
        
        log_error "Database failed to become ready after $max_attempts attempts"
        exit 1
    else
        log_info "Using SQLite database"
        return 0
    fi
}

# Function to check if migration is needed
needs_migration() {
    log_info "Checking if error_message column migration is needed..."
    
    python3 -c "
import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError

try:
    # Get database URL
    database_url = os.getenv('DATABASE_URL', 'sqlite:///instance/bigshot.db')
    engine = create_engine(database_url)
    
    # Check if jobs table exists and has error_message column
    inspector = inspect(engine)
    
    # Check if jobs table exists
    if 'jobs' not in inspector.get_table_names():
        print('Jobs table does not exist yet - will be created by schema')
        sys.exit(0)  # No migration needed, table will be created with schema
    
    # Check if error_message column exists
    columns = inspector.get_columns('jobs')
    column_names = [col['name'] for col in columns]
    
    if 'error_message' in column_names:
        print('error_message column already exists')
        sys.exit(0)  # No migration needed
    else:
        print('error_message column is missing')
        sys.exit(1)  # Migration needed
        
except Exception as e:
    print(f'Error checking migration status: {e}')
    # If we can't check, assume migration might be needed
    sys.exit(1)
    "
    
    return $?
}

# Function to run migration
run_migration() {
    log_info "Running error_message column migration..."
    
    if python3 scripts/add_error_message_column.py; then
        log_info "Migration completed successfully"
        return 0
    else
        log_error "Migration failed"
        return 1
    fi
}

# Function to check if this is a database service command
is_database_service() {
    case "$1" in
        *celery*)
            return 0
            ;;
        *run.py*|*server.py*)
            return 0
            ;;
        python*run.py*|python*server.py*)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Main execution
main() {
    log_info "BigShot Docker Entrypoint Starting..."
    log_info "Command: $*"
    
    # Only run database checks for backend/celery services
    if is_database_service "$*"; then
        log_info "This is a database service, checking database status..."
        
        # Wait for database to be available
        wait_for_database
        
        # Check if migration is needed and run it
        if needs_migration; then
            log_warn "Database migration needed"
            if ! run_migration; then
                log_error "Failed to run migration, exiting"
                exit 1
            fi
        else
            log_info "No migration needed, database schema is up to date"
        fi
    else
        log_info "Non-database service detected, skipping database checks"
    fi
    
    # Execute the original command
    log_info "Starting service: $*"
    exec "$@"
}

# Run main function with all arguments
main "$@"