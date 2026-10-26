import { expect, test } from '@playwright/test';
import { enterDemo } from '../src/domains/identity/test/helpers';

test('confirmed vote appears before refetch and another session updates without navigation', async ({
  page,
  browser,
}) => {
  await enterDemo(page, 'executive');
  await page.goto('/app/polls');
  await expect(page.locator('.motion-card.current')).toBeVisible();
  const context = await browser.newContext();
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  try {
    const writer = await context.newPage();
    await enterDemo(writer, 'active');
    await writer.goto('/app/polls');
    await expect(writer.getByRole('button', { name: 'Vote Aye', exact: true })).toBeVisible();
    await writer.route('**/api/v1/polls/', async (route) => {
      await gate;
      await route.continue().catch(() => {});
    });
    const response = writer.waitForResponse(
      (r) => r.url().endsWith('/vote/') && r.request().method() === 'PUT',
    );
    await writer.getByRole('button', { name: 'Vote Aye', exact: true }).click();
    const confirmed = await (await response).json();
    await expect(writer.getByRole('button', { name: 'Vote Aye', exact: true })).toHaveAttribute(
      'aria-pressed',
      'true',
      { timeout: 1000 },
    );
    await expect(writer.locator('.motion-card.current .vote-row').first()).toContainText(
      `${confirmed.aye} votes`,
    );
    await expect(page.locator('.motion-card.current .vote-row').first()).toContainText(
      `${confirmed.aye} votes`,
      { timeout: 10000 },
    );
    await expect(page.locator('.motion-card.current .vote-row').nth(1)).toContainText(
      `${confirmed.nay} votes`,
    );
  } finally {
    release();
    await context.close();
  }
});

test('background failure keeps confirmed results, while denied access clears them', async ({
  page,
}) => {
  await enterDemo(page, 'active');
  await page.goto('/app/polls');
  const card = page.locator('.motion-card.current');
  await expect(card).toBeVisible();
  const title = await card.locator('h3').innerText();
  await page.route('**/api/v1/polls/', (route) => route.fulfill({ status: 503, json: {} }));
  await page.getByRole('button', { name: 'Refresh results' }).click();
  await expect(page.getByRole('status')).toContainText('Updates paused.');
  await expect(card.locator('h3')).toHaveText(title);
  await expect(page.getByRole('button', { name: 'Vote Aye', exact: true })).toBeVisible();
  await page.unroute('**/api/v1/polls/');
  await page.route('**/api/v1/polls/', (route) => route.fulfill({ status: 403, json: {} }));
  await page.getByRole('button', { name: 'Refresh results' }).click();
  await expect(page.getByRole('heading', { name: 'Active member access required' })).toBeVisible();
  await expect(card).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Vote Aye', exact: true })).toHaveCount(0);
});
