import { expect, test } from '@playwright/test';
import { enterDemo } from './helpers';

test('anonymous member route exposes sign in without dashboard data', async ({ page, request }) => {
  expect((await request.get('/api/v1/dashboard/')).status()).toBe(403);
  await page.goto('/app/dashboard');
  await expect(page.getByRole('heading', { name: 'Member sign in' })).toBeVisible();
  await expect(page.locator('.dashboard-summary')).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Sign in to your chapter account' })).toHaveAttribute(
    'href',
    '/auth/login/?next=%2Fapp%2Fdashboard',
  );
});

test('real demo entry loads the caller and actual active announcements and resources', async ({
  page,
}) => {
  await enterDemo(page, 'executive');
  const session = await (await page.request.get('/api/v1/session/')).json();
  const dashboard = await (await page.request.get('/api/v1/dashboard/')).json();
  await expect(
    page.getByRole('heading', {
      name: `Welcome back, ${session.member.display_name.split(' ')[0]}.`,
    }),
  ).toBeVisible();
  await expect(page.locator('.announcement')).toHaveCount(dashboard.announcements.length);
  await expect(page.locator('.resource-list a')).toHaveCount(dashboard.links.length);
  await expect(page.locator('.member-topbar')).toContainText(session.member.display_name);
  await expect(page.getByRole('navigation', { name: 'Member navigation' })).toBeVisible();
  await page.reload();
  await expect(page.locator('.dashboard-summary')).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
});

test('new member native entry respects the actual separate landing rule', async ({ page }) => {
  await enterDemo(page, 'newmember');
  await expect(page).toHaveURL(/\/app\/new-members$/);
  await expect(page.getByRole('link', { name: 'Open your new-member dashboard' })).toHaveAttribute(
    'href',
    '/newmember/',
  );
  await expect(page.locator('.dashboard-summary')).toHaveCount(0);
  const dashboard = await (await page.request.get('/api/v1/dashboard/')).json();
  expect(dashboard.announcements).toEqual([]);
});

test('alumni navigation reflects actual role and logout ends the real session', async ({
  page,
}) => {
  await enterDemo(page, 'alumni');
  await expect(page.locator('.dashboard-summary')).toBeVisible();
  const nav = page.getByRole('navigation', { name: 'Member navigation' });
  await expect(nav.getByRole('link', { name: 'Polls', exact: true })).toHaveCount(0);
  await expect(nav.getByRole('link', { name: 'Service hours', exact: true })).toHaveCount(0);
  await page.getByRole('link', { name: 'Sign out', exact: true }).click();
  expect((await (await page.request.get('/api/v1/session/')).json()).authenticated).toBe(false);
});

test('session read failure retries without exposing member content', async ({ page }) => {
  await page.route('**/api/v1/session/', (route) => route.fulfill({ status: 503, json: {} }));
  await page.goto('/app/dashboard');
  await expect(page.getByRole('alert')).toHaveText(
    'We couldn’t check your session. Please try again.',
  );
  await expect(page.locator('.member-topbar')).toHaveCount(0);
  await page.unroute('**/api/v1/session/');
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.getByRole('link', { name: 'Sign in to your chapter account' })).toBeVisible();
});

test('missing profile has a clear state instead of a crash or data flash', async ({ page }) => {
  await page.route('**/api/v1/session/', (route) =>
    route.fulfill({
      json: {
        authenticated: true,
        profile_available: false,
        demo_enabled: false,
        landing_path: '/app/login',
        member: null,
      },
    }),
  );
  await page.goto('/app/dashboard');
  await expect(page.getByRole('alert')).toContainText('Your member profile is unavailable.');
  await expect(page.locator('.dashboard-summary')).toHaveCount(0);
});

test('dashboard permission failure removes feed and offers real sign in', async ({ page }) => {
  await page.route('**/api/v1/dashboard/', (route) =>
    route.fulfill({ status: 403, json: { detail: 'Permission denied' } }),
  );
  await enterDemo(page);
  await expect(page.getByRole('heading', { name: 'Member access required' })).toBeVisible();
  await expect(page.locator('.announcement')).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Sign in to your chapter account' })).toHaveAttribute(
    'href',
    '/auth/login/?next=%2Fapp%2Fdashboard',
  );
});

test('dashboard handles empty content and unavailable read with retry', async ({ page }) => {
  await page.route('**/api/v1/dashboard/', (route) =>
    route.fulfill({ json: { landing_path: '/app/dashboard', announcements: [], links: [] } }),
  );
  await enterDemo(page);
  await expect(page.getByText('There are no active chapter announcements.')).toBeVisible();
  await expect(page.getByText('No chapter resources have been published yet.')).toBeVisible();
  await page.route('**/api/v1/dashboard/', (route) => route.fulfill({ status: 503, json: {} }));
  await page.reload();
  await expect(page.getByRole('alert')).toHaveText(
    'We couldn’t load your chapter updates. Please try again.',
  );
  await page.unroute('**/api/v1/dashboard/');
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.locator('.announcement')).not.toHaveCount(0);
});

test('demo role change opens the actual role-selection form', async ({ page }) => {
  await enterDemo(page);
  await page.getByRole('link', { name: 'Change demo role' }).click();
  await expect(page).toHaveURL(/\/app\/login$/);
  await expect(page.getByLabel('Explore as')).toBeVisible();
  await page.getByLabel('Explore as').selectOption('alumni');
  await page.getByRole('button', { name: 'Enter demo', exact: true }).click();
  await expect(page).toHaveURL(/\/app\/dashboard$/);
  await expect(
    page
      .getByRole('navigation', { name: 'Member navigation' })
      .getByRole('link', { name: 'Polls', exact: true }),
  ).toHaveCount(0);
});
