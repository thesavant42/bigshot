#!/bin/bash
"""
Stop development environment script for BigShot
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

# Stop development environment
stop_development() {
    print_status "Stopping BigShot development environment..."
    
    # Stop all services
    docker-compose -f docker-compose.dev.yml down
    
    # Show final status
    print_status "Development environment stopped!"
    print_status "All containers have been stopped and removed."
    print_status ""
    print_status "To start again: ./scripts/setup_dev.sh"
}

# Cleanup function (optional)
cleanup() {
    print_warning "This will remove all containers, volumes, and networks!"
    read -p "Are you sure you want to cleanup everything? [y/N]: " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        print_status "Cleaning up development environment..."
        
        # Stop and remove everything
        docker-compose -f docker-compose.dev.yml down -v --remove-orphans
        
        # Remove custom networks
        docker network rm bigshot_dev_network 2>/dev/null || true
        
        print_status "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Main function
main() {
    echo "BigShot Development Environment Control"
    echo "======================================"
    echo ""
    echo "What would you like to do?"
    echo "1) Stop development environment"
    echo "2) Stop and cleanup everything (removes volumes)"
    echo ""
    read -p "Enter your choice [1-2]: " choice
    
    case $choice in
        1)
            stop_development
            ;;
        2)
            cleanup
            ;;
        *)
            print_error "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
}

# Run main function
main "$@"