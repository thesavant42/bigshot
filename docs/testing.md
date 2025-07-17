# Testing Guide

This document provides comprehensive guidance on testing the bigshot application.

## Test Structure

The application follows a multi-layered testing approach:

### Backend Tests (`tests/`)
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Performance Tests**: Test system performance and scalability
- **API Tests**: Test REST API endpoints

### Frontend Tests (`frontend/src/`)
- **Component Tests**: Test React components
- **Hook Tests**: Test custom React hooks
- **Service Tests**: Test API service functions
- **Integration Tests**: Test component interactions

## Running Tests

### Backend Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test categories
python -m pytest -m "unit"
python -m pytest -m "integration"
python -m pytest -m "performance"

# Run tests in parallel
python -m pytest -n auto

# Run tests with verbose output
python -m pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui
```

## Test Configuration

### Backend (`pytest.ini`)
- Coverage threshold: 80%
- Test markers for categorization
- Environment variables for testing
- Warning filters for clean output

### Frontend (`vitest.config.ts`)
- jsdom environment for DOM testing
- Coverage reporting
- Test setup files

## Writing Tests

### Backend Test Example

```python
import pytest
from app import create_app
from app.models.models import Domain, db

class TestDomains:
    def test_create_domain(self, app, client):
        """Test domain creation."""
        with app.app_context():
            response = client.post('/api/domains', json={
                'name': 'test.com',
                'description': 'Test domain'
            })
            assert response.status_code == 201
            assert Domain.query.count() == 1
```

### Frontend Test Example

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import MyComponent from './MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(
      <BrowserRouter>
        <MyComponent />
      </BrowserRouter>
    )
    expect(screen.getByText('Hello World')).toBeInTheDocument()
  })
})
```

## Test Data Management

### Database Tests
- Use test database: `bigshot_test`
- Automatic cleanup after each test
- Fixtures for common test data

### Mock Data
- Mock external API calls
- Use test doubles for dependencies
- Isolation between tests

## Performance Testing

### Backend Performance Tests
- Response time validation
- Concurrent request handling
- Database query performance
- Memory usage monitoring

### Frontend Performance Tests
- Component render time
- Bundle size validation
- Memory leak detection

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Push to main/develop branches
- Release tags

### CI Pipeline Steps
1. Backend tests with coverage
2. Frontend tests with coverage
3. Integration tests
4. Performance tests
5. Security scanning

## Test Best Practices

### General
- Write descriptive test names
- Use arrange-act-assert pattern
- Test both success and failure cases
- Keep tests independent and isolated

### Backend
- Use pytest fixtures for setup
- Mock external dependencies
- Test edge cases and error conditions
- Use database transactions for cleanup

### Frontend
- Use React Testing Library
- Test user interactions, not implementation
- Mock HTTP requests
- Test accessibility features

## Debugging Tests

### Backend
```bash
# Run with pdb debugger
python -m pytest --pdb

# Run single test
python -m pytest tests/test_domains.py::TestDomains::test_create_domain

# Show full traceback
python -m pytest --tb=long
```

### Frontend
```bash
# Run with browser UI
npm run test:ui

# Debug specific test
npm test -- --reporter=verbose MyComponent.test.tsx
```

## Coverage Requirements

- **Backend**: Minimum 80% coverage
- **Frontend**: Minimum 70% coverage
- **Critical paths**: 100% coverage required

## Test Automation

### Pre-commit Hooks
- Run linting before commits
- Run quick tests on changed files
- Format code automatically

### GitHub Actions
- Full test suite on CI
- Coverage reporting
- Performance regression detection

## Performance Benchmarks

### Backend
- API response time: < 500ms
- Database queries: < 100ms
- Concurrent requests: 50+ simultaneous
- Memory usage: < 10MB growth per 100 requests

### Frontend
- Component render: < 50ms
- Bundle size: < 500KB gzipped
- First contentful paint: < 2s
- Time to interactive: < 3s