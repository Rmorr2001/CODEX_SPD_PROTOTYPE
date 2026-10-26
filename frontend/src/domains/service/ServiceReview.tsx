import { useCallback, useState } from 'react';
import { Link } from 'react-router-dom';
import { useMemberRead } from '../../api/read';
import { command } from '../../api/write';
import { readRecords } from './transactions';

export function ServiceReview() {
  const load = useCallback(
    (signal: AbortSignal) => readRecords('/api/v1/service/review/', signal),
    [],
  );
  const { state, retry } = useMemberRead(load);
  const [busy, setBusy] = useState<number | null>(null);
  const [error, setError] = useState('');
  async function decide(id: number, action: 'approve' | 'deny') {
    setBusy(id);
    setError('');
    try {
      await command(`/api/v1/service/${id}/decision/`, 'POST', { action });
      retry();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to review request.');
    } finally {
      setBusy(null);
    }
  }
  return (
    <section>
      <Link to="/service">Service hours</Link>
      <h1>Review service requests</h1>
      <p>
        Only pending entries can be decided. Self-review and reversal are unavailable pending
        chapter policy.
      </p>
      {state.kind === 'loading' && <p role="status">Loading requests…</p>}
      {state.kind === 'denied' && <p role="alert">Active philanthropy chair access required.</p>}
      {state.kind === 'failed' && (
        <p role="alert">
          Unable to load requests. <button onClick={retry}>Try again</button>
        </p>
      )}
      {state.kind === 'ready' &&
        (state.data.length ? (
          state.data.map((entry) => (
            <article className="transaction-panel" key={entry.id}>
              <h2>{entry.title}</h2>
              <p>
                {entry.owner_name} · {entry.hours} hours · {entry.date}
              </p>
              <div className="transaction-actions">
                <button disabled={busy !== null} onClick={() => void decide(entry.id, 'approve')}>
                  Approve {entry.title}
                </button>
                <button disabled={busy !== null} onClick={() => void decide(entry.id, 'deny')}>
                  Deny {entry.title}
                </button>
                <Link to={`/service/events/${entry.id}/edit`}>Edit entry</Link>
              </div>
            </article>
          ))
        ) : (
          <p>No pending requests.</p>
        ))}
      {error && <p role="alert">{error}</p>}
    </section>
  );
}
