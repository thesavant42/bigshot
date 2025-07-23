import { expect, Page } from '@playwright/test';

/**
 * Utility to get config from args/env/defaults.
 * Returns { url, credentials } for use in tests.
 */
export function getConfig() {
  const argUrl = process.argv.find(arg => arg.startsWith('--test-url='))?.split('=')[1];
  const argUsername = process.argv.find(arg => arg.startsWith('--test-username='))?.split('=')[1];
  const argPassword = process.argv.find(arg => arg.startsWith('--test-password='))?.split('=')[1];
  return {
    url: argUrl || process.env.TEST_URL || 'http://192.168.1.98:3000/',
    credentials: {
      username: argUsername || process.env.TEST_USERNAME || 'admin',
      password: argPassword || process.env.TEST_PASSWORD || 'password'
    }
  };
}

/**
 * Modular authentication function for Playwright tests.
 * Navigates to login page and authenticates using provided credentials.
 */
export async function authenticate(
  page: Page,
  url: string,
  credentials: { username: string; password: string }
) {
  await page.goto(url);
  await page.getByRole('textbox', { name: 'Username' }).click();
  await page.getByRole('textbox', { name: 'Username' }).fill(credentials.username);
  await page.getByRole('textbox', { name: 'Password' }).click();
  await page.getByRole('textbox', { name: 'Password' }).fill(credentials.password);
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page.getByRole('textbox', { name: 'Search' })).toBeVisible();
}