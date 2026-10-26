import { useCallback, useEffect, useRef, useState } from 'react';
import { watchSaved, type Resource } from './updates';

export class MemberAccessError extends Error {}
export type ReadState<T> =
  | { kind: 'loading' }
  | { kind: 'failed' }
  | { kind: 'denied' }
  | { kind: 'ready'; data: T; stale?: boolean };

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

/** Retain confirmed reads during refresh; clear protected data on denial or query changes. */
export function useMemberRead<T>(
  load: (signal: AbortSignal) => Promise<T>,
  options: { resource?: Resource; refreshMs?: number } = {},
) {
  const { resource, refreshMs = 0 } = options;
  const [state, setState] = useState<ReadState<T>>({ kind: 'loading' });
  const refreshRef = useRef<() => void>(() => {});
  useEffect(() => {
    let active = true;
    let running = false;
    let generation = 0;
    let controller: AbortController | null = null;
    setState({ kind: 'loading' });
    async function refresh(force = false) {
      if (!active || (running && !force)) return;
      const requestId = ++generation;
      controller?.abort();
      const current = new AbortController();
      controller = current;
      running = true;
      const timer = window.setTimeout(() => current.abort(), 15000);
      setState((previous) => (previous.kind === 'ready' ? previous : { kind: 'loading' }));
      try {
        const data = await load(current.signal);
        if (active && requestId === generation) setState({ kind: 'ready', data });
      } catch (error) {
        if (active && requestId === generation)
          setState((previous) => {
            if (error instanceof MemberAccessError) return { kind: 'denied' };
            return previous.kind === 'ready' ? { ...previous, stale: true } : { kind: 'failed' };
          });
      } finally {
        window.clearTimeout(timer);
        if (requestId === generation) running = false;
      }
    }
    const forceRefresh = () => void refresh(true);
    const focusRefresh = () => {
      if (!document.hidden) void refresh();
    };
    refreshRef.current = forceRefresh;
    const stopWatching = watchSaved(resource, forceRefresh);
    const interval = refreshMs ? window.setInterval(focusRefresh, refreshMs) : undefined;
    if (refreshMs) {
      window.addEventListener('focus', focusRefresh);
      document.addEventListener('visibilitychange', focusRefresh);
    }
    void refresh();
    return () => {
      active = false;
      controller?.abort();
      stopWatching();
      if (interval) window.clearInterval(interval);
      window.removeEventListener('focus', focusRefresh);
      document.removeEventListener('visibilitychange', focusRefresh);
      refreshRef.current = () => {};
    };
  }, [load, resource, refreshMs]);
  const retry = useCallback(() => refreshRef.current(), []);
  const update = useCallback(
    (merge: (data: T) => T) =>
      setState((previous) =>
        previous.kind === 'ready' ? { ...previous, data: merge(previous.data) } : previous,
      ),
    [],
  );
  return { state, retry, update };
}
