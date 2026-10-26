import { expect, test, type Page } from '@playwright/test';
import { enterDemo } from '../../identity/test/helpers';

type MarkRow = {
  id: number;
  target_id: number;
  title: string;
  value: number;
  status: string;
  revision: string;
  reviewed_at: string | null;
  requester_id: number;
};
async function form(page: Page, title: string, value: string, names = ['Cameron Example']) {
  await page.goto('/app/new-members/new');
  for (const name of names) await page.getByRole('checkbox', { name, exact: true }).check();
  await page.getByLabel('Marks', { exact: true }).fill(value);
  await page.getByLabel('Reason', { exact: true }).fill(title);
}
async function save(page: Page) {
  const response = page.waitForResponse(
    (r) => r.url().endsWith('/new-members/submissions/') && r.request().method() === 'POST',
  );
  await page.getByRole('button', { name: 'Submit marks', exact: true }).click();
  const rows: MarkRow[] = await (await response).json();
  await expect(page).toHaveURL(/\/app\/new-members\?submitted=1$/);
  return rows;
}

test('ACTIVE batch, legacy approval, React denial, personal totals and role boundaries share real data', async ({
  page,
  browser,
}) => {
  await enterDemo(page);
  const context = await browser.newContext();
  const personalContext = await browser.newContext();
  try {
    const chair = await context.newPage();
    await enterDemo(chair, 'executive');
    const personal = await personalContext.newPage();
    await enterDemo(personal, 'newmember');
    const before = await (await personal.request.get('/api/v1/new-members/')).json();
    await form(page, 'Browser signed batch', '-2', ['Cameron Example', 'Drew Sample']);
    const rows = await save(page);
    expect(rows).toHaveLength(2);
    expect(rows.every((row) => row.status === 'requested' && row.value === -2)).toBeTruthy();
    const cameronId = Number(before.personal.history_url.split('/').filter(Boolean).at(-1));
    const cameron = rows.find((row) => row.target_id === cameronId)!;
    const drew = rows.find((row) => row.id !== cameron.id)!;
    await chair.goto('/newmember/approve/');
    const legacy = chair
      .locator('table tbody tr')
      .filter({ hasText: 'Browser signed batch' })
      .filter({ hasText: 'Cameron Example' });
    await legacy.getByRole('button', { name: 'Approve', exact: true }).click();
    await expect(personal.locator('.marks-total strong')).toHaveText(
      String(before.personal.total_marks - 2).replace(/^(\d)/, '+$1'),
      { timeout: 10000 },
    );
    await personal.getByRole('link', { name: 'View your history', exact: true }).click();
    await expect(
      personal.getByRole('heading', { name: 'Browser signed batch', exact: true }),
    ).toBeVisible();
    await expect(
      personal
        .getByRole('navigation', { name: 'Marks tools' })
        .getByRole('link', { name: 'Legacy view', exact: true }),
    ).toHaveAttribute('href', `/newmember/history/${cameron.target_id}/`);
    await chair.goto('/app/new-members/review');
    await chair
      .locator(`[data-mark-id="${drew.id}"]`)
      .getByRole('button', { name: 'Deny Browser signed batch for Drew Sample', exact: true })
      .click();
    await expect(chair.locator(`[data-mark-id="${drew.id}"]`)).toHaveCount(0);
    await expect(
      page
        .locator('.marks-submission-list li')
        .filter({ hasText: 'Drew Sample' })
        .filter({ hasText: 'Browser signed batch' }),
    ).toContainText('Denied', { timeout: 10000 });
    await page.goto('/newmember/marks/');
    await expect(page.getByRole('link', { name: 'Review Pending Marks', exact: true })).toHaveCount(
      0,
    );
    await page.goto('/app/new-members/review');
    await expect(page.getByRole('alert')).toContainText('access is denied');
    expect(
      (
        await page.request.post(`/api/v1/new-members/${drew.id}/decision/`, {
          data: { action: 'approve', revision: drew.revision },
        })
      ).status(),
    ).toBe(403);
    await personal.goto('/app/new-members/new');
    await expect(personal.getByRole('alert')).toContainText('Your role cannot');
  } finally {
    await context.close();
    await personalContext.close();
  }
});

