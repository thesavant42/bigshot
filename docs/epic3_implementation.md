# Epic 3: Background Task & Job Processing - Implementation Guide

## Overview

This implementation provides a comprehensive background task and job processing system for the bigshot application, featuring asynchronous enumeration, data normalization, deduplication, and real-time notifications.

## Architecture

### Core Components

1. **Celery Integration** - Distributed task queue for background processing
2. **Redis Message Broker** - High-performance message broker and cache
3. **Domain Enumeration Workers** - Specialized workers for each external source
4. **WebSocket Service** - Real-time updates and notifications
5. **Job Management System** - Comprehensive job lifecycle management
6. **Data Processing Pipeline** - Normalization and deduplication

### File Structure

```
app/
├── tasks/
│   ├── __init__.py
│   ├── domain_enumeration.py    # Domain enumeration tasks
│   ├── data_processing.py       # Data normalization & deduplication
│   └── notifications.py         # Notification tasks
├── services/
│   ├── enumeration.py           # Updated enumeration service
│   ├── job_manager.py           # Enhanced job management
│   └── websocket.py             # WebSocket service
└── api/
    └── jobs.py                  # Enhanced job API endpoints

celery_app.py                    # Celery application factory
celery_worker.py                 # Celery worker script
start_system.sh                  # System startup script
```

## Features Implemented

### ✅ 1. Celery Integration with Flask

- **Celery Application Factory**: `celery_app.py` provides configurable Celery instance
- **Task Modules**: Organized tasks in `app/tasks/` directory
- **Flask Context**: Tasks run with Flask application context
- **Queue Configuration**: Separate queues for different task types

### ✅ 2. Redis Message Broker and Cache

- **Message Broker**: Redis handles task queuing and distribution
- **Result Backend**: Task results cached in Redis
- **Pub/Sub**: Real-time notifications via Redis pub/sub
- **Connection Pooling**: Efficient Redis connection management

### ✅ 3. Domain Enumeration Workers

- **Async Task Processing**: Background enumeration with progress tracking
- **Multiple Sources**: Support for crt.sh, VirusTotal, and Shodan
- **Error Handling**: Robust error handling and retry mechanisms
- **Result Storage**: Efficient storage of enumeration results

### ✅ 4. Job Status & Progress Tracking

- **Real-time Updates**: Live progress tracking via WebSocket
- **Task State Management**: Comprehensive job lifecycle tracking
- **Progress Metadata**: Detailed progress information
- **Completion Estimation**: Intelligent completion time estimation

### ✅ 5. Data Normalization & Deduplication Pipeline

- **Domain Normalization**: Standardizes domain formats
- **Deduplication**: Merges duplicate domains from different sources
- **Cleanup Jobs**: Removes old data based on configurable age
- **Batch Processing**: Efficient bulk operations

### ✅ 6. Notification Hooks

- **Job Lifecycle Notifications**: Start, progress, completion, failure
- **WebSocket Broadcasting**: Real-time updates to connected clients
- **Notification History**: Tracking of all notifications
- **Webhook Support**: External webhook notifications

### ✅ 7. Comprehensive Testing

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Mock Testing**: Celery task mocking for reliable tests
- **Error Case Testing**: Failure scenario coverage

## API Endpoints

### Job Management
- `GET /api/v1/jobs` - List jobs with filtering and pagination
- `GET /api/v1/jobs/{id}` - Get specific job details
- `POST /api/v1/jobs/{id}/cancel` - Cancel running job
- `GET /api/v1/jobs/{id}/logs` - Get job execution logs
- `GET /api/v1/jobs/{id}/status` - Get detailed job status
- `GET /api/v1/jobs/{id}/results` - Get job results
- `GET /api/v1/jobs/{id}/task-status` - Get Celery task status

### Data Processing
- `POST /api/v1/jobs/data/normalize` - Start data normalization
- `POST /api/v1/jobs/data/deduplicate` - Start data deduplication
- `POST /api/v1/jobs/data/cleanup` - Start data cleanup

### Statistics & Monitoring
- `GET /api/v1/jobs/stats` - Get job statistics
- `GET /api/v1/websocket/stats` - Get WebSocket connection stats

## WebSocket Events

### Client Events
- `connect` - Establish WebSocket connection (requires JWT token)
- `subscribe_job` - Subscribe to specific job updates
- `unsubscribe_job` - Unsubscribe from job updates
- `subscribe_all_jobs` - Subscribe to all job updates
- `get_active_jobs` - Request list of active jobs

### Server Events
- `connected` - Connection acknowledgment
- `job_update` - Real-time job updates
- `active_jobs` - List of currently active jobs
- `subscribed` - Subscription confirmation
- `error` - Error messages

## Usage Examples

### Starting Domain Enumeration

