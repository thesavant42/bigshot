import { test } from '@playwright/test';
// Import helper functions for authentication
import { getConfig, authenticate } from './authenticationHelper';


test('frontend_authenticated_llm_settings', async ({ page }) => {
  const { url, credentials } = getConfig();
  await authenticate(page, url, credentials);
 /// Everything below this point requires authentication
  

  // Test Chat button Adk about domain"
  await page.getByRole('textbox', { name: 'Ask about domains, start' }).click();

 // // Fill in the chat input
 // await page.getByRole('textbox', { name: 'Ask about domains, start' }).fill('hello');


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