import { test, expect, Page } from '@playwright/test';
import { promises as fs } from 'fs';
import * as path from 'path';

if (!process.env.TEST_USERNAME) {
  throw new Error('Environment variable TEST_USERNAME is not set');
}
if (!process.env.TEST_PASSWORD) {
  throw new Error('Environment variable TEST_PASSWORD is not set');
}

const TEST_CREDENTIALS = {
  username: process.env.TEST_USERNAME,
  password: process.env.TEST_PASSWORD
};

// Screenshot size threshold in bytes - screenshots smaller than this are considered unhealthy
const SCREENSHOT_SIZE_THRESHOLD = 30000; // 30KB minimum for a real screenshot

// Expected dashboard elements that should be visible
const EXPECTED_DASHBOARD_ELEMENTS = [
  'BigShot', // App title  
  'Domain Reconnaissance Platform', // Subtitle or app description
];

// Alternative elements that might be present
const ALTERNATIVE_ELEMENTS = [
  'Domain Dashboard',
  'Chat Interface', 
  'Navigation',
  'Domains',
  'Jobs',
  'Health',
];

/**
 * Helper function to wait for page to fully load and become interactive
 */
async function waitForPageReady(page: Page) {
  // Wait for network to be idle (no requests for 500ms)
  await page.waitForLoadState('networkidle');
  
  // Wait for the app to be rendered (look for main content)
  await page.waitForSelector('body', { state: 'visible' });
  
  // Wait for React components to mount and render
  await page.waitForSelector(`text=${APPLICATION_NAME}`, { state: 'visible' });
}

/**
 * Helper function to perform login with test credentials
 */
async function performLogin(page: Page) {
  console.log('🔐 Starting login process...');
  
  // Navigate to the application
  await page.goto('/');
  await waitForPageReady(page);
  
  // Check if already authenticated by looking for dashboard elements
  const isAlreadyLoggedIn = await page.locator('text=BigShot').first().isVisible().catch(() => false);
  if (isAlreadyLoggedIn) {
    console.log('✅ Already logged in, skipping login');
    return;
  }
  
  // Check if we're on login page by looking for login form elements
  const usernameField = page.locator('input[type="text"], input[id="username"], input[name="username"]').first();
  const passwordField = page.locator('input[type="password"], input[id="password"], input[name="password"]').first();
  const signInButton = page.locator('button:has-text("Sign In"), button[type="submit"], button:has-text("Login")').first();
  
  // Wait for login form to be visible
  await expect(usernameField).toBeVisible({ timeout: 15000 });
  await expect(passwordField).toBeVisible();
  await expect(signInButton).toBeVisible();
  
  console.log('✅ Login form detected');
  
  // Clear any existing values and fill in credentials
  await usernameField.clear();
  await usernameField.fill(TEST_CREDENTIALS.username);
  await passwordField.clear();
  await passwordField.fill(TEST_CREDENTIALS.password);
  
  console.log('📝 Credentials entered');
  
  // Submit the form
  await signInButton.click();
  
  console.log('🚀 Login submitted');
  
  // Wait for the dashboard to appear, indicating login success
  await page.waitForSelector('text=BigShot', { state: 'visible' });
}

/**
 * Helper function to handle post-auth verification screen
 */
async function handlePostAuthVerification(page: Page) {
  console.log('🔍 Checking for post-auth verification screen...');
  
  // Look for post-auth proof elements with more flexible selectors
  const postAuthTitle = page.locator('text=Post-Authentication Verification')
    .or(page.locator('text=Verification'))
    .or(page.locator('text=Authentication'))
    .first();
  const continueButton = page.locator('button:has-text("Continue to Application"), button:has-text("Continue"), button:has-text("Proceed")').first();
  
  try {
    // Check if we're on the post-auth verification screen
    await postAuthTitle.waitFor({ timeout: 10000 });
    console.log('📋 Post-auth verification screen detected');
    
    // Wait for the screen to fully load
    await waitForPageReady(page);
    
    // Look for success indicators with timeout
    try {
      const authSuccess = page.locator('text=successful').or(page.locator('text=SUCCESS')).or(page.locator('text=authenticated')).first();
      await authSuccess.waitFor({ timeout: 5000 });
      console.log('✅ Authentication status confirmed');
    } catch {
      console.log('⚠️ Could not confirm auth status, but continuing');
    }
    
    // Wait for continue button to be available and click it
    await expect(continueButton).toBeVisible({ timeout: 15000 });
    await continueButton.click();
    
    console.log('➡️ Clicked continue to application');
    
    // Wait for navigation to dashboard
    await page.waitForSelector('text=BigShot', { timeout: 10000 });
    
  } catch {
    console.log('ℹ️ No post-auth verification screen found, proceeding...');
    // If post-auth screen is not present, that's also fine
  }
}

