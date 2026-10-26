import { expect, test } from '@playwright/test';
import { enterDemo } from '../../identity/test/helpers';

for (const width of [1536, 390]) {
  test(`service drawer protects drafts, traps focus and submits at ${width}px`, async ({
    page,
  }, info) => {
    await page.setViewportSize({ width, height: 1024 });
    await enterDemo(page);
    await page.goto('/app/service');
    await expect(page.locator('.service-summary')).toBeVisible();
    const trigger = page.getByRole('button', { name: 'Log service', exact: true });
    await expect(
      page.locator('.member-topbar').getByRole('button', { name: 'Log service', exact: true }),
    ).toHaveCount(0);
    await expect(
      page.locator('.service-summary').getByRole('button', { name: 'Log service', exact: true }),
    ).toBeVisible();
    await trigger.click();
    const dialog = page.getByRole('dialog', { name: 'Log service', exact: true });
    const event = dialog.getByLabel('Event', { exact: true });
    await expect(event).toBeFocused();
    await expect(dialog.getByLabel('Notes')).toHaveCount(0);
    const bounds = await dialog.boundingBox();
    expect(bounds!.width).toBeLessThanOrEqual(width);
    if (width === 390) expect(bounds!.width).toBe(width);
    for (let i = 0; i < 8; i++) {
      await page.keyboard.press('Tab');
      expect(await dialog.evaluate((node) => node.contains(document.activeElement))).toBeTruthy();
    }
    await event.fill(`Fictional drawer ${width}`);
    await dialog.getByLabel('Hours', { exact: true }).fill('0.75');
    await page.screenshot({ path: info.outputPath(`service-${width}.png`), fullPage: true });
    // A failed background read must not erase a separate form-local draft.
    await page.route('**/api/v1/service/', (route) =>
      route.request().method() === 'GET'
        ? route.fulfill({ status: 503, json: {} })
        : route.continue(),
    );
    await expect(page.getByText('Updates paused.')).toBeVisible({ timeout: 10000 });
    await expect(event).toHaveValue(`Fictional drawer ${width}`);
    page.once('dialog', (confirm) => confirm.dismiss());
    await page.keyboard.press('Escape');
    await expect(dialog).toBeVisible();
    await expect(event).toHaveValue(`Fictional drawer ${width}`);
    page.once('dialog', (confirm) => confirm.accept());
    await dialog.getByRole('button', { name: 'Cancel', exact: true }).click();
    await expect(dialog).toHaveCount(0);
    await expect(trigger).toBeFocused();
    await trigger.click();
    await expect(dialog.getByLabel('Event', { exact: true })).toHaveValue('');
    await dialog.getByLabel('Event', { exact: true }).fill(`Fictional drawer ${width}`);
    await dialog.getByLabel('Hours', { exact: true }).fill('0.75');
    await page.unroute('**/api/v1/service/');
    await dialog.getByRole('button', { name: 'Submit', exact: true }).click();
    await expect(dialog).toHaveCount(0);
    await expect(page.getByText('Service submitted.', { exact: true })).toBeVisible();
    await expect(
      page.getByRole('row').filter({ hasText: `Fictional drawer ${width}` }),
    ).toContainText('Pending');
    await page.getByRole('button', { name: 'Dismiss service confirmation' }).click();
    await expect(page.getByText('Service submitted.', { exact: true })).toHaveCount(0);
    await trigger.click();
    await expect(dialog.getByLabel('Event', { exact: true })).toHaveValue('');
    await page.keyboard.press('Escape');
    await expect(trigger).toBeFocused();
    if (width === 390) {
      await page.getByRole('button', { name: 'Open navigation' }).click();
      const menu = page.getByRole('dialog', { name: 'Menu', exact: true });
      await menu.getByRole('link', { name: 'Polls', exact: true }).click();
      await expect(menu).toHaveCount(0);
      await expect(page.locator('.motion-card.current')).toBeVisible();
      expect(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
      ).toBeTruthy();
    }
  });
}

test('drawer retains validation errors, blocks dismissal during a save and prevents duplicate writes', async ({
  page,
}) => {
  await enterDemo(page);
  await page.goto('/app/service');
  await page.getByRole('button', { name: 'Log service', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Log service', exact: true });
  await dialog.getByLabel('Event', { exact: true }).fill('Fictional validation');
  await dialog.getByLabel('Hours', { exact: true }).fill('1.25');
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  let writes = 0;
  await page.route('**/api/v1/service/', async (route) => {
    if (route.request().method() !== 'POST') return route.continue();
    writes++;
    await gate;
    await route.fulfill({ status: 400, json: { detail: 'Example validation failure.' } });
  });
  try {
    await dialog.getByRole('button', { name: 'Submit', exact: true }).click();
    await expect(dialog.getByRole('button', { name: 'Submitting…' })).toBeDisabled();
    await expect(dialog.getByRole('button', { name: 'Cancel' })).toBeDisabled();
    await expect(dialog.getByRole('button', { name: 'Close service drawer' })).toBeDisabled();
    await page.keyboard.press('Escape');
    await expect(dialog).toBeVisible();
    expect(writes).toBe(1);
  } finally {
    release();
  }
  await expect(dialog.getByRole('alert')).toContainText('Example validation failure.');
  await expect(dialog.getByLabel('Event', { exact: true })).toHaveValue('Fictional validation');
  await expect(dialog.getByLabel('Hours', { exact: true })).toHaveValue('1.25');
});

test('dirty drawer handles browser back and forward without silent draft loss', async ({
  page,
}) => {
  await enterDemo(page);
  await page
    .getByRole('navigation', { name: 'Member navigation' })
    .getByRole('link', { name: 'Service', exact: true })
    .click();
  await page.getByRole('button', { name: 'Log service', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Log service', exact: true });
  await dialog.getByLabel('Event', { exact: true }).fill('Keep this draft');
  page.once('dialog', (confirm) => confirm.dismiss());
  await page.goBack();
  await expect(page).toHaveURL(/\/app\/service$/);
  await expect(dialog.getByLabel('Event', { exact: true })).toHaveValue('Keep this draft');
  page.once('dialog', (confirm) => confirm.accept());
  await page.goBack();
  await expect(page).toHaveURL(/\/app\/dashboard$/);
  await expect(dialog).toHaveCount(0);
  await page.goForward();
  await expect(page).toHaveURL(/\/app\/service$/);
  await page.getByRole('button', { name: 'Log service', exact: true }).click();
  await expect(dialog.getByLabel('Event', { exact: true })).toHaveValue('');
});

test('ineligible member has no quick-entry control', async ({ page }) => {
  await enterDemo(page, 'alumni');
  await expect(page.getByRole('button', { name: 'Log service', exact: true })).toHaveCount(0);
});
