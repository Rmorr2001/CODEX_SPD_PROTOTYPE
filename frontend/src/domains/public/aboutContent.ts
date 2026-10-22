import { safePublicUrl } from './content';

export type Executive = { name: string; position: string; image: string | null };
export type AboutContent = { active_count: number; executives: Executive[] };

function executive(value: unknown): value is Executive {
  return Boolean(
    value &&
    typeof value === 'object' &&
    'name' in value &&
    typeof value.name === 'string' &&
    'position' in value &&
    typeof value.position === 'string' &&
    'image' in value &&
    safePublicUrl(value.image),
  );
}

/** Only accept the public chapter-card contract; missing or malformed data triggers retry UI. */
export async function fetchAbout(signal: AbortSignal): Promise<AboutContent> {
  const response = await fetch('/api/v1/public/about/', {
    headers: { Accept: 'application/json' },
    signal,
  });
  if (!response.ok || !response.headers.get('content-type')?.includes('application/json'))
    throw new Error('Chapter data unavailable');
  const value: unknown = await response.json();
  if (
    !value ||
    typeof value !== 'object' ||
    !('active_count' in value) ||
    !Number.isInteger(value.active_count) ||
    typeof value.active_count !== 'number' ||
    value.active_count < 0 ||
    !('executives' in value) ||
    !Array.isArray(value.executives) ||
    !value.executives.every(executive)
  )
    throw new Error('Invalid chapter data');
  return { active_count: value.active_count, executives: value.executives };
}
