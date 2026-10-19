import { useEffect, useState } from 'react';
import { fetchStatus } from '../api/client';

type State = { kind: 'loading' } | { kind: 'ready' } | { kind: 'failed' };

export function ServiceConnection() {
  const [state, setState] = useState<State>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let disposed = false;
    setState({ kind: 'loading' });
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    fetchStatus(controller.signal)
      .then(() => {
        if (!disposed) setState({ kind: 'ready' });
      })
      .catch(() => {
        if (!disposed) setState({ kind: 'failed' });
      })
      .finally(() => window.clearTimeout(timeout));
    // Cleanup also prevents a previous request from updating a newly mounted screen.
    return () => {
      disposed = true;
      controller.abort();
      window.clearTimeout(timeout);
    };
  }, [attempt]);

  return (
    <section className="connection" aria-labelledby="connection-title">
      <div className="connection-heading">
        <h2 id="connection-title">Service connection</h2>
        <span className={`indicator ${state.kind}`} aria-hidden="true" />
      </div>
      {state.kind === 'loading' && <p role="status">Checking the chapter service…</p>}
      {state.kind === 'ready' && <p role="status">Connected to the chapter service.</p>}
      {state.kind === 'failed' && (
        <>
          <p role="alert">Unable to reach the chapter service. Please try again.</p>
          <button type="button" onClick={() => setAttempt((value) => value + 1)}>
            Try again
          </button>
        </>
      )}
    </section>
  );
}
