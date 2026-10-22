import { safePublicUrl } from '../../api/links';
import { chapterSite } from '../../app/links';

export type HomeContent = { banner_image: string | null; rush_interest_url: string | null };

/** Read only whitelisted public content; malformed contracts fail without replacing the page. */
export async function fetchHome(signal: AbortSignal): Promise<HomeContent> {
  const response = await fetch('/api/v1/public/home/', {
    headers: { Accept: 'application/json' },
    signal,
  });
  if (!response.ok || !response.headers.get('content-type')?.includes('application/json'))
    throw new Error('Public content unavailable');
  const data: unknown = await response.json();
  if (
    !data ||
    typeof data !== 'object' ||
    !('banner_image' in data) ||
    !('rush_interest_url' in data) ||
    !safePublicUrl(data.banner_image) ||
    !safePublicUrl(data.rush_interest_url)
  )
    throw new Error('Invalid public content');
  return { banner_image: data.banner_image, rush_interest_url: data.rush_interest_url };
}

/** Vite and Django have separate origins in development; built URLs stay same-origin. */
export function publicAsset(path: string): string {
  return path.startsWith('/') ? `${chapterSite}${path.slice(1)}` : path;
}
