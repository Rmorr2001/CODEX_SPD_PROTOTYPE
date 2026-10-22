import { expect, type Page } from '@playwright/test';

/** Enter an actual seeded account through the existing CSRF-protected demo form. */
export async function enterDemo(page: Page, persona = 'active') {
  await page.goto('/app/login');
  await page.getByLabel('Explore as').selectOption(persona);
  await page.getByRole('button', { name: 'Enter demo', exact: true }).click();
  await expect(page).toHaveURL(/\/app\/(dashboard|new-members)$/);
}
