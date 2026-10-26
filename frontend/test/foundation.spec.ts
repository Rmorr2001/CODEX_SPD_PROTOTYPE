import { expect, test } from '@playwright/test';

test.beforeEach(async ({ request }) => {
  await expect
    .poll(
      async () => {
        try {
          return (await request.get('/api/v1/status/')).status();
        } catch {
          return 0;
        }
      },
      { timeout: 30000 },
    )
    .toBe(200);
});

test('public home retains built assets and legacy pages', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/app/');
  await expect(
    page.getByRole('heading', { name: 'Engineering a stronger brotherhood.', exact: true }),
  ).toBeVisible();
  const scripts = await page
    .locator('script[src]')
    .evaluateAll((nodes) => nodes.map((node) => node.getAttribute('src')));
  expect(scripts.some((path) => path?.startsWith('/static/app/assets/'))).toBeTruthy();
  await page.getByRole('link', { name: 'Legacy site' }).click();
  await expect(page).toHaveURL('/legacy/');
  await expect(
    page.getByText('Sigma Phi Delta: Beta-Omicron Chapter', { exact: false }),
  ).toBeVisible();
  expect(errors).toEqual([]);
});

test('nested route survives refresh and stays under the app prefix', async ({ page }) => {
  await page.goto('/app/connection');
  await expect(page.getByRole('heading', { name: 'Connection', exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('status')).toHaveText('Connected to the chapter service.');
  await page.getByRole('link', { name: 'Workspace', exact: true }).click();
  await expect(page).toHaveURL(/\/app\/?$/);
});

test('unknown SPA route displays a useful empty state', async ({ page }) => {
  await page.goto('/app/does-not-exist');
  await expect(page.getByRole('heading', { name: 'Page not found' })).toBeVisible();
  await page.getByRole('link', { name: 'Return to workspace' }).click();
  await expect(
    page.getByRole('heading', { name: 'Engineering a stronger brotherhood.', exact: true }),
  ).toBeVisible();
});

test('unknown API paths stay JSON rather than the SPA shell', async ({ request }) => {
  const response = await request.get('/api/v1/not-found/');
  expect(response.status()).toBe(404);
  expect(response.headers()['content-type']).toContain('application/json');
  expect(await response.json()).toEqual({ detail: 'Not found.' });
});

test('loading is visible until a response arrives', async ({ page }) => {
  let release!: () => void;
  const responseGate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route('**/api/v1/status/', async (route) => {
    await responseGate;
    await route.fulfill({ json: { status: 'ok', api_version: 'v1' } });
  });
  await page.goto('/app/connection');
  await expect(page.getByRole('status')).toHaveText('Checking the chapter service…');
  release();
  await expect(page.getByRole('status')).toHaveText('Connected to the chapter service.');
});

for (const failure of ['unavailable', 'invalid-contract', 'html-response'] as const) {
  test(`service ${failure} can recover with retry`, async ({ page }) => {
    await page.route('**/api/v1/status/', (route) => {
      if (failure === 'unavailable')
        return route.fulfill({ status: 503, json: { detail: 'Unavailable' } });
      if (failure === 'invalid-contract')
        return route.fulfill({ json: { status: 'ok', api_version: 999 } });
      return route.fulfill({ contentType: 'text/html', body: '<html>Wrong response</html>' });
    });
    await page.goto('/app/connection');
    await expect(page.getByRole('alert')).toHaveText(
      'Unable to reach the chapter service. Please try again.',
    );
    await page.unroute('**/api/v1/status/');
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page.getByRole('status')).toHaveText('Connected to the chapter service.');
  });
}

test('small screens retain navigation without page overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/app/');
  await expect(page.getByRole('navigation', { name: 'Public navigation' })).toBeVisible();
  await expect(
    page.getByRole('heading', { name: 'Engineering a stronger brotherhood.' }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
  ).toBeTruthy();
});
