import { useEffect, useState } from 'react';

export class MemberAccessError extends Error {}
export type ReadState<T> =
  { kind: 'loading' } | { kind: 'failed' } | { kind: 'denied' } | { kind: 'ready'; data: T };

/** Same-origin authenticated reads distinguish denied access from transport/contract failures. */
export async function memberJson(url: string, signal: AbortSignal): Promise<unknown> {
  const response = await fetch(url, {
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
    cache: 'no-store',
    signal,
  });
  if ([401, 403].includes(response.status)) throw new MemberAccessError('Member access required');
  if (!response.ok || !response.headers.get('content-type')?.includes('application/json'))
    throw new Error('Member data unavailable');
  return response.json();
}

/** Cancel stale reads, clear previous protected data and bound each attempt to 15 seconds. */
export function useMemberRead<T>(load: (signal: AbortSignal) => Promise<T>) {
  const [state, setState] = useState<ReadState<T>>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 15000);
    setState({ kind: 'loading' });
    load(controller.signal)
      .then((data) => {
        if (active) setState({ kind: 'ready', data });
      })
      .catch((error: unknown) => {
        if (active) setState({ kind: error instanceof MemberAccessError ? 'denied' : 'failed' });
      })
      .finally(() => window.clearTimeout(timer));
    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [load, attempt]);
  return { state, retry: () => setAttempt((value) => value + 1) };
}
