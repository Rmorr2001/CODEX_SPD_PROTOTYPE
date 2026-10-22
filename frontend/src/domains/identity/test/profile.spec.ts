import { expect, test } from '@playwright/test';
import { enterDemo } from './helpers';

test('profile displays the actual caller and opens the functioning original edit page', async ({
  page,
}) => {
  await enterDemo(page, 'executive');
  const profile = await (await page.request.get('/api/v1/profile/')).json();
  await page
    .getByRole('navigation', { name: 'Member navigation' })
    .getByRole('link', { name: 'Profile', exact: true })
    .click();
  await expect(page).toHaveURL(/\/app\/profile$/);
  await expect(page.getByRole('heading', { name: 'Your profile.' })).toBeVisible();
  await expect(page.locator('.profile-fields')).toContainText(profile.username);
  await expect(page.locator('.profile-fields')).toContainText(profile.email);
  await expect(page.locator('.profile-identity h2')).toHaveText(profile.display_name);
  await expect(page.locator('main input')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Save changes', exact: true })).toHaveCount(0);
  await page.reload();
  await expect(page.locator('.profile-fields')).toContainText(profile.username);
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
  await expect(
    page.getByRole('link', { name: 'Edit in chapter site', exact: true }),
  ).toHaveAttribute('href', '/auth/profile/');
  await page.getByRole('link', { name: 'Edit in chapter site', exact: true }).click();
  await expect(page).toHaveURL(/\/auth\/profile\/$/);
  await expect(page.locator('input[name="username"]')).toHaveValue(profile.username);
});

test('profile handles a denied read without showing personal fields', async ({ page }) => {
  await enterDemo(page);
  await page.route('**/api/v1/profile/', (route) => route.fulfill({ status: 403, json: {} }));
  await page.goto('/app/profile');
  await expect(page.getByRole('alert')).toHaveText(
    'Your profile is unavailable. Sign in again to continue.',
  );
  await expect(page.locator('.profile-fields')).toHaveCount(0);
});

test('profile read failure retries against real data and falls back for missing images', async ({
  page,
}) => {
  await enterDemo(page);
  await page.route('**/api/v1/profile/', (route) => route.fulfill({ status: 503, json: {} }));
  await page.goto('/app/profile');
  await expect(page.getByRole('alert')).toHaveText(
    'We couldn’t load your profile. Please try again.',
  );
  await page.unroute('**/api/v1/profile/');
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.locator('.profile-identity .member-avatar span')).toBeVisible();
  await expect(page.locator('.profile-fields')).toBeVisible();
});
