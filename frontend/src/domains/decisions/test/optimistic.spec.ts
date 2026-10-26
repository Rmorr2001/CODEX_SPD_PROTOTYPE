import { expect, test } from '@playwright/test';
import { enterDemo } from '../../identity/test/helpers';

function deferred() {
  let release!: () => void;
  const promise = new Promise<void>((resolve) => {
    release = resolve;
  });
  return { promise, release };
}

test('rapid changes select instantly, serialize actual writes and save only the final acknowledged choice', async ({
  page,
}) => {
  await enterDemo(page);
  await page.goto('/app/polls');
  const card = page.locator('.motion-card.current');
  await expect(card).toBeVisible();
  const initial = await (await page.request.get('/api/v1/polls/')).json();
  const first = initial.own_choice === 'Aye' ? 'Nay' : 'Aye';
  const last = first === 'Aye' ? 'Nay' : 'Aye';
  const firstGate = deferred(),
    lastGate = deferred();
  const choices: string[] = [];
  await page.route('**/api/v1/polls/*/vote/', async (route) => {
    choices.push(route.request().postDataJSON().choice);
    await (choices.length === 1 ? firstGate.promise : lastGate.promise);
    await route.continue();
  });
  try {
    await page.getByRole('button', { name: `Vote ${first}`, exact: true }).click();
    await expect(page.getByRole('button', { name: `Vote ${first}`, exact: true })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    await expect(card.getByRole('status')).toHaveText('Saving…');
    expect((await (await page.request.get('/api/v1/polls/')).json()).own_choice).toBe(
      initial.own_choice,
    );
    await page.getByRole('button', { name: `Vote ${last}`, exact: true }).click();
    await expect(page.getByRole('button', { name: `Vote ${last}`, exact: true })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    expect(choices).toEqual([first]);
    firstGate.release();
    await expect.poll(() => choices.length).toBe(2);
    expect((await (await page.request.get('/api/v1/polls/')).json()).own_choice).toBe(first);
    await expect(card.getByRole('status')).toHaveText('Saving…');
    await expect(page.getByRole('button', { name: `Vote ${last}`, exact: true })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    lastGate.release();
    await expect(card.getByRole('status')).toHaveText('Saved');
    expect((await (await page.request.get('/api/v1/polls/')).json()).own_choice).toBe(last);
    await page.reload();
    await expect(page.getByRole('button', { name: `Vote ${last}`, exact: true })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
  } finally {
    firstGate.release();
    lastGate.release();
  }
});

test('failed optimistic tally and choice roll back, explicit retry persists, stale refresh cannot overwrite acknowledgement', async ({
  page,
}) => {
  await enterDemo(page);
  await page.goto('/app/polls');
  const card = page.locator('.motion-card.current');
  await expect(card).toBeVisible();
  const initial = await (await page.request.get('/api/v1/polls/')).json();
  const next = initial.own_choice === 'Aye' ? 'Nay' : 'Aye';
  const failure = deferred();
  await page.route('**/api/v1/polls/*/vote/', async (route) => {
    await failure.promise;
    await route.fulfill({ status: 503, json: { detail: 'Temporarily unavailable.' } });
  });
  await page.getByRole('button', { name: `Vote ${next}`, exact: true }).click();
  await expect(page.getByRole('button', { name: `Vote ${next}`, exact: true })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
  await expect(card.getByRole('status')).toHaveText('Saving…');
  const row = card.locator('.vote-row').nth(next === 'Aye' ? 0 : 1);
  await expect(row).toContainText(`${initial.current[next === 'Aye' ? 'aye' : 'nay'] + 1} votes`);
  failure.release();
  await expect(card.getByRole('status')).toHaveText('Not synced');
  await expect(
    page.getByRole('button', { name: `Vote ${initial.own_choice}`, exact: true }),
  ).toHaveAttribute('aria-pressed', 'true');
  await page.unroute('**/api/v1/polls/*/vote/');
  const stale = deferred();
  let held = false;
  await page.route('**/api/v1/polls/', async (route) => {
    if (!held) {
      held = true;
      await stale.promise;
      await route.fulfill({ json: initial }).catch(() => {});
    } else await route.continue();
  });
  try {
    await page.getByRole('button', { name: 'Refresh results' }).click();
    await expect.poll(() => held).toBe(true);
    await page.getByRole('button', { name: 'Retry vote' }).click();
    await expect(card.getByRole('status')).toHaveText('Saved');
    stale.release();
    await page.getByRole('button', { name: 'Refresh results' }).click();
    await expect(page.getByRole('button', { name: `Vote ${next}`, exact: true })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    expect((await (await page.request.get('/api/v1/polls/')).json()).own_choice).toBe(next);
  } finally {
    stale.release();
  }
});

for (const status of [403, 409]) {
  test(`denied/closed vote ${status} never reports saved or offers an unsafe retry`, async ({
    page,
  }) => {
    await enterDemo(page);
    await page.goto('/app/polls');
    await expect(page.locator('.motion-card.current')).toBeVisible();
    const snapshot = await (await page.request.get('/api/v1/polls/')).json();
    await page.route('**/api/v1/polls/*/vote/', (route) =>
      route.fulfill({
        status,
        json: { detail: status === 403 ? 'Sign in required.' : 'This poll is closed.' },
      }),
    );
    await page.route('**/api/v1/polls/', (route) =>
      status === 403
        ? route.fulfill({ status: 403, json: {} })
        : route.fulfill({ json: { ...snapshot, current: null } }),
    );
    await page.getByRole('button', { name: 'Vote Nay', exact: true }).click();
    await expect(page.locator('.motion-card.current')).toHaveCount(0);
    await expect(page.getByText('Saved', { exact: true })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Retry vote' })).toHaveCount(0);
  });
}
