#!/bin/bash

# Comprehensive Docker configuration validation script
# Tests frontend-backend communication setup

echo "=== BigShot Docker Configuration Validation ==="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall success
OVERALL_SUCCESS=true

# Helper functions
success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    OVERALL_SUCCESS=false
}

# Test 1: Validate Docker Compose Files
echo "1. Validating Docker Compose configurations..."

for file in docker-compose.yml docker-compose.dev.yml docker-compose.prod.yml; do
    if [ -f "$file" ]; then
        echo "   Testing $file..."
        if docker compose -f "$file" config >/dev/null 2>&1; then
            success "   $file is valid"
        else
            error "   $file has syntax errors"
        fi
        
        # Check for required services
        if docker compose -f "$file" config --services 2>/dev/null | grep -q "backend"; then
            success "   Backend service defined in $file"
        else
            error "   Backend service missing in $file"
        fi
        
        if docker compose -f "$file" config --services 2>/dev/null | grep -q "frontend"; then
            success "   Frontend service defined in $file"
        else
            error "   Frontend service missing in $file"
        fi
    else
        warning "   $file not found"
    fi
done
echo ""

# Test 2: Validate Frontend Configuration
echo "2. Validating frontend configuration..."

if [ -f "frontend/vite.config.ts" ]; then
    if grep -q "localhost:5000" frontend/vite.config.ts; then
        success "   Vite proxy targets correct port (5000)"
    else
        error "   Vite proxy configuration incorrect"
    fi
    
    if grep -q "host: '0.0.0.0'" frontend/vite.config.ts; then
        success "   Vite configured for external connections"
    else
        warning "   Vite may not accept external connections"
    fi
else
    error "   vite.config.ts not found"
fi

if [ -f "frontend/nginx.conf" ]; then
    if grep -q "http://backend:5000" frontend/nginx.conf; then
        success "   Nginx proxies to correct backend service"
    else
        error "   Nginx proxy configuration incorrect"
    fi
    
    if grep -q "location /api/" frontend/nginx.conf; then
        success "   API proxy location configured"
    else
        error "   API proxy location missing"
    fi
    
    if grep -q "location /socket.io/" frontend/nginx.conf; then
        success "   WebSocket proxy location configured"
    else
        error "   WebSocket proxy location missing"
    fi
else
    error "   nginx.conf not found"
fi
echo ""

# Test 3: Test Frontend Build
echo "3. Testing frontend build process..."

cd frontend || exit 1

if [ -f "package.json" ]; then
    success "   package.json found"
    
    # Check if node_modules exists or install dependencies
    if [ ! -d "node_modules" ]; then
        echo "   Installing dependencies..."
        if npm ci >/dev/null 2>&1; then
            success "   Dependencies installed successfully"
        else
            error "   Failed to install dependencies"
        fi
    else
        success "   Dependencies already installed"
    fi
    
    # Test build
    echo "   Building frontend..."
    if npm run build >/dev/null 2>&1; then
        success "   Frontend builds successfully"
        
        if [ -d "dist" ]; then
            success "   Build artifacts created"
        else
            error "   Build artifacts missing"
        fi
    else
        error "   Frontend build failed"
    fi
else
    error "   package.json not found in frontend directory"
fi

cd .. || exit 1
echo ""

# Test 4: Validate Environment Detection Logic
echo "4. Testing environment detection logic..."

# Run our environment detection test
if node /tmp/test_environment_detection.js >/dev/null 2>&1; then
    success "   Environment detection logic works correctly"
else
    error "   Environment detection logic has issues"
fi
echo ""

# Test 5: Docker Image Build Test (optional - skip if no Docker available)
echo "5. Testing Docker image builds..."

if command -v docker >/dev/null 2>&1; then
    success "   Docker is available"
    
    # Test frontend Docker build
    echo "   Building frontend Docker image..."
    if docker build -t bigshot-frontend-test frontend/ >/dev/null 2>&1; then
        success "   Frontend Docker image builds successfully"
        
        # Clean up
        docker rmi bigshot-frontend-test >/dev/null 2>&1
    else
        error "   Frontend Docker image build failed"
    fi
else
    warning "   Docker not available - skipping image build tests"
fi
echo ""

# Test 6: Configuration File Consistency
echo "6. Checking configuration consistency..."

# Check that all Docker compose files use the same service names
BACKEND_SERVICE_NAME=""
FRONTEND_SERVICE_NAME=""

for file in docker-compose.yml docker-compose.dev.yml; do
    if [ -f "$file" ]; then
        if grep -q "backend:" "$file"; then
            if [ -z "$BACKEND_SERVICE_NAME" ]; then
                BACKEND_SERVICE_NAME="backend"
            fi
            success "   $file uses 'backend' service name"
        else
            error "   $file missing 'backend' service"
        fi
        
        if grep -q "frontend:" "$file"; then
            if [ -z "$FRONTEND_SERVICE_NAME" ]; then
                FRONTEND_SERVICE_NAME="frontend"
            fi
            success "   $file uses 'frontend' service name"
        else
            error "   $file missing 'frontend' service"
        fi
    fi
done
echo ""

# Test 7: Documentation Check
echo "7. Checking documentation..."

if [ -f "docs/docker-networking.md" ]; then
    success "   Docker networking documentation exists"
    
    if grep -q "backend:5000" docs/docker-networking.md; then
        success "   Documentation mentions correct backend service"
    else
        warning "   Documentation may be incomplete"
    fi
else
    error "   Docker networking documentation missing"
fi

if [ -f "README.md" ]; then
    success "   README.md exists"
else
    warning "   README.md not found"
fi
echo ""

# Summary
echo "=== Validation Summary ==="
if [ "$OVERALL_SUCCESS" = true ]; then
    echo -e "${GREEN}All critical tests passed! ✓${NC}"
    echo ""
    echo "The frontend-backend communication should work correctly in Docker deployments."
    echo "Key fixes implemented:"
    echo "  • Vite proxy targets correct backend port (5000)"
    echo "  • Nginx proxy configuration is correct"
    echo "  • Environment detection handles all scenarios"
    echo "  • Documentation provides troubleshooting guidance"
    echo ""
    exit 0
else
    echo -e "${RED}Some tests failed! ✗${NC}"
    echo ""
    echo "Please review the errors above and fix any issues before deploying."
    echo ""
    exit 1
fi