import { expect, test } from '@playwright/test';
import { enterDemo } from '../../identity/test/helpers';

test('decisions render actual aggregate motion results and truthful legacy voting action', async ({
  page,
}) => {
  await enterDemo(page, 'executive');
  const content = await (await page.request.get('/api/v1/polls/')).json();
  await page
    .getByRole('navigation', { name: 'Member navigation' })
    .getByRole('link', { name: 'Polls', exact: true })
    .click();
  await expect(page).toHaveURL(/\/app\/polls$/);
  await expect(page.locator('.motion-card.current h3')).toHaveText(content.current.title);
  await expect(page.locator('.motion-card.current .vote-row').first()).toContainText(
    `${content.current.aye} votes`,
  );
  await expect(page.locator('.closed-motion-list .motion-card')).toHaveCount(content.closed.length);
  await expect(
    page.getByRole('link', { name: 'Vote in chapter site', exact: true }),
  ).toHaveAttribute('href', '/poll/');
  await expect(page.getByRole('link', { name: 'Create a motion in chapter site' })).toHaveAttribute(
    'href',
    '/poll/start_vote/',
  );
  await expect(page.locator('input[type="radio"]')).toHaveCount(0);
  await page.getByRole('button', { name: 'Refresh results' }).click();
  await expect(page.locator('.motion-card.current')).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Chapter decisions.' })).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
});

test('decision creation is hidden for active nonexecutive and alumni read is denied', async ({
  page,
}) => {
  await enterDemo(page);
  await page.goto('/app/polls');
  await expect(page.locator('.motion-card.current')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Create a motion in chapter site' })).toHaveCount(0);
  await enterDemo(page, 'alumni');
  expect((await page.request.get('/api/v1/polls/')).status()).toBe(403);
  await page.goto('/app/polls');
  await expect(page.getByRole('heading', { name: 'Active member access required' })).toBeVisible();
  await expect(page.locator('.motion-card')).toHaveCount(0);
});

test('decisions handle zero votes, no open motion and failed read with real retry', async ({
  page,
}) => {
  await enterDemo(page);
  const zero = {
    id: 99,
    title: 'No votes yet',
    started_at: '2026-01-01T12:00:00Z',
    ended_at: null,
    aye: 0,
    nay: 0,
  };
  await page.route('**/api/v1/polls/', (route) =>
    route.fulfill({ json: { current: zero, closed: [], can_manage: false } }),
  );
  await page.goto('/app/polls');
  await expect(page.getByText('No votes recorded')).toBeVisible();
  expect(await page.locator('.vote-track > span').first().getAttribute('style')).toContain(
    'width: 0%',
  );
  await page.route('**/api/v1/polls/', (route) =>
    route.fulfill({ json: { current: null, closed: [], can_manage: false } }),
  );
  await page.reload();
  await expect(page.getByRole('heading', { name: 'The floor is clear.' })).toBeVisible();
  await expect(page.getByText('No closed motions have been recorded yet.')).toBeVisible();
  await page.route('**/api/v1/polls/', (route) => route.fulfill({ status: 503, json: {} }));
  await page.reload();
  await expect(page.getByRole('alert')).toHaveText(
    'We couldn’t load the motion results. Please try again.',
  );
  await page.unroute('**/api/v1/polls/');
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.locator('.motion-card.current')).toBeVisible();
});
