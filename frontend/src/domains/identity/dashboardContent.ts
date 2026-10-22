import { MemberAccessError } from '../../api/read';
import { safePublicUrl } from '../../api/links';

export type DashboardContent = {
  landing_path: string;
  announcements: { id: number; title: string; content: string; created_at: string }[];
  links: { text: string; url: string }[];
};
export { MemberAccessError } from '../../api/read';

function announcement(value: unknown): value is DashboardContent['announcements'][number] {
  return Boolean(
    value &&
    typeof value === 'object' &&
    'id' in value &&
    Number.isInteger(value.id) &&
    'title' in value &&
    typeof value.title === 'string' &&
    'content' in value &&
    typeof value.content === 'string' &&
    'created_at' in value &&
    typeof value.created_at === 'string' &&
    !Number.isNaN(Date.parse(value.created_at)),
  );
}

/** Auth failures are distinct from service failures so retry never reveals stale protected data. */
export async function fetchDashboard(signal: AbortSignal): Promise<DashboardContent> {
  const response = await fetch('/api/v1/dashboard/', {
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
    cache: 'no-store',
    signal,
  });
  if ([401, 403].includes(response.status)) throw new MemberAccessError('Member access required');
  if (!response.ok || !response.headers.get('content-type')?.includes('application/json'))
    throw new Error('Dashboard unavailable');
  const data: unknown = await response.json();
  if (
    !data ||
    typeof data !== 'object' ||
    !('landing_path' in data) ||
    !['/app/dashboard', '/app/new-members'].includes(String(data.landing_path)) ||
    !('announcements' in data) ||
    !Array.isArray(data.announcements) ||
    !data.announcements.every(announcement) ||
    !('links' in data) ||
    !Array.isArray(data.links) ||
    !data.links.every(
      (link: unknown) =>
        link &&
        typeof link === 'object' &&
        'text' in link &&
        typeof link.text === 'string' &&
        'url' in link &&
        typeof link.url === 'string' &&
        safePublicUrl(link.url),
    )
  )
    throw new Error('Invalid dashboard content');
  return {
    landing_path: String(data.landing_path),
    announcements: data.announcements,
    links: data.links,
  };
}
