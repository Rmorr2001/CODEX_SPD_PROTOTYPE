import { expect, test } from '@playwright/test';
import { enterDemo } from './helpers';

test('directory uses actual current and alumni rosters with working search and selection', async ({
  page,
}) => {
  await enterDemo(page);
  const current = await (await page.request.get('/api/v1/members/')).json();
  await page
    .getByRole('navigation', { name: 'Member navigation' })
    .getByRole('link', { name: 'Members', exact: true })
    .click();
  await expect(page).toHaveURL(/\/app\/members$/);
  await expect(page.locator('.directory-member')).toHaveCount(current.members.length);
  const member = current.members[0];
  await page.getByLabel('Search the chapter').fill(member.display_name);
  await expect(page.locator('.directory-member').first()).toContainText(member.display_name);
  await page.locator('.directory-member').first().click();
  await expect(page.locator('.directory-detail h2')).toHaveText(member.display_name);
  await page.getByLabel('Search the chapter').fill('no matching member 198237');
  await expect(page.getByRole('heading', { name: 'No matching members' })).toBeVisible();
  await page.getByRole('button', { name: 'Clear filters' }).click();
  await expect(page.locator('.directory-member')).toHaveCount(current.members.length);
  await page.getByLabel('Filter by role').selectOption('ACTIVE');
  expect(await page.locator('.directory-member').count()).toBe(
    current.members.filter((item: { roles: { code: string }[] }) =>
      item.roles.some((role) => role.code === 'ACTIVE'),
    ).length,
  );
  const alumni = await (await page.request.get('/api/v1/members/?group=alumni')).json();
  await page.getByRole('button', { name: 'Alumni', exact: true }).click();
  await expect(page.locator('.directory-member')).toHaveCount(alumni.members.length);
  await expect(page.getByRole('button', { name: 'Alumni', exact: true })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'The chapter.' })).toBeVisible();
});

test('directory handles an empty group and failed read with real retry', async ({ page }) => {
  await enterDemo(page);
  await page.route('**/api/v1/members/**', (route) =>
    route.fulfill({ json: { group: 'current', members: [] } }),
  );
  await page.goto('/app/members');
  await expect(page.getByRole('heading', { name: 'No members to show yet' })).toBeVisible();
  await page.route('**/api/v1/members/**', (route) => route.fulfill({ status: 503, json: {} }));
  await page.reload();
  await expect(page.getByRole('alert')).toHaveText(
    'We couldn’t load the chapter directory. Please try again.',
  );
  await page.unroute('**/api/v1/members/**');
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.locator('.directory-member')).not.toHaveCount(0);
});

test('directory denied read shows no member cards', async ({ page }) => {
  await enterDemo(page);
  await page.route('**/api/v1/members/**', (route) => route.fulfill({ status: 403, json: {} }));
  await page.goto('/app/members');
  await expect(page.getByRole('heading', { name: 'Member access required' })).toBeVisible();
  await expect(page.locator('.directory-member')).toHaveCount(0);
});

test('mobile directory selection reveals and focuses the chosen member detail', async ({
  page,
}) => {
  await enterDemo(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/app/members');
  const choice = page.locator('.directory-member').nth(3);
  const name = await choice.locator('strong').innerText();
  await expect(choice).toHaveAttribute('aria-controls', 'directory-member-detail');
  await choice.click();
  const details = page.locator('#directory-member-detail');
  await expect(details.locator('h2')).toHaveText(name);
  await expect(details).toBeFocused();
  await expect(details.locator('h2')).toBeInViewport();
  await expect(details).toBeInViewport({ ratio: 0.9 });
});
