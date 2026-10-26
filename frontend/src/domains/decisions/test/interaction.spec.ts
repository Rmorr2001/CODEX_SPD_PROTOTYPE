import { expect, test } from '@playwright/test';
import { enterDemo } from '../../identity/test/helpers';

test('unchanged, held and focus refreshes preserve mounted poll content and focus', async ({
  page,
}) => {
  await enterDemo(page);
  await page.goto('/app/polls');
  const card = page.locator('.motion-card.current');
  await expect(card).toBeVisible();
  const node = await card.elementHandle();
  const choice = page.getByRole('button', { name: 'Vote Aye', exact: true });
  await choice.focus();
  const before = await card.boundingBox();
  const snapshot = await (await page.request.get('/api/v1/polls/')).json();
  let reads = 0;
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route('**/api/v1/polls/', async (route) => {
    reads++;
    if (reads === 1) await gate;
    await route.fulfill({ json: snapshot });
  });
  await page.evaluate(() => {
    const card = document.querySelector('.motion-card.current')!;
    const state = { mutations: 0 };
    Object.assign(window, { pollObservation: state });
    new MutationObserver((records) => {
      state.mutations += records.length;
    }).observe(card, { subtree: true, childList: true, characterData: true, attributes: true });
    window.dispatchEvent(new Event('focus'));
  });
  await expect.poll(() => reads).toBe(1);
  await expect(choice).toBeFocused();
  expect(await card.boundingBox()).toEqual(before);
  release();
  await expect.poll(() => reads, { timeout: 8000 }).toBeGreaterThanOrEqual(2);
  expect(
    await node!.evaluate((element) => element === document.querySelector('.motion-card.current')),
  ).toBeTruthy();
  expect(
    await page.evaluate(
      () =>
        (window as unknown as { pollObservation: { mutations: number } }).pollObservation.mutations,
    ),
  ).toBe(0);
  await expect(choice).toBeFocused();
  await expect(page.getByText('Loading polls…')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Log service', exact: true })).toHaveCount(0);
});

test('held repeated votes give immediate feedback without layout jumps and rolls back failed selection', async ({
  page,
}) => {
  await enterDemo(page);
  await page.goto('/app/polls');
  const card = page.locator('.motion-card.current');
  await expect(card).toBeVisible();
  const before = await card.boundingBox();
  const selectedLabel = await card.getByRole('button', { pressed: true }).textContent();
  const selected = card.getByRole('button', { name: selectedLabel!.trim(), exact: true });
  const next = page.getByRole('button', {
    name: selectedLabel?.includes('Aye') ? 'Vote Nay' : 'Vote Aye',
    exact: true,
  });
  let writes = 0;
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route('**/api/v1/polls/*/vote/', async (route) => {
    writes++;
    await gate;
    await route.fulfill({ status: 400, json: { detail: 'Vote could not be saved.' } });
  });
  try {
    await next.evaluate((element: HTMLButtonElement) => {
      element.click();
      element.click();
    });
    await expect(card.getByRole('status')).toContainText('Saving');
    await expect.poll(() => writes).toBe(1);
    expect(await card.boundingBox()).toEqual(before);
    await expect(selected).toHaveAttribute('aria-pressed', 'false');
    await expect(next).toHaveAttribute('aria-pressed', 'true');
    await expect(next).toBeEnabled();
  } finally {
    release();
  }
  await expect(card.getByRole('alert')).toHaveText('Vote could not be saved.');
  await expect(selected).toHaveAttribute('aria-pressed', 'true');
  await expect(next).toBeEnabled();
  expect(await card.boundingBox()).toEqual(before);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  expect(
    await card
      .locator('.vote-track > span')
      .first()
      .evaluate((element) => getComputedStyle(element).transitionProperty),
  ).toBe('none');
});

test('failed automatic poll reads stay in their error state rather than flashing loading', async ({
  page,
}) => {
  await enterDemo(page);
  let reads = 0;
  await page.route('**/api/v1/polls/', (route) => {
    reads++;
    return route.fulfill({ status: 503, json: {} });
  });
  await page.goto('/app/polls');
  await expect(page.getByRole('alert')).toHaveText('Couldn’t load polls.');
  await page.evaluate(() => {
    Object.assign(window, { loadingFlashes: 0 });
    new MutationObserver(() => {
      if (document.querySelector('main')?.textContent?.includes('Loading polls…')) {
        (window as unknown as { loadingFlashes: number }).loadingFlashes++;
      }
    }).observe(document.querySelector('main')!, { subtree: true, childList: true });
  });
  await expect.poll(() => reads, { timeout: 8000 }).toBeGreaterThanOrEqual(2);
  await expect(page.getByRole('alert')).toHaveText('Couldn’t load polls.');
  expect(
    await page.evaluate(() => (window as unknown as { loadingFlashes: number }).loadingFlashes),
  ).toBe(0);
});
