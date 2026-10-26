import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useMemberRead } from '../../api/read';
import { command } from '../../api/write';
import { isMark, readReview, type MarkRecord } from './contracts';
import { MarksFrame, MarksIcon } from './MarksFrame';
import { signed, markDate } from './content';

export function MarkReview() {
  const { state, retry, update } = useMemberRead(readReview, {
    resource: 'marks',
    refreshMs: 3000,
  });
  const [busy, setBusy] = useState<number | null>(null),
    [error, setError] = useState('');
  const pending = useRef(false);
  async function decide(mark: MarkRecord, action: 'approve' | 'deny') {
    if (pending.current) return;
    pending.current = true;
    setBusy(mark.id);
    setError('');
    try {
      const result = await command(`/api/v1/new-members/${mark.id}/decision/`, 'POST', {
        action,
        revision: mark.revision,
      });
      if (!isMark(result))
        throw new Error('Unable to confirm the decision. Check the queue before retrying.');
      update((rows) => rows.filter((row) => row.id !== mark.id));
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Unable to decide this request.');
      retry();
    } finally {
      pending.current = false;
      setBusy(null);
    }
  }
  return (
    <MarksFrame title="Review marks" legacy="/newmember/approve/">
      {error && (
        <p role="alert" className="text-sm text-primary">
          {error}
        </p>
      )}
      {state.kind === 'ready' && state.stale && (
        <p role="status">
          Updates paused.{' '}
          <Button variant="outline" onClick={retry}>
            Retry
          </Button>
        </p>
      )}
      {state.kind === 'ready' ? (
        <div className="grid gap-4">
          {state.data.map((mark) => (
            <Card className="p-5 sm:p-6" key={mark.id} data-mark-id={mark.id}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="mb-2">{mark.title}</h2>
                  <p className="mb-2 text-sm">
                    {mark.target_name} · {signed(mark.value)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {markDate(mark.date)} · Submitted by {mark.requester_name}
                  </p>
                </div>
                <span className="rounded-full border border-border px-3 py-1 text-xs">Pending</span>
              </div>
              <div className="flex flex-wrap gap-3">
                <Button
                  disabled={busy !== null}
                  aria-label={`Approve ${mark.title} for ${mark.target_name}`}
                  onClick={() => void decide(mark, 'approve')}
                >
                  <MarksIcon kind="review" />
                  {busy === mark.id ? 'Saving…' : 'Approve'}
                </Button>
                <Button
                  variant="outline"
                  disabled={busy !== null}
                  aria-label={`Deny ${mark.title} for ${mark.target_name}`}
                  onClick={() => void decide(mark, 'deny')}
                >
                  Deny
                </Button>
                <Button asChild variant="ghost">
                  <Link to={`/new-members/marks/${mark.id}/edit`}>Edit</Link>
                </Button>
              </div>
            </Card>
          ))}
          {!state.data.length && <Card className="p-6">No pending marks.</Card>}
        </div>
      ) : (
        <p role={state.kind === 'loading' ? 'status' : 'alert'}>
          {state.kind === 'loading'
            ? 'Loading requests…'
            : 'Mark review is unavailable or access is denied.'}{' '}
          {state.kind === 'failed' && (
            <Button variant="outline" onClick={retry}>
              Try again
            </Button>
          )}
        </p>
      )}
    </MarksFrame>
  );
}
