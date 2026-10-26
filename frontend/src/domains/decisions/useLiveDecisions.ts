import { useEffect, useState } from 'react';
import { MemberAccessError, type ReadState } from '../../api/read';
import { fetchDecisions, type DecisionsContent } from './content';

/** Refresh snapshots without unmounting the active form; no mutation is retried. */
export function useLiveDecisions() {
  const [state, setState] = useState<ReadState<DecisionsContent>>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    let running = false;
    let controller: AbortController | null = null;
    async function load() {
      if (running) return;
      running = true;
      controller = new AbortController();
      const timer = window.setTimeout(() => controller?.abort(), 15000);
      try {
        const data = await fetchDecisions(controller.signal);
        if (active) setState({ kind: 'ready', data });
      } catch (error) {
        if (active) setState({ kind: error instanceof MemberAccessError ? 'denied' : 'failed' });
      } finally {
        running = false;
        window.clearTimeout(timer);
      }
    }
    void load();
    const interval = window.setInterval(() => {
      if (!document.hidden) void load();
    }, 5000);
    return () => {
      active = false;
      controller?.abort();
      window.clearInterval(interval);
    };
  }, [attempt]);
  return { state, retry: () => setAttempt((n) => n + 1) };
}
