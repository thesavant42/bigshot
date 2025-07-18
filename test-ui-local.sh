#!/bin/bash
# Simple local test script for UI health testing

set -e

echo "🧪 Starting local UI health test validation..."

# Check if required dependencies are available
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true

# Start the application stack
echo "🚀 Starting application stack..."
docker-compose -f docker-compose.test.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

echo "📊 Service status:"
docker-compose -f docker-compose.test.yml ps

# Test the endpoints manually
echo "🔍 Testing application endpoints..."

# Test backend health
if curl -f http://localhost:5000/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend health endpoint is responding"
else
    echo "❌ Backend health endpoint is not responding"
    docker-compose -f docker-compose.test.yml logs backend
    docker-compose -f docker-compose.test.yml down -v
    exit 1
fi

# Test frontend
if curl -f http://localhost:80 > /dev/null 2>&1; then
    echo "✅ Frontend is responding"
else
    echo "❌ Frontend is not responding"
    docker-compose -f docker-compose.test.yml logs frontend
    docker-compose -f docker-compose.test.yml down -v
    exit 1
fi

# Install frontend dependencies if needed
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm ci
fi

# Install Playwright browsers if needed
if [ ! -d "~/.cache/ms-playwright" ]; then
    echo "📥 Installing Playwright browsers..."
    npx playwright install chromium
fi

# Run the UI tests
echo "🎭 Running Playwright UI tests..."
export PLAYWRIGHT_BASE_URL=http://localhost:80
export CI=true

if npm run test:e2e; then
    echo "✅ UI tests passed!"
    
    # Check if screenshot was created
    if [ -f "test-results/dashboard-health.png" ]; then
        SIZE=$(stat -c%s "test-results/dashboard-health.png" 2>/dev/null || stat -f%z "test-results/dashboard-health.png" 2>/dev/null || echo "0")
        echo "📸 Dashboard screenshot created: ${SIZE} bytes"
        
        if [ "$SIZE" -gt 30000 ]; then
            echo "✅ Screenshot appears healthy"
        else
            echo "⚠️ Screenshot may be too small"
        fi
    else
        echo "⚠️ No dashboard screenshot found"
    fi
    
else
    echo "❌ UI tests failed"
    cd ..
    docker-compose -f docker-compose.test.yml logs
    docker-compose -f docker-compose.test.yml down -v
    exit 1
fi

cd ..

# Clean up
echo "🧹 Cleaning up..."
docker-compose -f docker-compose.test.yml down -v

echo "🎉 Local UI health test validation completed successfully!"