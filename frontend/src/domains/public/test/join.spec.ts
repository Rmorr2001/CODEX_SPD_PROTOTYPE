import { expect, test } from '@playwright/test';

test('join renders actual recruitment content and original configured destination', async ({
  page,
  request,
}) => {
  const response = await request.get('/api/v1/public/recruitment/');
  expect(response.status()).toBe(200);
  const content = await response.json();
  await page.goto('/app/join');
  await expect(
    page.getByRole('heading', { name: 'Find your people. Build your future.' }),
  ).toBeVisible();
  await expect(page.locator('.recruitment-slide')).toHaveCount(content.slides.length);
  for (const [index, slide] of content.slides.entries())
    await expect(page.locator('.recruitment-slide figcaption').nth(index)).toHaveText(
      slide.caption || 'A look at chapter life',
    );
  await expect(page.getByRole('link', { name: 'Explore recruitment' })).toHaveAttribute(
    'href',
    content.interest_url,
  );
  await expect(
    page.getByRole('link', { name: 'Recruitment details', exact: true }),
  ).toHaveAttribute('href', '/rush/');
  await page.reload();
  await expect(
    page.getByRole('heading', { name: 'Find your people. Build your future.' }),
  ).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
});

test('join handles empty content and failure with meaningful fallbacks and retry', async ({
  page,
}) => {
  await page.route('**/api/v1/public/recruitment/', (route) =>
    route.fulfill({ json: { interest_url: null, slides: [] } }),
  );
  await page.goto('/app/join');
  await expect(
    page.getByText('An interest link has not been published.', { exact: false }),
  ).toBeVisible();
  await expect(page.getByRole('link', { name: 'View original recruitment page' })).toHaveAttribute(
    'href',
    '/rush/',
  );
  await expect(
    page.getByText('Recruitment photos have not been published yet.', { exact: false }),
  ).toBeVisible();
  await page.route('**/api/v1/public/recruitment/', (route) =>
    route.fulfill({ status: 503, json: {} }),
  );
  await page.reload();
  await expect(page.getByRole('alert')).toHaveText(
    'Recruitment updates are unavailable right now.',
  );
  await page.unroute('**/api/v1/public/recruitment/');
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.getByRole('alert')).toHaveCount(0);
  await expect(page.locator('.recruitment-slide')).not.toHaveCount(0);
});

test('join navigation stays in React and does not invent scheduled events', async ({ page }) => {
  await page.goto('/app/');
  await page
    .getByRole('navigation', { name: 'Public navigation' })
    .getByRole('link', { name: 'Join SPD' })
    .click();
  await expect(page).toHaveURL(/\/app\/join$/);
  await page.getByRole('link', { name: 'Meet the chapter' }).click();
  await expect(page).toHaveURL(/\/app\/about$/);
  await page.getByRole('link', { name: 'Explore recruitment' }).click();
  await expect(page).toHaveURL(/\/app\/join$/);
  await expect(page.getByText('Recruitment events', { exact: true })).toHaveCount(0);
});