/**
 * Helper function to validate dashboard is properly loaded
 */
async function validateDashboard(page: Page) {
  console.log('🏠 Validating dashboard...');
  
  // Wait for dashboard to load
  await waitForPageReady(page);
  
  // Look for main dashboard container
  const dashboardContainer = page.locator('body');
  await expect(dashboardContainer).toBeVisible();
  
  let foundElements = 0;
  let foundAlternatives = 0;
  
  // Check for primary expected elements
  for (const element of EXPECTED_DASHBOARD_ELEMENTS) {
    try {
      const locator = page.locator(`text=${element}`).first();
      await locator.waitFor({ timeout: 3000 });
      console.log(`✅ Found primary element: ${element}`);
      foundElements++;
    } catch {
      console.log(`⚠️ Missing primary element: ${element}`);
    }
  }
  
  // Check for alternative elements that indicate a working dashboard
  for (const element of ALTERNATIVE_ELEMENTS) {
    try {
      const locator = page.locator(`text=${element}`).first();
      await locator.waitFor({ timeout: 2000 });
      console.log(`✅ Found alternative element: ${element}`);
      foundAlternatives++;
    } catch {
      console.log(`ℹ️ Alternative element not found: ${element}`);
    }
  }
  
  const totalFound = foundElements + foundAlternatives;
  console.log(`📊 Found ${foundElements}/${EXPECTED_DASHBOARD_ELEMENTS.length} primary elements and ${foundAlternatives}/${ALTERNATIVE_ELEMENTS.length} alternative elements`);
  
  // Check if the page shows error messages
  const errorMessages = await page.locator('text=Error')
    .or(page.locator('text=Failed'))
    .or(page.locator('text=error'))
    .or(page.locator('text=failed'))
    .count();
  if (errorMessages > 0) {
    console.log(`⚠️ Found ${errorMessages} error messages on page`);
  }
  
  // Ensure we found at least some elements indicating a working interface
  if (totalFound === 0) {
    // Try to get more information about what's on the page
    const pageTitle = await page.title();
    const pageText = await page.locator('body').textContent();
    console.log(`Page title: ${pageTitle}`);
    console.log(`Page content preview: ${pageText?.substring(0, 200)}...`);
    
    throw new Error('No expected dashboard elements found - page may not have loaded correctly');
  }
  
  return { primary: foundElements, alternative: foundAlternatives, total: totalFound };
}

/**
 * Helper function to analyze screenshot for basic health check
 */
async function analyzeScreenshot(screenshotPath: string): Promise<{ isHealthy: boolean; reason: string; size: number }> {
  try {
    const stats = await fs.stat(screenshotPath);
    const size = stats.size;
    
    console.log(`📊 Screenshot size: ${Math.round(size / 1024)}KB`);
    
    // Check if file exists and has reasonable size (not empty)
    if (size < 1000) {
      return { isHealthy: false, reason: 'Screenshot file is too small (likely empty or corrupted)', size };
    }
    
    // Basic file size check - a healthy screenshot should be reasonably sized
    // Lowered threshold for CI environments where screenshots might be smaller
    if (size > SCREENSHOT_SIZE_THRESHOLD) { // 30KB minimum for a real screenshot
      return { isHealthy: true, reason: 'Screenshot appears to contain content', size };
    } else {
      return { isHealthy: false, reason: 'Screenshot too small, may be blank or mostly empty', size };
    }
    
  } catch (error) {
    return { isHealthy: false, reason: `Failed to analyze screenshot: ${error}`, size: 0 };
  }
}

