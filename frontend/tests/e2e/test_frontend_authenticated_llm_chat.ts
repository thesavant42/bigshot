import { test } from '@playwright/test';
// Import helper functions for authentication
import { getConfig, authenticate } from './authenticationHelper';


test('frontend_authenticated_llm_settings', async ({ page }) => {
  const { url, credentials } = getConfig();
  await authenticate(page, url, credentials);
 /// Everything below this point requires authentication
  

  // Test Chat button Adk about domain"
  await page.getByRole('textbox', { name: 'Ask about domains, start' }).click();

  // Fill in the chat input
  await page.getByRole('textbox', { name: 'Ask about domains, start' }).fill('hello');

});