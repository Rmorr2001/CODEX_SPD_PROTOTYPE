import { expect, test } from '@playwright/test';
import { enterDemo } from '../../identity/test/helpers';

test('service shows actual own stored totals, statuses and working academic year selection', async ({
  page,
}) => {
  await enterDemo(page, 'executive');
  const data = await (await page.request.get('/api/v1/service/')).json();
  await page
    .getByRole('navigation', { name: 'Member navigation' })
    .getByRole('link', { name: 'Service hours', exact: true })
    .click();
  await expect(page).toHaveURL(/\/app\/service$/);
  await expect(page.locator('#service-total-title strong')).toHaveText(String(data.approved_hours));
  await expect(page.locator('.service-table tbody tr')).toHaveCount(data.events.length);
  await expect(page.locator('.service-status.requested').first()).toHaveText('…Pending');
  await expect(page.getByRole('link', { name: 'Log service hours' })).toHaveAttribute(
    'href',
    '/app/service/new',
  );
  await expect(page.getByRole('link', { name: 'Review service requests' })).toHaveAttribute(
    'href',
    '/app/service/review',
  );
  await expect(
    page.getByRole('link', { name: 'Log hours in chapter site', exact: true }),
  ).toHaveCount(0);
  await expect(page.locator('.service-heading a.primary')).toHaveAttribute(
    'href',
    '/app/service/new',
  );
  await expect(page.getByRole('link', { name: 'Legacy service', exact: true })).toHaveAttribute(
    'href',
    '/philanthropy/',
  );
  const previous = String(data.available_years[data.available_years.length - 1]);
  await page.getByLabel('Academic year').selectOption(previous);
  await expect(page).toHaveURL(new RegExp(`year=${previous}`));
  await expect(page.getByLabel('Academic year')).toHaveValue(previous);
  await expect(
    page.getByRole('heading', { name: 'No service entries for this year.' }),
  ).toBeVisible();
  await page.reload();
  await expect(page.getByLabel('Academic year')).toHaveValue(previous);
  await page.getByLabel('Academic year').selectOption(String(data.year));
  await expect(page.locator('.service-table')).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByText('Scroll horizontally to see hours and status.')).toBeVisible();
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
  const region = page.getByRole('region', { name: 'Your service hours table' });
  await expect(region).toHaveAttribute('aria-describedby', 'service-table-hint');
  await region.hover();
  await page.mouse.wheel(800, 0);
  await expect.poll(() => region.evaluate((node) => node.scrollLeft)).toBeGreaterThan(0);
  await expect(page.locator('.service-table .service-status').first()).toBeInViewport();
});

test('service approval is gated and alumni API reads are denied', async ({ page }) => {
  await enterDemo(page);
  await page.goto('/app/service');
  await expect(page.locator('.service-summary')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Review service requests' })).toHaveCount(0);
  await enterDemo(page, 'alumni');
  expect((await page.request.get('/api/v1/service/')).status()).toBe(403);
  await page.goto('/app/service');
  await expect(page.getByRole('heading', { name: 'Active member access required' })).toBeVisible();
  await expect(page.locator('.service-table')).toHaveCount(0);
});

test('service failure retries against actual data and request handoff opens real form', async ({
  page,
}) => {
  await enterDemo(page);
  await page.route('**/api/v1/service/**', (route) => route.fulfill({ status: 503, json: {} }));
  await page.goto('/app/service');
  await expect(page.getByRole('alert')).toHaveText(
    'We couldn’t load service hours for this academic year. Please try again.',
  );
  await page.unroute('**/api/v1/service/**');
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.locator('.service-summary')).toBeVisible();
  await page.getByRole('link', { name: 'Log service hours' }).click();
  await expect(page).toHaveURL(/\/app\/service\/new$/);
  await expect(page.getByLabel('Hours', { exact: true })).toBeVisible();
});
