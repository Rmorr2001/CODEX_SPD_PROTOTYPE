import { expect, test } from '@playwright/test';
import { enterDemo } from '../src/domains/identity/test/helpers';

test('legacy active ballot hides executive controls while executive still sees them', async ({
  page,
}) => {
  await enterDemo(page, 'active');
  await page.goto('/poll/');
  await expect(page.getByRole('button', { name: 'Aye', exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Start New Vote', exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'End Vote', exact: true })).toHaveCount(0);
  await enterDemo(page, 'executive');
  await page.goto('/poll/');
  await expect(page.getByRole('link', { name: 'Start New Vote', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'End Vote', exact: true })).toBeVisible();
});

test('both review interfaces hide own decisions and retain eligible controls', async ({ page }) => {
  await enterDemo(page, 'executive');
  const records: { id: number; title: string; can_decide: boolean }[] = await (
    await page.request.get('/api/v1/service/review/')
  ).json();
  const own = records.find((entry) => !entry.can_decide);
  const other = records.find((entry) => entry.can_decide);
  expect(own).toBeTruthy();
  expect(other).toBeTruthy();
  await page.goto('/app/service/review');
  const ownCard = page.locator(`article[data-request-id="${own!.id}"]`);
  await expect(ownCard).toContainText('Another chair must review.');
  await expect(ownCard.getByRole('button', { name: /^Approve|^Deny/ })).toHaveCount(0);
  const otherCard = page.locator(`article[data-request-id="${other!.id}"]`);
  await expect(
    otherCard.getByRole('button', { name: `Approve ${other!.title}`, exact: true }),
  ).toBeVisible();
  await page.goto('/philanthropy/approve/');
  await expect(page.locator(`input[name="event_id"][value="${own!.id}"]`)).toHaveCount(0);
  await expect(page.getByText('Another chair must review.', { exact: true })).toBeVisible();
  await expect(page.locator(`input[name="event_id"][value="${other!.id}"]`)).toBeAttached();
});
