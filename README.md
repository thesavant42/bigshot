# BigShot

A comprehensive domain enumeration and intelligence gathering platform with integrated AI chat capabilities.

## Features

- **Domain Enumeration**: Automated subdomain discovery and enumeration
- **AI Chat Integration**: LLM-powered chat interface with domain intelligence
- **Real-time Updates**: WebSocket-based real-time communication
- **Background Processing**: Celery-based asynchronous task processing
- **Modern UI**: React-based frontend with TypeScript and Tailwind CSS
- **API-First Design**: RESTful API with comprehensive endpoints
- **Performance Monitoring**: Built-in performance tracking and monitoring

## Architecture

### Backend
- **Flask**: Python web framework with REST API
- **SQLAlchemy**: Database ORM with PostgreSQL support
- **Celery**: Distributed task queue for background processing
- **Redis**: Caching and message broker
- **Socket.IO**: Real-time WebSocket communication

### Frontend
- **React**: Modern UI library with TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Fast build tool and development server
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+ (required for background task processing and caching)

### Platform Requirements
- **Windows**: WSL2 is required and is the only tested environment for Windows users
- **Linux/macOS**: Native installation supported

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/thesavant42/bigshot.git
   cd bigshot
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows WSL2: source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   
   # Run migrations
   flask db upgrade
   ```

3. **Start Backend Services**
   ```bash
   # Start Redis (required for the application to function)
   redis-server
   
   # Start Celery worker (requires Redis to be running)
   celery -A celery_app worker --loglevel=info
   
   # Start Flask backend
   python run.py
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Docker Setup

```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up
```

## Testing

### Backend Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test types
python -m pytest -m "unit"
python -m pytest -m "performance"
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

### CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

- **Backend Tests**: Python tests with PostgreSQL and Redis
- **Frontend Tests**: TypeScript/React tests with Vitest
- **Performance Tests**: Database and API performance benchmarks
- **Code Quality**: Black formatting and ESLint checks

## API Documentation

### Authentication
```bash
# Login
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "password"
}

# Get profile
GET /api/v1/auth/profile
Authorization: Bearer <token>
```

### Domains
```bash
# List domains
GET /api/v1/domains

# Create domain
POST /api/v1/domains
{
  "root_domain": "example.com",
  "subdomain": "sub.example.com",
  "source": "manual"
}

# Get domain
GET /api/v1/domains/{id}
```

### Chat
```bash
# Send message
POST /api/v1/chat/send
{
  "message": "Find subdomains for example.com",
  "conversation_id": "uuid"
}

# Get status
GET /api/v1/chat/status
```

## Configuration

### Environment Variables

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=postgresql://user:pass@localhost/bigshot

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# OpenAI (Optional)
OPENAI_API_KEY=your-openai-key
```

### Production Deployment

1. **Database Setup**
   ```bash
   # Create production database
   createdb bigshot_prod
   
   # Run migrations
   FLASK_ENV=production flask db upgrade
   ```

2. **Static Files**
   ```bash
   cd frontend
   npm run build
   ```

3. **Process Management**
   ```bash
   # Use supervisor or systemd for process management
   # Example supervisor config in docs/deployment.md
   ```

## Performance

### Benchmarks
- **API Response Time**: < 500ms for 95th percentile
- **Database Queries**: < 100ms average
- **Concurrent Users**: 50+ simultaneous connections
- **Memory Usage**: < 512MB typical usage

### Monitoring
- Built-in health checks at `/api/health`
- Performance metrics collection
- Error tracking and logging
- Resource usage monitoring

## Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   python -m pytest
   cd frontend && npm test
   ```
5. **Submit a pull request**

### Code Style
- **Python**: Black formatting, Flake8 linting
- **TypeScript**: ESLint with TypeScript rules
- **Commits**: Conventional commit format

## Documentation

- [API Documentation](docs/api.md)
- [Frontend Architecture](docs/frontend_architecture.md)
- [Database Schema](docs/database_schema.md)
- [Deployment Guide](docs/deployment.md)
- [Testing Guide](docs/testing.md)
- [CI/CD Pipeline](docs/cicd.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/thesavant42/bigshot/issues)
- **Documentation**: [Project Wiki](https://github.com/thesavant42/bigshot/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/thesavant42/bigshot/discussions)
