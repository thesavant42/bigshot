# UI Health Testing

This directory contains automated UI health tests for the BigShot application using Playwright.

## Overview

The UI health tests verify that:
1. The application login flow works correctly
2. Post-authentication verification screen can be navigated
3. The main dashboard loads properly with expected elements
4. Screenshots can be captured and validated for health

## Test Structure

- `ui-health.spec.ts` - Main UI health test suite
- Validates login with default credentials (`admin`/`password`)
- Handles post-auth verification screen flow
- Takes full-page screenshots for visual validation
- Analyzes screenshot size to detect blank/corrupted captures

## Running Tests Locally

### Prerequisites
- Node.js 18+ 
- Docker and Docker Compose
- Application services running (backend, frontend, database, redis)

### Quick Start
```bash
# From the project root
./test-ui-local.sh
```

### Manual Steps
```bash
# Start application services
docker-compose -f docker-compose.test.yml up -d

# Install dependencies
cd frontend
npm ci

# Install Playwright browsers
npx playwright install chromium

# Run tests
npm run test:e2e

# Clean up
cd ..
docker-compose -f docker-compose.test.yml down -v
```

## CI/CD Integration

The tests are automatically run in the GitHub Actions CI pipeline as part of the `ui-health-tests` job:

1. Spins up full application stack using Docker Compose
2. Waits for all services to be healthy
3. Runs Playwright tests against the live application
4. Validates screenshot health and size
5. Uploads test results and screenshots as artifacts
6. Fails the pipeline if dashboard is not accessible or screenshots are blank

## Test Configuration

Key configurations in `playwright.config.ts`:
- Base URL: `http://localhost:80` (configurable via `PLAYWRIGHT_BASE_URL`)
- Browser: Chromium (headless in CI)
- Timeout: 120 seconds per test
- Retries: 2 attempts in CI
- Screenshots: On failure + full-page dashboard capture
- Video: On failure for debugging

## Expected Dashboard Elements

The test validates presence of key UI elements:
- **Primary Elements**: BigShot title, Domain Reconnaissance Platform text
- **Alternative Elements**: Domain Dashboard, Chat Interface, Navigation menus

## Screenshot Validation

Screenshots are analyzed for health:
- **Healthy**: File size > 30KB (indicates actual content)
- **Unhealthy**: File size < 30KB (likely blank/corrupted)
- Full-page screenshots saved as `test-results/dashboard-health.png`
- Failure screenshots saved as `test-results/dashboard-failure.png`

## Troubleshooting

### Common Issues

**Test timeout/login fails:**
- Check that backend is healthy: `curl http://localhost:5000/api/v1/health`
- Verify default user exists in database
- Check container logs: `docker-compose -f docker-compose.test.yml logs`

**Screenshot too small:**
- Application may not be fully loaded
- Check for JavaScript errors in browser console
- Verify all required services are healthy
- Review failure screenshot and page debug HTML

**Services won't start:**
- Check port availability (80, 5000, 5432, 6379)
- Verify Docker and Docker Compose versions
- Check available disk space and memory

### Debug Mode

Run tests in headed mode for debugging:
```bash
npm run test:e2e:headed
```

View test report:
```bash
npx playwright show-report
```

## Artifacts

In CI, the following artifacts are preserved:
- `ui-test-results/` - Full Playwright test results
- `playwright-report/` - HTML test report
- `ui-screenshots/` - Dashboard and failure screenshots

Artifacts are retained for 30 days and can be downloaded from the GitHub Actions run page.