import { expect, test } from '@playwright/test';
import { cn } from '../src/lib/utils';

test('UI class overrides keep conditional states and resolve conflicting spacing', () => {
  expect(cn('px-2 py-1', false && 'hidden', { 'opacity-50': true }, 'px-4')).toBe(
    'py-1 opacity-50 px-4',
  );
  expect(cn('focus:ring-2', 'focus:ring-4', 'disabled:opacity-50')).toBe(
    'focus:ring-4 disabled:opacity-50',
  );
});
