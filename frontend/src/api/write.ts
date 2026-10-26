import { notifySaved } from './updates';
/** Same-origin CSRF writes. Failures preserve the form; never automatically retry mutations. */
export function csrfToken(): string {
  const cookie = document.cookie.split('; ').find((part) => part.startsWith('csrftoken='));
  return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : '';
}

export class CommandError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

export async function command(
  url: string,
  method: 'POST' | 'PUT' | 'PATCH',
  data: unknown = {},
  options: { notify?: boolean } = {},
) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(url, {
      method,
      credentials: 'same-origin',
      cache: 'no-store',
      signal: controller.signal,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken(),
      },
      body: JSON.stringify(data),
    });
    if (!response.headers.get('content-type')?.includes('application/json'))
      throw new Error(
        'The service returned an unexpected response. Refresh and check before retrying.',
      );
    const result: unknown = await response.json();
    if (!response.ok) {
      const values =
        result && typeof result === 'object'
          ? Object.values(result)
              .flat()
              .filter((v) => typeof v === 'string')
          : [];
      throw new CommandError(
        values.join(' ') || 'The action could not be completed. Refresh and try again.',
        response.status,
      );
    }
    if (options.notify !== false && url.startsWith('/api/v1/polls/')) notifySaved('polls');
    if (options.notify !== false && url.startsWith('/api/v1/service/')) notifySaved('service');
    return result;
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError')
      throw new Error('The request timed out. Refresh to check its status before retrying.');
    throw error;
  } finally {
    window.clearTimeout(timer);
  }
}
