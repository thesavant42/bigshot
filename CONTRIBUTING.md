# Contributing to BigShot

We love your input! We want to make contributing to BigShot as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Request Process

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

### Branch Naming

- `feature/description` - for new features
- `bugfix/description` - for bug fixes
- `hotfix/description` - for urgent fixes
- `docs/description` - for documentation updates

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add two-factor authentication
fix(api): resolve domain enumeration timeout
docs(readme): update installation instructions
```

## Code Style

### Python (Backend)

- Follow PEP 8 style guide
- Use Black for code formatting
- Use Flake8 for linting
- Maximum line length: 88 characters
- Use type hints where appropriate

#### Code Formatting
```bash
# Format code
black app/ tests/

# Check formatting
black --check app/ tests/

# Lint code
flake8 app/ tests/
```

### TypeScript/React (Frontend)

- Follow ESLint configuration
- Use Prettier for code formatting
- Use TypeScript for type safety
- Follow React best practices

#### Code Formatting
```bash
cd frontend

# Format code
npm run format

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix
```

### General Guidelines

- Write clear, readable code
- Add comments for complex logic
- Keep functions small and focused
- Use descriptive variable names
- Follow existing patterns in the codebase

## Testing

### Backend Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_domains.py

# Run with coverage
python -m pytest --cov=app

# Run performance tests
python -m pytest -m performance
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run specific test file
npm test -- ChatInterface.test.tsx

# Run with coverage
npm run test:coverage
```

### Test Guidelines

- Write tests for new features
- Update tests when changing existing code
- Aim for high test coverage (>80%)
- Use descriptive test names
- Follow arrange-act-assert pattern

## Documentation

### API Documentation

- Document all API endpoints
- Include request/response examples
- Update OpenAPI/Swagger specs
- Add authentication requirements

### Code Documentation

- Add docstrings to Python functions
- Add JSDoc comments to TypeScript functions
- Document complex algorithms
- Update README for new features

### User Documentation

- Update user guide for new features
- Add screenshots for UI changes
- Update installation instructions
- Add troubleshooting information

## Issue Guidelines

### Bug Reports

Please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment information (OS, browser, version)
- Screenshots if applicable
- Error messages or logs

### Feature Requests

Please include:
- Clear description of the feature
- Use case and motivation
- Possible implementation approach
- Any relevant examples or references

### Issue Labels

- `bug`: Something isn't working
- `feature`: New feature request
- `enhancement`: Improvement to existing feature
- `documentation`: Documentation improvement
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/thesavant42/bigshot.git
   cd bigshot
   ```

2. **Backend setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Database setup**
   ```bash
   # Create database
   createdb bigshot_dev
   
   # Run migrations
   flask db upgrade
   ```

5. **Environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running the Application

```bash
# Start backend
python run.py

# Start frontend (in another terminal)
cd frontend
npm run dev

# Start Celery worker (in another terminal)
celery -A celery_app worker --loglevel=info

# Start Redis
redis-server
```

## Performance Guidelines

### Backend Performance

- Use database indexing appropriately
- Implement caching where beneficial
- Use async operations for I/O
- Monitor query performance
- Optimize database queries

### Frontend Performance

- Use React.memo for expensive components
- Implement lazy loading
- Optimize bundle size
- Use proper state management
- Minimize re-renders

## Security Guidelines

### General Security

- Never commit secrets to version control
- Use environment variables for configuration
- Validate all inputs
- Implement proper authentication
- Use HTTPS in production

### Backend Security

- Validate and sanitize all inputs
- Use parameterized queries
- Implement rate limiting
- Use secure session management
- Follow OWASP guidelines

### Frontend Security

- Sanitize user inputs
- Use Content Security Policy
- Implement CSRF protection
- Validate API responses
- Use secure cookies

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Steps

1. Update version numbers
2. Update CHANGELOG.md
3. Create release tag
4. GitHub Actions handles the rest

### Changelog

We maintain a changelog following [Keep a Changelog](https://keepachangelog.com/) format:
- Added: New features
- Changed: Changes to existing features
- Deprecated: Features to be removed
- Removed: Removed features
- Fixed: Bug fixes
- Security: Security improvements

## Community

### Getting Help

- Check existing documentation
- Search existing issues
- Ask questions in GitHub Discussions
- Join our community chat

### Contributing Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Annual contributor highlights
- Community showcases

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Don't hesitate to reach out if you have questions about contributing:
- Create an issue for general questions
- Use GitHub Discussions for community help
- Contact maintainers directly for sensitive issues

Thank you for contributing to BigShot! 🚀