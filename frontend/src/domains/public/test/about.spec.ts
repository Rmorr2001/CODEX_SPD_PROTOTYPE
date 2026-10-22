import { expect, test } from '@playwright/test';

test('about uses real public executive cards, count and original supporting routes', async ({
  page,
  request,
}) => {
  const response = await request.get('/api/v1/public/about/');
  expect(response.status()).toBe(200);
  const content = await response.json();
  await page.goto('/app/about');
  await expect(page.getByRole('heading', { name: 'Built together.' })).toBeVisible();
  await expect(page.locator('.executive-card')).toHaveCount(content.executives.length);
  await expect(page.locator('.chapter-count strong')).toHaveText(String(content.active_count));
  if (content.executives.length)
    await expect(page.locator('.executive-card h3').first()).toHaveText(content.executives[0].name);
  await expect(page.getByRole('link', { name: 'Read our full history' })).toHaveAttribute(
    'href',
    '/ourHistory/',
  );
  await expect(page.getByRole('link', { name: 'Our code of ethics' })).toHaveAttribute(
    'href',
    '/codeOfEthics/',
  );
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Built together.' })).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
});

test('about empty leadership and read failure remain useful and recoverable', async ({ page }) => {
  await page.route('**/api/v1/public/about/', (route) =>
    route.fulfill({ json: { active_count: 0, executives: [] } }),
  );
  await page.goto('/app/about');
  await expect(page.getByText('Chapter leadership has not been published yet.')).toBeVisible();
  await page.route('**/api/v1/public/about/', (route) => route.fulfill({ status: 503, json: {} }));
  await page.reload();
  await expect(page.getByRole('alert')).toHaveText('Chapter leadership is unavailable right now.');
  await page.unroute('**/api/v1/public/about/');
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.getByRole('alert')).toHaveCount(0);
  await expect(page.locator('.executive-card')).not.toHaveCount(0);
});

test('about and brotherhood navigation reaches React screen and leadership anchor', async ({
  page,
}) => {
  await page.goto('/app/');
  await page.getByRole('link', { name: 'Meet the chapter' }).click();
  await expect(page).toHaveURL(/\/app\/about$/);
  await page.getByRole('link', { name: 'Brotherhood', exact: true }).click();
  await expect(page).toHaveURL(/\/app\/about#leadership$/);
  await expect
    .poll(() =>
      page
        .locator('#leadership')
        .evaluate((node) => Math.abs(node.getBoundingClientRect().top - 20)),
    )
    .toBeLessThan(2);
});
