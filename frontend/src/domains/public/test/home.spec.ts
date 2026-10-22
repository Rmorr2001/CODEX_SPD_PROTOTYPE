import { expect, test } from '@playwright/test';

test('home presents chapter content from the real public API without invented events', async ({
  page,
  request,
}) => {
  const response = await request.get('/api/v1/public/home/');
  expect(response.status()).toBe(200);
  expect(Object.keys(await response.json()).sort()).toEqual(['banner_image', 'rush_interest_url']);
  await page.goto('/app/');
  await expect(
    page.getByRole('heading', { name: 'Engineering a stronger brotherhood.' }),
  ).toBeVisible();
  await expect(
    page.getByRole('heading', { name: 'Engineering. Friendship. Service.' }),
  ).toBeVisible();
  await expect(page.getByRole('link', { name: 'Join SPD', exact: true }).last()).toHaveAttribute(
    'href',
    '/app/join',
  );
  await expect(
    page.getByRole('img', {
      name: 'Sigma Phi Delta chapter members together with the fraternity banner',
    }),
  ).toBeVisible();
  expect(
    await page.locator('.hero-image').evaluate((image) => (image as HTMLImageElement).naturalWidth),
  ).toBeGreaterThan(0);
  await expect(page.getByText('Upcoming events', { exact: true })).toHaveCount(0);
  await page.reload();
  await expect(
    page.getByRole('heading', { name: 'Engineering a stronger brotherhood.' }),
  ).toBeVisible();
});

test('failed home content shows retry and preserves useful chapter links', async ({ page }) => {
  await page.route('**/api/v1/public/home/', (route) => route.fulfill({ status: 503, json: {} }));
  await page.goto('/app/');
  await expect(page.getByRole('alert')).toContainText('Chapter updates are unavailable.');
  await expect(page.getByRole('link', { name: 'Explore recruitment' })).toHaveAttribute(
    'href',
    '/app/join',
  );
  await page.unroute('**/api/v1/public/home/');
  await page.getByRole('button', { name: 'Retry chapter updates' }).click();
  await expect(page.getByRole('alert')).toHaveCount(0);
});

test('purpose navigation scrolls to the section after rendering from another route', async ({
  page,
}) => {
  await page.goto('/app/connection');
  await page.getByRole('link', { name: 'Our purpose' }).click();
  await expect(page).toHaveURL(/\/app\/?#purpose$/);
  await expect
    .poll(() =>
      page.locator('#purpose').evaluate((node) => Math.abs(node.getBoundingClientRect().top)),
    )
    .toBeLessThan(2);
});
