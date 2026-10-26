import { useState } from 'react';
import { command } from '../../api/write';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function PollActions({
  id,
  canManage,
  ownChoice,
  done,
}: {
  id: number;
  canManage: boolean;
  ownChoice?: string | null;
  done: (result: unknown) => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function act(action: 'Aye' | 'Nay' | 'close') {
    setBusy(true);
    setError('');
    try {
      const result = await command(
        `/api/v1/polls/${id}/${action === 'close' ? 'close' : 'vote'}/`,
        action === 'close' ? 'POST' : 'PUT',
        action === 'close' ? {} : { choice: action },
      );
      done(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to save vote.');
    } finally {
      setBusy(false);
    }
  }
  return (
    <section aria-label="Your ballot" className="space-y-4">
      <p>
        Your vote:{' '}
        <strong>{ownChoice === 'Aye' || ownChoice === 'Nay' ? ownChoice : 'Not cast'}</strong>
      </p>
      <div className="flex flex-wrap items-center gap-3">
        <Button
          variant="outline"
          className="aria-pressed:border-primary aria-pressed:bg-primary/5 aria-pressed:text-primary"
          disabled={busy}
          aria-pressed={ownChoice === 'Aye'}
          onClick={() => void act('Aye')}
        >
          Vote Aye
        </Button>
        <Button
          variant="outline"
          className="aria-pressed:border-primary aria-pressed:bg-primary/5 aria-pressed:text-primary"
          disabled={busy}
          aria-pressed={ownChoice === 'Nay'}
          onClick={() => void act('Nay')}
        >
          Vote Nay
        </Button>
        {canManage && (
          <Button
            variant="outline"
            className="sm:ml-auto"
            disabled={busy}
            onClick={() => {
              if (window.confirm('Close this motion and save its final results?'))
                void act('close');
            }}
          >
            Close poll
          </Button>
        )}
      </div>
      {busy && <p role="status">Saving…</p>}
      {error && <p role="alert">{error}</p>}
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
