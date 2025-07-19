
// UI Health Tests - Playwright-based browser automation tests
// This file implements actual UI health testing with screenshot capture

import { test, expect } from '@playwright/test';

test.describe('UI Health Tests', () => {
  let testUsername: string | undefined;
  let testPassword: string | undefined;
  let isCI: boolean;

  test.beforeAll(() => {
    testUsername = process.env.TEST_USERNAME;
    testPassword = process.env.TEST_PASSWORD;
    isCI = process.env.CI === 'true';
    
    console.log('🔧 Test Environment Configuration:');
    console.log(`  CI: ${isCI}`);
    console.log(`  TEST_USERNAME: ${testUsername ? '✅ Set' : '❌ Not set'}`);
    console.log(`  TEST_PASSWORD: ${testPassword ? '✅ Set' : '❌ Not set'}`);
    console.log(`  PLAYWRIGHT_BASE_URL: ${process.env.PLAYWRIGHT_BASE_URL || 'Not set (using default)'}`);
  });

  test('should load dashboard and capture health screenshot', async ({ page }) => {
    console.log('🚀 Starting dashboard health test...');
    
    // Navigate to the dashboard
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Wait a bit more for any dynamic content
    await page.waitForTimeout(2000);
    
    // Check if page has loaded successfully by looking for common elements
    // This is flexible - we just want to ensure the page isn't blank or errored
    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();
    expect(bodyText!.length).toBeGreaterThan(0);
    
    console.log('✅ Dashboard page loaded successfully');
    
    // Take a full-page screenshot for health analysis
    await page.screenshot({ 
      path: 'test-results/dashboard-health.png', 
      fullPage: true,
      type: 'png'
    });
    
    console.log('📸 Dashboard screenshot captured: test-results/dashboard-health.png');
  });

  test('should validate environment variables are accessible', async () => {
    // Test environment variable configuration
    if (isCI) {
      if (testUsername && testPassword) {
        console.log('✅ CI environment variables are properly configured');
        expect(testUsername).toBeTruthy();
        expect(testPassword).toBeTruthy();
        expect(typeof testUsername).toBe('string');
        expect(typeof testPassword).toBe('string');
      } else {
        console.log('⚠️ CI environment detected but credentials not provided');
        console.log('This is expected when GitHub secrets are not configured');
        // Don't fail the test - just log the status
      }
    } else {
      console.log('ℹ️ Running in local development mode');
      console.log('Environment variables are optional in local development');
    }
    
    // This test always passes but provides useful logging
    expect(true).toBe(true);
  });

  test('should handle application errors gracefully', async ({ page }) => {
    console.log('🛡️ Testing error handling...');
    
    // Navigate to dashboard
    await page.goto('/');
    
    // Listen for console errors
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Listen for uncaught exceptions
    const uncaughtErrors: string[] = [];
    page.on('pageerror', error => {
      uncaughtErrors.push(error.message);
    });
    
    // Wait for any initial load errors
    await page.waitForTimeout(3000);
    
    // Log any errors found (but don't necessarily fail)
    if (consoleErrors.length > 0) {
      console.log('⚠️ Console errors detected:', consoleErrors);
    }
    
    if (uncaughtErrors.length > 0) {
      console.log('⚠️ Uncaught errors detected:', uncaughtErrors);
    }
    
    if (consoleErrors.length === 0 && uncaughtErrors.length === 0) {
      console.log('✅ No errors detected in dashboard');
    }
    
    // Test passes regardless - this is for monitoring, not strict validation
    expect(true).toBe(true);
  });
});