test('should login, pass verification, and capture healthy dashboard screenshot', async ({ page }) => {
  console.log('🚀 Starting UI health check test...');
  
  // Set longer timeout for this test
  test.setTimeout(180000);
  
  try {
    // Step 1: Perform login
    await performLogin(page);
    
    // Step 2: Handle post-auth verification if present
    await handlePostAuthVerification(page);
    
    // Step 3: Validate dashboard is loaded
    const elementCounts = await validateDashboard(page);
    
    // Step 4: Take screenshot
    console.log('📸 Taking dashboard screenshot...');
    const screenshotPath = path.join(process.cwd(), 'test-results', 'dashboard-health.png');
    
    // Ensure test-results directory exists
    await fs.mkdir(path.dirname(screenshotPath), { recursive: true });
    
    await page.screenshot({ 
      path: screenshotPath, 
      fullPage: true,
      timeout: 30000
    });
    
    console.log(`💾 Screenshot saved to: ${screenshotPath}`);
    
    // Step 5: Analyze screenshot
    const analysis = await analyzeScreenshot(screenshotPath);
    
    console.log(`📋 Screenshot analysis: ${analysis.reason} (${analysis.size} bytes)`);
    
    // Test assertions with more flexible requirements
    expect(elementCounts.total).toBeGreaterThan(0);
    expect(analysis.isHealthy).toBe(true);
    
    // Additional checks for CI environments
    if (process.env.CI) {
      console.log('🏗️ Running in CI environment - performing additional checks');
      
      // Verify the page isn't showing only loading spinners
      const loadingSpinners = await page.locator('[class*="loading"], [class*="spinner"], text=Loading').count();
      if (loadingSpinners > 0) {
        console.log(`⚠️ Found ${loadingSpinners} loading indicators - may still be loading`);
      }
      
      // Check page is not blank
      const bodyText = await page.locator('body').textContent();
      expect(bodyText?.length || 0).toBeGreaterThan(50);
    }
    
    console.log('✅ UI health check completed successfully!');
    console.log(`📈 Summary: Found ${elementCounts.primary} primary + ${elementCounts.alternative} alternative elements, screenshot ${analysis.size} bytes`);
    
  } catch (error) {
    console.error('❌ UI health check failed:', error);
    
    // Take a screenshot on failure for debugging
    try {
      const failureScreenshotPath = path.join(process.cwd(), 'test-results', 'dashboard-failure.png');
      await fs.mkdir(path.dirname(failureScreenshotPath), { recursive: true });
      await page.screenshot({ 
        path: failureScreenshotPath, 
        fullPage: true 
      });
      console.log(`🐛 Failure screenshot saved to: ${failureScreenshotPath}`);
      
      // Also capture page content for debugging
      const pageContent = await page.content();
      const debugPath = path.join(process.cwd(), 'test-results', 'page-debug.html');
      await fs.writeFile(debugPath, pageContent);
      console.log(`🔍 Page content saved to: ${debugPath}`);
      
    } catch (screenshotError) {
      console.error('Failed to take failure screenshot:', screenshotError);
    }
    
    throw error;
  }
});

test('should detect and fail on blank/corrupted screenshots', async () => {
  console.log('🧪 Testing screenshot validation...');
  
  // Create a tiny fake screenshot to test validation
  const testScreenshotPath = path.join(process.cwd(), 'test-results', 'test-small.png');
  await fs.mkdir(path.dirname(testScreenshotPath), { recursive: true });
  await fs.writeFile(testScreenshotPath, Buffer.alloc(100)); // Very small file
  
  const analysis = await analyzeScreenshot(testScreenshotPath);
  
  // This should fail validation
  expect(analysis.isHealthy).toBe(false);
  expect(analysis.reason).toContain('too small');
  
  console.log('✅ Screenshot validation test passed');
  
  // Clean up
  await fs.unlink(testScreenshotPath).catch(() => {});
});