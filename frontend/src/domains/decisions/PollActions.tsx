import { useRef, useState } from 'react';
import { command } from '../../api/write';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useOptimisticBallot, type Choice } from './useOptimisticBallot';

export function PollActions({
  id,
  canManage,
  ownChoice,
  done,
  preview,
  reconcile,
}: {
  id: number;
  canManage: boolean;
  ownChoice?: string | null;
  done: (result: unknown) => void;
  preview: (choice: Choice | null) => void;
  reconcile: () => void;
}) {
  const { sync, choose, retry } = useOptimisticBallot({ id, done, preview, reconcile });
  const [closing, setClosing] = useState(false);
  const [closeError, setCloseError] = useState('');
  const closingRef = useRef(false);
  const selected = sync.phase === 'saving' ? sync.choice : ownChoice;
  async function close() {
    if (closingRef.current || sync.phase === 'saving') return;
    if (!window.confirm('Close this motion and save its final results?')) return;
    closingRef.current = true;
    setClosing(true);
    setCloseError('');
    try {
      done(await command(`/api/v1/polls/${id}/close/`, 'POST'));
    } catch (error) {
      setCloseError(error instanceof Error ? error.message : 'Unable to close poll.');
      reconcile();
    } finally {
      closingRef.current = false;
      setClosing(false);
    }
  }
  const phaseLabel = closing
    ? 'Closing…'
    : sync.phase === 'saving'
      ? 'Saving…'
      : sync.phase === 'saved'
        ? 'Saved'
        : sync.phase === 'failed'
          ? 'Not synced'
          : '';
  return (
    <section aria-label="Your ballot" className="space-y-4">
      <div className="flex min-h-7 flex-wrap items-center justify-between gap-x-4 gap-y-1">
        <span>
          Your vote:{' '}
          <strong>{selected === 'Aye' || selected === 'Nay' ? selected : 'Not cast'}</strong>
        </span>
        <span
          role={phaseLabel ? 'status' : undefined}
          title={sync.phase === 'saved' ? 'Saved to the database' : undefined}
          className={`inline-flex items-center gap-2 text-xs ${sync.phase === 'failed' ? 'text-primary' : 'text-muted-foreground'}`}
        >
          {phaseLabel && (
            <span
              aria-hidden="true"
              className={`h-2 w-2 rounded-full ${sync.phase === 'saved' ? 'bg-emerald-600' : sync.phase === 'failed' ? 'bg-primary' : 'bg-amber-500'}`}
            />
          )}
          {phaseLabel}
        </span>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        {(['Aye', 'Nay'] as const).map((choice) => (
          <Button
            key={choice}
            variant="outline"
            className="disabled:opacity-100 aria-pressed:border-primary aria-pressed:bg-primary/5 aria-pressed:text-primary"
            disabled={closing}
            aria-pressed={selected === choice}
            onClick={() => choose(choice)}
          >
            Vote {choice}
          </Button>
        ))}
        {canManage && (
          <Button
            variant="outline"
            className="sm:ml-auto disabled:opacity-100"
            disabled={closing || sync.phase === 'saving'}
            onClick={() => void close()}
          >
            Close poll
          </Button>
        )}
      </div>
      <div className="flex min-h-7 items-start gap-2 text-sm text-primary">
        {(sync.error || closeError) && <span role="alert">{sync.error || closeError}</span>}
        {sync.phase === 'failed' && sync.retryable && (
          <Button variant="ghost" className="min-h-0 shrink-0 p-0 text-sm" onClick={retry}>
            Retry vote
          </Button>
        )}
      </div>
    </section>
  );
}

export function CreateMotion({ done }: { done: (result: unknown) => void }) {
  const [title, setTitle] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  return (
    <form
      className="transaction-panel"
      onSubmit={async (event) => {
        event.preventDefault();
        setBusy(true);
        setError('');
        try {
          const result = await command('/api/v1/polls/', 'POST', { title });
          setTitle('');
          done(result);
        } catch (e) {
          setError(e instanceof Error ? e.message : 'Unable to create motion.');
        } finally {
          setBusy(false);
        }
      }}
    >
      <label htmlFor="motion-title">Motion title</label>
      <Input
        id="motion-title"
        required
        maxLength={200}
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <Button type="submit" disabled={busy}>
        Open motion
      </Button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
