import { useState } from 'react';
import { command } from '../../api/write';

export function PollActions({
  id,
  canManage,
  ownChoice,
  done,
}: {
  id: number;
  canManage: boolean;
  ownChoice?: string | null;
  done: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function act(action: 'Aye' | 'Nay' | 'close') {
    setBusy(true);
    setError('');
    try {
      await command(
        `/api/v1/polls/${id}/${action === 'close' ? 'close' : 'vote'}/`,
        action === 'close' ? 'POST' : 'PUT',
        action === 'close' ? {} : { choice: action },
      );
      done();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to save vote.');
    } finally {
      setBusy(false);
    }
  }
  return (
    <section aria-label="Your ballot" className="transaction-panel">
      <h3>Vote here in React</h3>
      <p>
        Your current vote:{' '}
        <strong>{ownChoice === 'Aye' || ownChoice === 'Nay' ? ownChoice : 'Not cast'}</strong>
      </p>
      <div className="transaction-actions">
        <button disabled={busy} aria-pressed={ownChoice === 'Aye'} onClick={() => void act('Aye')}>
          Vote Aye
        </button>
        <button disabled={busy} aria-pressed={ownChoice === 'Nay'} onClick={() => void act('Nay')}>
          Vote Nay
        </button>
        {canManage && (
          <button
            disabled={busy}
            onClick={() => {
              if (window.confirm('Close this motion and save its final results?'))
                void act('close');
            }}
          >
            Close motion
          </button>
        )}
      </div>
      {busy && <p role="status">Saving…</p>}
      {error && <p role="alert">{error}</p>}
    </section>
  );
}

export function CreateMotion({ done }: { done: () => void }) {
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
          await command('/api/v1/polls/', 'POST', { title });
          setTitle('');
          done();
        } catch (e) {
          setError(e instanceof Error ? e.message : 'Unable to create motion.');
        } finally {
          setBusy(false);
        }
      }}
    >
      <label htmlFor="motion-title">Motion title</label>
      <input
        id="motion-title"
        required
        maxLength={200}
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <button disabled={busy}>Open motion</button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
