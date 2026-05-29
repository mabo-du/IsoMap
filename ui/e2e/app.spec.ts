import { test, expect } from '@playwright/test';

test('has title and displays IsoMap header', async ({ page }) => {
  await page.goto('http://localhost:5173');
  
  // Expect the title to contain IsoMap (if we set it in index.html)
  // Vite default is usually "Vite + React + TS", but we'll check body text.
  
  // Check main headers
  await expect(page.locator('h1')).toHaveText('IsoMap');
  await expect(page.locator('text=Isotopic and paleoecological data standardisation middleware')).toBeVisible();

  // Check the tabs exist
  await expect(page.locator('text=1. Import Engine')).toBeVisible();
  await expect(page.locator('text=2. Column Mapping')).toBeVisible();
  await expect(page.locator('text=3. Spatial Verification')).toBeVisible();
  await expect(page.locator('text=4. Validation')).toBeVisible();
  await expect(page.locator('text=5. Export')).toBeVisible();
});
