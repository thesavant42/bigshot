# CI/CD Pipeline Guide

This document explains the continuous integration and deployment pipeline for the bigshot application.

## Pipeline Overview

The CI/CD pipeline is implemented using GitHub Actions and consists of several workflows:

### Main CI Pipeline (`.github/workflows/ci.yml`)
Triggered on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Release Pipeline (`.github/workflows/release.yml`)
Triggered on:
- Git tags matching `v*` pattern (e.g., `v1.0.0`)

## CI Pipeline Jobs

### 1. Backend Tests
- **Environment**: Ubuntu with Python 3.12
- **Services**: PostgreSQL 15, Redis 7
- **Steps**:
  - Install Python dependencies
  - Run code formatting checks (Black)
  - Run linting (Flake8)
  - Execute tests with coverage
  - Upload coverage reports to Codecov

### 2. Frontend Tests
- **Environment**: Ubuntu with Node.js 20
- **Steps**:
  - Install npm dependencies
  - Run ESLint for code quality
  - Execute TypeScript compilation check
  - Run Vitest tests with coverage
  - Build production bundle

### 3. Integration Tests
- **Dependencies**: Backend and frontend tests must pass
- **Environment**: Full stack with database and Redis
- **Steps**:
  - Build complete application
  - Run end-to-end integration tests
  - Verify component interactions

### 4. Security Scan
- **Tool**: Trivy vulnerability scanner
- **Scope**: File system and dependencies
- **Output**: SARIF format uploaded to GitHub Security

### 5. Performance Tests
- **Dependencies**: Backend tests must pass
- **Environment**: Database and Redis services
- **Steps**:
  - Run performance test suite
  - Validate response times
  - Check memory usage patterns

## Release Pipeline

### Automatic Release Creation
When a version tag is pushed:
1. **Build Assets**: Create production-ready application bundle
2. **Generate Changelog**: Auto-generate from commit history
3. **Create GitHub Release**: With changelog and assets
4. **Docker Image**: Build and publish to Docker Hub

### Release Artifacts
- **Source Archive**: Complete application source code
- **Built Frontend**: Production-optimized frontend bundle
- **Docker Image**: Container image with version tag
- **Documentation**: Updated API and user documentation

## Environment Configuration

### Test Environment Variables
```bash
FLASK_ENV=testing
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bigshot_test
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=test-secret-key
JWT_SECRET_KEY=test-jwt-secret
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Required Secrets
- `GITHUB_TOKEN`: Automatic GitHub token for releases
- `DOCKER_USERNAME`: Docker Hub username (optional)
- `DOCKER_PASSWORD`: Docker Hub password (optional)
- `CODECOV_TOKEN`: Codecov token for coverage reports (optional)

## Pipeline Optimization

### Caching Strategy
- **Python**: Cache pip dependencies based on requirements.txt
- **Node.js**: Cache npm dependencies based on package-lock.json
- **Docker**: Use GitHub Actions cache for Docker builds

### Parallel Execution
- Backend and frontend tests run in parallel
- Independent job execution for faster feedback
- Conditional job execution based on changes

## Quality Gates

### Code Quality
- **Backend**: Flake8 linting with E9, F63, F7, F82 checks
- **Frontend**: ESLint with TypeScript rules
- **Formatting**: Black for Python, Prettier for TypeScript

### Test Coverage
- **Backend**: Minimum 80% coverage required
- **Frontend**: Minimum 70% coverage required
- **Coverage Reports**: Uploaded to Codecov

### Performance Thresholds
- **API Response Time**: < 500ms for 95th percentile
- **Database Queries**: < 100ms average
- **Memory Usage**: < 10MB growth per 100 requests
- **Frontend Bundle**: < 500KB gzipped

## Deployment Strategy

### Staging Deployment
- Automatic deployment to staging on `develop` branch
- Full integration testing in staging environment
- User acceptance testing before production

### Production Deployment
- Manual approval required for production
- Blue-green deployment strategy
- Automated rollback on failure

## Monitoring and Alerts

### Pipeline Monitoring
- **Slack Notifications**: On build failures
- **Email Alerts**: On security vulnerabilities
- **Dashboard**: GitHub Actions status page

### Application Monitoring
- **Health Checks**: Automated endpoint monitoring
- **Performance Metrics**: Response time and throughput
- **Error Tracking**: Automated error reporting

## Troubleshooting

### Common Issues

#### Test Failures
```bash
# Local debugging
python -m pytest tests/ -v --tb=long

# Specific test debugging
python -m pytest tests/test_domains.py::TestDomains::test_create_domain -v
```

#### Build Failures
```bash
# Check formatting
python -m black --check app/ tests/

# Fix formatting
python -m black app/ tests/

# Check linting
python -m flake8 app/ tests/
```

#### Frontend Issues
```bash
# Type checking
npx tsc --noEmit

# Lint checking
npm run lint

# Test debugging
npm run test:ui
```

### Debug CI Issues
1. Check GitHub Actions logs
2. Run tests locally with same environment
3. Verify environment variables
4. Check service connectivity

## Best Practices

### Branch Strategy
- **Main**: Production-ready code
- **Develop**: Integration branch for features
- **Feature**: Short-lived branches for development

### Commit Messages
- Follow conventional commits format
- Include breaking change indicators
- Reference issue numbers

### Version Management
- Use semantic versioning (x.y.z)
- Tag releases consistently
- Maintain changelog

### Security
- Scan dependencies regularly
- Use secrets management
- Rotate tokens periodically
- Review security reports

## Pipeline Configuration

### Adding New Tests
1. Create test file in appropriate directory
2. Use proper test markers (`@pytest.mark.unit`)
3. Update coverage thresholds if needed
4. Document test purpose and requirements

### Modifying Pipeline
1. Update workflow files in `.github/workflows/`
2. Test changes in feature branch
3. Verify all jobs pass
4. Update documentation

### Environment Updates
1. Update service versions in workflow files
2. Update dependencies in requirements.txt/package.json
3. Test compatibility
4. Update documentation