test('board auto-approval, retarget/edit, stale form recovery, educator denial and workbook download work in React', async ({
  page,
  browser,
}) => {
  await enterDemo(page, 'executive');
  await form(page, 'Browser board zero', '0');
  const [created] = await save(page);
  expect(created.status).toBe('approved');
  const options = await (await page.request.get('/api/v1/new-members/options/')).json();
  const drew = options.targets.find((target: { name: string }) => target.name === 'Drew Sample');
  const context = await browser.newContext();
  try {
    const stale = await context.newPage();
    await enterDemo(stale, 'executive');
    await stale.goto(`/app/new-members/marks/${created.id}/edit`);
    await expect(stale.getByLabel('Reason', { exact: true })).toHaveValue('Browser board zero');
    await page.goto(`/app/new-members/marks/${created.id}/edit`);
    await page.getByLabel('Recipient', { exact: true }).selectOption(String(drew.id));
    await page.getByLabel('Marks', { exact: true }).fill('4');
    await page.getByLabel('Reason', { exact: true }).fill('Browser board edited');
    await page.getByRole('button', { name: 'Save mark', exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`/app/new-members/history/${drew.id}\\?saved=1$`));
    const edited = await (await page.request.get(`/api/v1/new-members/${created.id}/`)).json();
    expect([edited.reviewed_at, edited.requester_id, edited.status]).toEqual([
      created.reviewed_at,
      created.requester_id,
      'approved',
    ]);
    expect(edited.target_id).toBe(drew.id);
    expect(edited.edited_by).toBe('Alex Example');
    await stale.getByLabel('Marks', { exact: true }).fill('9');
    await stale.getByRole('button', { name: 'Save mark', exact: true }).click();
    await expect(stale.getByRole('alert')).toContainText('changed');
    await expect(stale.getByLabel('Marks', { exact: true })).toHaveValue('9');
    stale.once('dialog', (dialog) => dialog.accept());
    await stale.getByRole('button', { name: 'Reload mark', exact: true }).click();
    await expect(stale.getByLabel('Marks', { exact: true })).toHaveValue('4');
    await expect(stale.getByLabel('Recipient', { exact: true })).toHaveValue(String(drew.id));
    await page.goto(`/newmember/history/${drew.id}/`);
    await expect(
      page.getByRole('cell', { name: 'Browser board edited', exact: true }),
    ).toBeVisible();
    await page.goto(`/app/new-members/marks/${created.id}/edit`);
    page.once('dialog', (dialog) => dialog.accept());
    await page.getByRole('button', { name: 'Deny mark', exact: true }).click();
    await expect(page).toHaveURL(/\/app\/new-members\?submitted=1$/);
    expect(
      (await (await page.request.get(`/api/v1/new-members/${created.id}/`)).json()).status,
    ).toBe('denied');
    await page.goto(`/app/new-members/history/${drew.id}`);
    await expect(
      page.getByRole('heading', { name: 'Browser board edited', exact: true }),
    ).toHaveCount(0);
    await page.getByRole('link', { name: 'Export marks', exact: true }).click();
    for (const pclass of ['Current', 'Beta Omicron']) {
      await page.getByLabel('Class', { exact: true }).selectOption(pclass);
      const download = page.waitForEvent('download');
      await page.getByRole('button', { name: 'Download marks', exact: true }).click();
      expect((await download).suggestedFilename()).toBe(
        `Approved_${pclass}_Class_Newmember_Marks.xlsx`,
      );
    }
  } finally {
    await context.close();
  }
});

test('interrupted acknowledgement replays one operation, repeated clicks and dirty navigation preserve the draft at 390px', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await enterDemo(page);
  await form(page, 'Browser interrupted marks', '1');
  page.once('dialog', (dialog) => dialog.dismiss());
  await page.getByRole('button', { name: 'Cancel', exact: true }).click();
  await expect(page.getByLabel('Reason', { exact: true })).toHaveValue('Browser interrupted marks');
  let requests = 0,
    ids: number[] = [];
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route('**/api/v1/new-members/submissions/', async (route) => {
    requests++;
    const actual = await route.fetch();
    ids = (await actual.json()).map((row: MarkRow) => row.id);
    await gate;
    await route.fulfill({
      status: 503,
      json: { detail: 'Acknowledgement interrupted. Check before retrying.' },
    });
  });
  try {
    await page
      .getByRole('button', { name: 'Submit marks', exact: true })
      .evaluate((button: HTMLButtonElement) => {
        button.click();
        button.click();
      });
    await expect.poll(() => ids.length).toBe(1);
    await expect(page.getByRole('button', { name: 'Saving…' })).toBeDisabled();
    expect(requests).toBe(1);
  } finally {
    release();
  }
  await expect(page.getByRole('alert')).toContainText('Acknowledgement interrupted');
  await expect(page.getByLabel('Reason', { exact: true })).toHaveValue('Browser interrupted marks');
  await expect(page.getByRole('checkbox', { name: 'Cameron Example', exact: true })).toBeChecked();
  await page.unroute('**/api/v1/new-members/submissions/');
  const replay = await save(page);
  expect(replay.map((row) => row.id)).toEqual(ids);
  const own = await (await page.request.get('/api/v1/new-members/')).json();
  expect(
    own.submissions.filter((row: MarkRow) => row.title === 'Browser interrupted marks'),
  ).toHaveLength(1);
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
  await page.getByRole('link', { name: 'Submit marks', exact: true }).click();
  await expect(page.getByLabel('Reason', { exact: true })).toHaveValue('');
  await page.getByRole('checkbox', { name: 'Cameron Example', exact: true }).check();
  await page.getByLabel('Marks', { exact: true }).fill('1.5');
  await page.getByLabel('Reason', { exact: true }).fill('Not a whole mark');
  await page.getByRole('button', { name: 'Submit marks', exact: true }).click();
  expect(
    await page
      .getByLabel('Marks', { exact: true })
      .evaluate((input: HTMLInputElement) => input.validity.stepMismatch),
  ).toBeTruthy();
});
