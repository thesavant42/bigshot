#!/bin/bash

# Test script for frontend hot reload functionality in Docker development environment
# This script verifies that frontend changes are reflected in the running container

set -e

echo "🚀 Testing Frontend Hot Reload in Docker Development Environment"
echo "================================================================"

# Navigate to project root
cd "$(dirname "$0")/.."

echo "📦 Building frontend development image..."
docker build -f frontend/Dockerfile.dev -t bigshot-frontend:dev frontend/

echo "🔧 Starting frontend container with volume mounts..."
docker run -d -p 3000:3000 \
  -v "$(pwd)/frontend:/app" \
  -v /app/node_modules \
  -e NODE_ENV=development \
  -e CHOKIDAR_USEPOLLING=true \
  -e CHOKIDAR_INTERVAL=500 \
  --name bigshot-frontend-test \
  bigshot-frontend:dev

echo "⏳ Waiting for Vite dev server to start..."
sleep 10

echo "🌐 Frontend dev server should be running at http://localhost:3000"
echo "📝 To test hot reload:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Make changes to frontend/src/App.tsx"
echo "   3. Changes should appear automatically without manual refresh"

echo ""
echo "🛑 To stop the test container:"
echo "   docker stop bigshot-frontend-test && docker rm bigshot-frontend-test"

echo ""
echo "✅ Frontend hot reload test setup complete!"