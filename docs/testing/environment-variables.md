# Environment Variables in Tests

This document outlines the environment variables used in various test suites and how they are configured in the CI/CD pipeline.

## Current Environment Variable Usage

### Frontend Tests

#### ErrorBoundary Component Tests
- **Location**: `frontend/src/components/ErrorBoundary.test.tsx`
- **Variables Used**: `NODE_ENV`
- **Configuration**: Tests explicitly set and restore `process.env.NODE_ENV` within the test cases
- **CI Configuration**: `NODE_ENV=test` is set in the CI workflow for consistency

#### ErrorBoundary Component
- **Location**: `frontend/src/components/ErrorBoundary.tsx`
- **Variables Used**: `NODE_ENV`
- **Purpose**: Shows/hides error details based on development vs production mode
- **Configuration**: Reads from `process.env.NODE_ENV` (standard Node.js behavior)

#### Vite Configuration
- **Location**: `frontend/vite.config.ts`
- **Variables Used**: `VITE_API_URL`
- **Purpose**: Configures proxy target for API and WebSocket connections
- **Default**: Falls back to `http://localhost:5000` if not set

### Backend Tests

#### Test Environment Configuration
- **Location**: CI workflow creates `.env.test` file
- **Variables Set**:
  - `FLASK_ENV=testing`
  - `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bigshot_test`
  - `REDIS_URL=redis://localhost:6379/0`
  - `SECRET_KEY=test-secret-key`
  - `JWT_SECRET_KEY=test-jwt-secret`
  - `CELERY_BROKER_URL=redis://localhost:6379/0`
  - `CELERY_RESULT_BACKEND=redis://localhost:6379/0`

## Future UI Health Tests (Prepared Configuration)

The CI workflow includes a commented section ready for UI health tests using Playwright:

### Required Environment Variables for UI Health Tests

When UI health tests are implemented, the following variables will be needed:

- **`CI`**: Set to `true` to indicate CI environment
- **`TEST_USERNAME`**: Username for test authentication (stored as GitHub secret)
- **`TEST_PASSWORD`**: Password for test authentication (stored as GitHub secret)  
- **`PLAYWRIGHT_BASE_URL`**: Base URL for Playwright tests (typically `http://localhost:3000`)

### Enabling UI Health Tests

To enable UI health tests:

1. Uncomment the `ui-health-tests` job in `.github/workflows/ci.yml`
2. Add the necessary GitHub secrets:
   - `TEST_USERNAME`
   - `TEST_PASSWORD`
3. Install Playwright in the frontend project:
   ```bash
   cd frontend
   npm install --save-dev @playwright/test
   ```
4. Add the test:e2e script to `frontend/package.json`:
   ```json
   {
     "scripts": {
       "test:e2e": "playwright test"
     }
   }
   ```
5. Create the UI health test file at `frontend/tests/e2e/ui-health.spec.ts`

### Example UI Health Test Structure

```typescript
// frontend/tests/e2e/ui-health.spec.ts
import { test, expect } from '@playwright/test';

test.describe('UI Health Tests', () => {
  const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000';
  const testUsername = process.env.TEST_USERNAME;
  const testPassword = process.env.TEST_PASSWORD;
  const isCI = process.env.CI === 'true';

  test('application loads successfully', async ({ page }) => {
    await page.goto(baseUrl);
    await expect(page).toHaveTitle(/BigShot/);
  });

  test('login functionality works', async ({ page }) => {
    if (!testUsername || !testPassword) {
      test.skip(!isCI, 'Test credentials not available');
    }
    
    await page.goto(`${baseUrl}/login`);
    await page.fill('[data-testid="username"]', testUsername);
    await page.fill('[data-testid="password"]', testPassword);
    await page.click('[data-testid="login-button"]');
    
    await expect(page).toHaveURL(/dashboard/);
  });
});
```

## Best Practices

1. **Environment Variable Handling in Tests**:
   - Set and restore environment variables within test cases when possible
   - Use GitHub secrets for sensitive test data
   - Provide sensible defaults for development environments

2. **CI Configuration**:
   - Explicitly set all required environment variables in CI workflow steps
   - Use job-level or step-level `env` blocks rather than relying on inheritance
   - Document any new environment variables in this file

3. **Security**:
   - Never commit real credentials to the repository
   - Use GitHub secrets for sensitive environment variables
   - Ensure test credentials have minimal permissions

## Troubleshooting

### Common Issues

1. **"Environment variable ... is not set" errors**:
   - Check that the variable is defined in the CI workflow step
   - Verify GitHub secrets are properly configured
   - Ensure the variable name matches exactly (case-sensitive)

2. **Tests pass locally but fail in CI**:
   - Check that all local environment variables are also set in CI
   - Verify that CI environment has access to required services
   - Review CI logs for missing dependencies or configuration

3. **NODE_ENV related issues**:
   - ErrorBoundary tests handle NODE_ENV internally and should not fail
   - If adding new environment-dependent behavior, ensure tests set appropriate values
   - Remember that NODE_ENV in CI is typically set to 'test' or 'ci'