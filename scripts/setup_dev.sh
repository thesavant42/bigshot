#!/bin/bash
"""
Enhanced development environment setup script for BigShot
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
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Frontend development will use Docker container."
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_warning "Python 3 is not installed. Backend development will use Docker container."
    fi
    
    print_status "Requirements check completed."
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs/nginx
    mkdir -p instance
    mkdir -p backups
    mkdir -p ssl
    mkdir -p monitoring
    
    print_status "Directories created."
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment file..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Created .env file from .env.example. Please update with your actual values."
    else
        print_status "Environment file already exists."
    fi
}

# Install local dependencies (optional)
install_local_dependencies() {
    print_status "Installing local dependencies..."
    
    # Python dependencies
    if command -v python3 &> /dev/null && command -v pip3 &> /dev/null; then
        print_status "Installing Python dependencies..."
        pip3 install -r requirements.txt
    fi
    
    # Node.js dependencies
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        print_status "Installing Node.js dependencies..."
        cd frontend && npm install && cd ..
    fi
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    # Start database container
    docker-compose -f docker-compose.dev.yml up -d database
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations if needed
    print_status "Database setup completed."
}

# Start development environment
start_development() {
    print_status "Starting development environment..."
    
    # Start all services
    docker-compose -f docker-compose.dev.yml up -d
    
    # Wait for services to be ready
    sleep 15
    
    # Show service status
    docker-compose -f docker-compose.dev.yml ps
    
    print_status "Development environment started!"
    print_status "Services:"
    print_status "  - Frontend: http://localhost:3000"
    print_status "  - Backend API: http://localhost:5001"
    print_status "  - Database: localhost:5433"
    print_status "  - Redis: localhost:6380"
    print_status ""
    print_status "To stop the environment: ./scripts/stop_dev.sh"
    print_status "To view logs: docker-compose -f docker-compose.dev.yml logs -f"
}

# Main setup function
main() {
    print_status "Starting BigShot development environment setup..."
    
    check_requirements
    create_directories
    setup_environment
    
    # Ask user what they want to do
    echo ""
    echo "What would you like to do?"
    echo "1) Install local dependencies (optional)"
    echo "2) Setup database only"
    echo "3) Start full development environment"
    echo "4) All of the above"
    echo ""
    read -p "Enter your choice [1-4]: " choice
    
    case $choice in
        1)
            install_local_dependencies
            ;;
        2)
            setup_database
            ;;
        3)
            start_development
            ;;
        4)
            install_local_dependencies
            setup_database
            start_development
            ;;
        *)
            print_error "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
    
    print_status "Setup completed successfully!"
}

# Run main function
main "$@"