```python
from app.services.enumeration import EnumerationService

service = EnumerationService()
job = service.start_enumeration(
    domains=['example.com'],
    sources=['crt.sh', 'virustotal'],
    options={}
)
```

### Data Processing

```python
from app.services.job_manager import JobManager

job_manager = JobManager()

# Start normalization
normalize_job = job_manager.start_data_normalization()

# Start deduplication
dedupe_job = job_manager.start_data_deduplication()

# Start cleanup (remove data older than 30 days)
cleanup_job = job_manager.start_data_cleanup(days_old=30)
```

### WebSocket Client

```javascript
const socket = io('http://localhost:5000', {
    auth: {
        token: 'your-jwt-token'
    }
});

// Subscribe to all job updates
socket.emit('subscribe_all_jobs');

// Listen for job updates
socket.on('job_update', (data) => {
    console.log('Job update:', data);
});
```

## Running the System

### Prerequisites
- Redis server installed and running
- Python dependencies installed (`pip install -r requirements.txt`)

### Manual Start
```bash
# Start Redis
redis-server --daemonize yes

# Start Celery worker
python celery_worker.py

# Start Flask application
python run.py
```

### Automated Start
```bash
# Use the provided start script
./start_system.sh
```

## Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Test job processing
python -m pytest tests/test_job_processing.py -v

# Test domain functionality
python -m pytest tests/test_domains.py -v

# Test authentication
python -m pytest tests/test_auth.py -v
```

### Test Coverage
```bash
python -m pytest tests/ --cov=app --cov-report=html
```

## Monitoring and Debugging

### Celery Monitoring
```bash
# Monitor Celery worker
celery -A celery_app.celery_app events

# Monitor task execution
celery -A celery_app.celery_app monitor
```

### Redis Monitoring
```bash
# Connect to Redis CLI
redis-cli

# Monitor Redis commands
redis-cli monitor

# Check Redis info
redis-cli info
```

### Application Logs
- Flask logs: Console output from `python run.py`
- Celery logs: Console output from `python celery_worker.py`
- WebSocket logs: Integrated with Flask logging

## Performance Considerations

### Scalability
- **Horizontal Scaling**: Multiple Celery workers can be started
- **Queue Isolation**: Different task types use separate queues
- **Connection Pooling**: Redis connections are pooled for efficiency
- **Task Routing**: Tasks routed to appropriate workers

### Optimization
- **Batch Processing**: Data operations process multiple records at once
- **Progress Tracking**: Minimal overhead progress updates
- **Result Caching**: Task results cached in Redis
- **Database Indexing**: Proper indexing for job queries

## Production Deployment

### Docker Configuration
```dockerfile
# Example Dockerfile for Celery worker
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "celery_worker.py"]
```

### Environment Variables
```bash
# Production configuration
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@db:5432/bigshot
export REDIS_URL=redis://redis:6379/0
export CELERY_BROKER_URL=redis://redis:6379/0
```

### Monitoring Setup
- **Flower**: Web-based Celery monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Sentry**: Error tracking and monitoring

## Security Considerations

### Authentication
- WebSocket connections require JWT tokens
- API endpoints protected with JWT authentication
- Task results access controlled

### Network Security
- Redis connection security
- WebSocket CORS configuration
- API rate limiting

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Check Redis server status: `redis-cli ping`
   - Verify Redis URL configuration

2. **Celery Tasks Not Executing**
   - Check worker status: `celery -A celery_app.celery_app status`
   - Verify task imports and registration

3. **WebSocket Connection Issues**
   - Check JWT token validity
   - Verify CORS configuration
   - Check network connectivity

### Debug Mode
```bash
# Start with debug logging
export CELERY_LOG_LEVEL=DEBUG
python celery_worker.py
```

## Contributing

### Adding New Tasks
1. Create task function in appropriate module under `app/tasks/`
2. Register task with Celery decorators
3. Add task routing in `celery_app.py`
4. Create corresponding API endpoints
5. Add comprehensive tests

### Testing Guidelines
- Mock external dependencies
- Test error scenarios
- Validate task state transitions
- Test WebSocket functionality
- Performance testing for large datasets

## Future Enhancements

### Planned Features
- **Multi-tenant Support**: Isolated job processing per tenant
- **Advanced Scheduling**: Cron-like job scheduling
- **Workflow Engine**: Complex multi-step job workflows
- **Distributed Processing**: Cross-datacenter task distribution
- **Enhanced Monitoring**: Custom metrics and alerting

### Performance Improvements
- **Database Sharding**: Horizontal database scaling
- **Caching Layer**: Enhanced caching strategies
- **Task Prioritization**: Priority-based task queuing
- **Resource Management**: Dynamic resource allocation

This implementation provides a robust, scalable foundation for background task processing in the bigshot application, meeting all requirements of Epic 3 with room for future enhancements.