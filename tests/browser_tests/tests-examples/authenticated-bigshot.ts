import { test, expect } from '@playwright/test';


// Read the URL from environment variables with defaults

// Accept TEST_URL from process.env, command-line arg, or default
const argUrl = process.argv.find(arg => arg.startsWith('--test-url='))?.split('=')[1];
const TEST_URL = argUrl || process.env.TEST_URL || 'http://192.168.1.98:3000/';
// Default credentials for testing, can be overridden by environment variables

// Accept TEST_USERNAME and TEST_PASSWORD from command-line args, env vars, or defaults
const argUsername = process.argv.find(arg => arg.startsWith('--test-username='))?.split('=')[1];
const argPassword = process.argv.find(arg => arg.startsWith('--test-password='))?.split('=')[1];

const TEST_CREDENTIALS = {
  username: argUsername || process.env.TEST_USERNAME || 'admin',
  password: argPassword || process.env.TEST_PASSWORD || 'password'
};

test('authenticated_bigshot', async ({ page }) => {
  await page.goto(TEST_URL);
  await page.getByRole('textbox', { name: 'Username' }).click();
  await page.getByRole('textbox', { name: 'Username' }).fill(TEST_CREDENTIALS.username);
  await page.getByRole('textbox', { name: 'Password' }).click();
  await page.getByRole('textbox', { name: 'Password' }).fill(TEST_CREDENTIALS.password);
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page.getByRole('textbox', { name: 'Search' })).toBeVisible();
  // Authenticated.
  
  /// Everything below this point requires authentication
  
  // Test Chat button Adk about domain"
  await page.getByRole('textbox', { name: 'Ask about domains, start' }).click();

  // Fill in the chat input
  await page.getByRole('textbox', { name: 'Ask about domains, start' }).fill('hello');
  await page.locator('form').getByRole('button').click();

  // Click Settings Hamburger button 
  await page.getByRole('button', { name: 'Open sidebar' }).click();
  await page.getByRole('button', { name: 'Close sidebar' }).click();
  
  // Example changing from settings page
  
  // Click setting sidebar button
  await page.getByRole('button', { name: 'Settings' }).nth(1).click();
  
  // Make a change to currently loaded model
  
  //  Open Question: does this form get submitted?
  await page.locator('div').filter({ hasText: /^Max Tokens: 10001004000$/ }).getByRole('slider').fill('4000');
  await page.getByRole('button', { name: 'Settings' }).nth(1).click();
  await page.getByRole('button', { name: 'View Jobs' }).click();
});