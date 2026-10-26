import { expect, test } from '@playwright/test';
import { enterDemo } from '../../identity/test/helpers';

test('new member sees actual own approved history and standing after native entry and refresh', async ({
  page,
}) => {
  await enterDemo(page, 'newmember');
  const data = await (await page.request.get('/api/v1/new-members/')).json();
  expect(data.mode).toBe('personal');
  await expect(page.getByRole('heading', { name: 'New-member marks', exact: true })).toBeVisible();
  await expect(page.locator('.marks-total strong')).toHaveText(`+${data.personal.total_marks}`);
  await expect(
    page.getByRole('heading', { name: data.personal.standing, exact: true }),
  ).toBeVisible();
  await expect(page.locator('.marks-history li')).toHaveCount(data.personal.history.length);
  await expect(page.getByRole('link', { name: 'View your history' })).toHaveAttribute(
    'href',
    '/app/new-members/history/' + data.personal.history_url.split('/').filter(Boolean).at(-1),
  );
  await expect(page.locator('.marks-analytics')).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Submit marks', exact: true })).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Review marks', exact: true })).toHaveCount(0);
  await page.reload();
  await expect(page.locator('.marks-total strong')).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(
    page.getByRole('heading', { name: data.personal.standing, exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
  await page.getByRole('link', { name: 'View your history' }).click();
  await expect(page).toHaveURL(/\/app\/new-members\/history\/\d+$/);
});

test('active class totals and executive own submissions use real data and legacy workflows', async ({
  page,
}) => {
  await enterDemo(page, 'executive');
  const data = await (await page.request.get('/api/v1/new-members/')).json();
  await page
    .getByRole('navigation', { name: 'Member navigation' })
    .getByRole('link', { name: 'New members', exact: true })
    .click();
  await expect(page).toHaveURL(/\/app\/new-members$/);
  await expect(page.locator('.marks-analytics > div').first().locator('strong')).toHaveText(
    String(data.analytics.total_new_members),
  );
  await expect(page.locator('.class-marks-list > li')).toHaveCount(data.members.length);
  await expect(page.locator('.marks-submission-list > li')).toHaveCount(data.submissions.length);
  for (const [index, member] of data.members.entries()) {
    await expect(page.locator('.class-marks-list > li').nth(index).getByRole('heading')).toHaveText(
      member.display_name,
    );
  }
  await expect(page.getByRole('link', { name: 'Review marks', exact: true })).toHaveAttribute(
    'href',
    '/app/new-members/review',
  );
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
  await page.getByRole('link', { name: 'Submit marks', exact: true }).click();
  await expect(page).toHaveURL(/\/app\/new-members\/new$/);
  await expect(page.getByLabel('Marks', { exact: true })).toBeVisible();
});

test('ordinary active has no review action and alumni are denied without marks', async ({
  page,
}) => {
  await enterDemo(page);
  await page.goto('/app/new-members');
  await expect(page.locator('.marks-analytics')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Review marks', exact: true })).toHaveCount(0);
  await expect(page.getByText('You have no pending or recent denied submissions.')).toBeVisible();
  await enterDemo(page, 'alumni');
  expect((await page.request.get('/api/v1/new-members/')).status()).toBe(403);
  await page.goto('/app/new-members');
  await expect(page.getByRole('heading', { name: 'Member access required' })).toBeVisible();
  await expect(page.locator('.marks-history, .marks-analytics')).toHaveCount(0);
});

test('marks network failure retries the real API and session loss removes restricted data', async ({
  page,
}) => {
  await enterDemo(page, 'newmember');
  await page.route('**/api/v1/new-members/', (route) => route.fulfill({ status: 503, json: {} }));
  await page.goto('/app/new-members');
  await expect(page.getByRole('alert')).toHaveText(
    'We couldn’t load new-member marks. Please try again.',
  );
  await page.unroute('**/api/v1/new-members/');
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.locator('.marks-history')).toBeVisible();
  await page.context().clearCookies();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Member sign in' })).toBeVisible();
  await expect(page.locator('.marks-history')).toHaveCount(0);
});
