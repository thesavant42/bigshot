#!/bin/bash
"""
Start script for bigshot background job processing system
"""

# Function to check if Redis is running
check_redis() {
    if pgrep redis-server > /dev/null; then
        echo "✅ Redis is running"
        return 0
    else
        echo "❌ Redis is not running"
        return 1
    fi
}

# Function to start Redis
start_redis() {
    echo "Starting Redis..."
    redis-server --daemonize yes --port 6379
    sleep 2
    if check_redis; then
        echo "✅ Redis started successfully"
    else
        echo "❌ Failed to start Redis"
        exit 1
    fi
}

# Function to start Celery worker
start_celery() {
    echo "Starting Celery worker..."
    python celery_worker.py -A celery_app.celery_app worker --loglevel=info --concurrency=4 &
    CELERY_PID=$!
    echo "✅ Celery worker started with PID: $CELERY_PID"
}

# Function to start Flask app
start_flask() {
    echo "Starting Flask application..."
    python run.py &
    FLASK_PID=$!
    echo "✅ Flask app started with PID: $FLASK_PID"
}

# Function to stop all services
stop_services() {
    echo "Stopping services..."
    
    # Stop Flask
    if [[ -n $FLASK_PID ]]; then
        kill $FLASK_PID 2>/dev/null
        echo "✅ Flask app stopped"
    fi
    
    # Stop Celery
    if [[ -n $CELERY_PID ]]; then
        kill $CELERY_PID 2>/dev/null
        echo "✅ Celery worker stopped"
    fi
    
    # Stop Redis
    pkill redis-server 2>/dev/null
    echo "✅ Redis stopped"
    
    exit 0
}

# Trap SIGINT and SIGTERM to stop services gracefully
trap stop_services SIGINT SIGTERM

echo "🚀 Starting bigshot background job processing system..."
echo "============================================================"

# Check if Redis is running, start if not
if ! check_redis; then
    start_redis
fi

# Start services
start_celery
sleep 3
start_flask

echo "============================================================"
echo "✅ System started successfully!"
echo ""
echo "Services:"
echo "  - Redis: localhost:6379"
echo "  - Flask API: http://localhost:5000"
echo "  - WebSocket: ws://localhost:5000"
echo "  - Celery worker: Running in background"
echo ""
echo "API Endpoints:"
echo "  - GET /api/v1/jobs - List jobs"
echo "  - POST /api/v1/domains/enumerate - Start enumeration"
echo "  - POST /api/v1/jobs/data/normalize - Start normalization"
echo "  - POST /api/v1/jobs/data/deduplicate - Start deduplication"
echo "  - GET /api/v1/jobs/stats - Job statistics"
echo "  - GET /api/v1/websocket/stats - WebSocket statistics"
echo ""
echo "Press Ctrl+C to stop all services"
echo "============================================================"

# Wait for services to run
wait