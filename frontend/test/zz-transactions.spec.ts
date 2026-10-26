import { expect, test } from '@playwright/test';
import { enterDemo } from '../src/domains/identity/test/helpers';

test.describe('cross-interface transactions', () => {
  test.describe.configure({ mode: 'serial' });

  test('same poll accepts React ballots, legacy changes, and saves final results', async ({
    page,
    browser,
  }) => {
    await enterDemo(page, 'executive');
    await page.goto('/app/polls');
    await expect(
      page.getByRole('heading', { name: 'Chapter decisions.', exact: true }),
    ).toBeVisible();
    page.on('dialog', (dialog) => void dialog.accept());
    if (await page.getByRole('button', { name: 'Close motion', exact: true }).count()) {
      await page.getByRole('button', { name: 'Close motion', exact: true }).click();
    }
    await page.getByLabel('Motion title').fill('Fictional migration demonstration');
    await page.getByRole('button', { name: 'Open motion', exact: true }).click();
    await expect(
      page.getByRole('heading', { name: 'Fictional migration demonstration', exact: true }),
    ).toBeVisible();
    const data = await (await page.request.get('/api/v1/polls/')).json();
    const id = data.current.id;
    const memberContext = await browser.newContext();
    try {
      const member = await memberContext.newPage();
      await enterDemo(member, 'active');
      await member.goto('/app/polls');
      await member.getByRole('button', { name: 'Vote Aye', exact: true }).click();
      await expect(member.getByRole('button', { name: 'Vote Aye', exact: true })).toHaveAttribute(
        'aria-pressed',
        'true',
      );
      await member.goto('/poll/');
      await expect(
        member.getByRole('heading', { name: 'Fictional migration demonstration' }),
      ).toBeVisible();
      await member.getByRole('button', { name: 'Nay', exact: true }).click();
      await member.goto('/app/polls');
      await expect(member.getByRole('button', { name: 'Vote Nay', exact: true })).toHaveAttribute(
        'aria-pressed',
        'true',
      );
      await expect
        .poll(async () => (await (await page.request.get(`/api/v1/polls/${id}/`)).json()).nay)
        .toBe(1);
      await expect(page.getByText('1 votes · 100%', { exact: true })).toBeVisible();
      await page.getByRole('button', { name: 'Close motion', exact: true }).click();
      await expect(page.getByLabel('Motion title')).toBeVisible();
      await member.goto(`/app/polls/${id}`);
      await expect(member.getByText('CLOSED', { exact: true })).toBeVisible();
      await expect(member.getByRole('button', { name: 'Vote Aye', exact: true })).toHaveCount(0);
      await member.goto('/poll/past_polls/');
      await expect(
        member.getByText('Fictional migration demonstration', { exact: true }),
      ).toBeVisible();
    } finally {
      await memberContext.close();
    }
  });

  test('fractional React service request is reviewed through legacy and reflected in React', async ({
    page,
    browser,
  }) => {
    await enterDemo(page, 'active');
    await page.goto('/app/service/new');
    const today = new Date().toISOString().slice(0, 10);
    await page.getByLabel('Event title').fill('Fictional React service 1.75');
    await page.getByLabel('Hours', { exact: true }).fill('1.75');
    await page.getByLabel('Event date').fill(today);
    await page.getByRole('button', { name: 'Submit hours', exact: true }).click();
    await expect(page.getByRole('status')).toHaveText('Service hours submitted for review.');
    const ownRow = page.getByRole('row').filter({ hasText: 'Fictional React service 1.75' });
    await expect(ownRow).toContainText('Pending');
    await expect(ownRow).toContainText('1.75');
    const context = await browser.newContext();
    try {
      const chair = await context.newPage();
      await enterDemo(chair, 'executive');
      await chair.goto('/app/service/review');
      await expect(
        chair.getByRole('heading', { name: 'Fictional React service 1.75', exact: true }),
      ).toBeVisible();
      const queue = await (await chair.request.get('/api/v1/service/review/')).json();
      const entryId = queue.find(
        (entry: { title: string }) => entry.title === 'Fictional React service 1.75',
      ).id;
      await chair.goto('/philanthropy/approve/');
      const row = chair.getByRole('row').filter({ hasText: 'Fictional React service 1.75' });
      await row.getByRole('button', { name: 'Approve', exact: true }).click();
      await page.reload();
      await expect(ownRow).toContainText('Approved');
      await page.getByRole('link', { name: 'View your service history' }).click();
      await expect(
        page.getByRole('heading', { name: 'Fictional React service 1.75', exact: true }),
      ).toBeVisible();
      await chair.goto(`/app/service/events/${entryId}/edit`);
      await expect(chair.getByLabel('Hours', { exact: true })).toHaveValue('1.75');
      await chair.getByLabel('Hours', { exact: true }).fill('2.25');
      await chair.getByRole('button', { name: 'Save service entry', exact: true }).click();
      await expect(chair).toHaveURL(/\/app\/service\/review$/);
      await page.reload();
      await expect(
        page.getByRole('article').filter({ hasText: 'Fictional React service 1.75' }),
      ).toContainText('2.25 hours');
      await page.goto('/app/service/chapter');
      await page.getByRole('link', { name: 'Jordan Sample', exact: true }).click();
      await expect(
        page.getByRole('heading', { name: 'Fictional React service 1.75', exact: true }),
      ).toBeVisible();
      await page.goto('/app/service');
      const downloadPromise = page.waitForEvent('download');
      await page.getByRole('link', { name: 'Download approved hours (XLSX)', exact: true }).click();
      expect((await downloadPromise).suggestedFilename()).toBe('approved_philanthropy_hours.xlsx');
      await chair.goto('/philanthropy/request/');
      await chair.locator('[name="event_title"]').fill('Fictional legacy service 2.25');
      await chair.locator('[name="hours"]').fill('2.25');
      await chair.locator('[name="event_date"]').fill(today);
      await chair.getByRole('button', { name: /Submit/ }).click();
      await chair.goto('/app/service');
      await expect(
        chair.getByRole('row').filter({ hasText: 'Fictional legacy service 2.25' }),
      ).toContainText('2.25');
    } finally {
      await context.close();
    }
  });

  test('React chair approval and denial persist and ordinary members cannot review', async ({
    page,
    browser,
  }) => {
    await enterDemo(page, 'active');
    const today = new Date().toISOString().slice(0, 10);
    for (const title of ['React approval example', 'React denial example']) {
      await page.goto('/app/service/new');
      await page.getByLabel('Event title').fill(title);
      await page.getByLabel('Hours', { exact: true }).fill('0.5');
      await page.getByLabel('Event date').fill(today);
      await page.getByRole('button', { name: 'Submit hours', exact: true }).click();
      await expect(page.getByRole('status')).toHaveText('Service hours submitted for review.');
    }
    const context = await browser.newContext();
    try {
      const chair = await context.newPage();
      await enterDemo(chair, 'executive');
      await chair.goto('/app/service/review');
      await chair
        .getByRole('button', { name: 'Approve React approval example', exact: true })
        .click();
      await expect(
        chair.getByRole('heading', { name: 'React approval example', exact: true }),
      ).toHaveCount(0);
      await chair.getByRole('button', { name: 'Deny React denial example', exact: true }).click();
      await expect(
        chair.getByRole('heading', { name: 'React denial example', exact: true }),
      ).toHaveCount(0);
      await page.goto('/app/service');
      await expect(
        page.getByRole('row').filter({ hasText: 'React approval example' }),
      ).toContainText('Approved');
      await expect(page.getByRole('row').filter({ hasText: 'React denial example' })).toContainText(
        'Denied',
      );
      await page.goto('/app/service/review');
      await expect(page.getByRole('alert')).toHaveText(
        'Active philanthropy chair access required.',
      );
    } finally {
      await context.close();
    }
  });
});
