import { useEffect, useRef, useState } from 'react';
import { command, CommandError } from '../../api/write';
import { notifySaved } from '../../api/updates';
import { isMotion } from './content';

export type Choice = 'Aye' | 'Nay';
type Sync = {
  phase: 'idle' | 'saving' | 'saved' | 'failed';
  choice: Choice | null;
  error: string;
  retryable: boolean;
};
const idle: Sync = { phase: 'idle', choice: null, error: '', retryable: false };

/** Serialize writes and coalesce rapid changes to the latest intent; never invent a saved vote. */
export function useOptimisticBallot({
  id,
  done,
  preview,
  reconcile,
}: {
  id: number;
  done: (result: unknown) => void;
  preview: (choice: Choice | null) => void;
  reconcile: () => void;
}) {
  const [sync, setSync] = useState<Sync>(idle);
  const queued = useRef<Choice | null>(null);
  const intent = useRef<Choice | null>(null);
  const running = useRef(false);
  const mounted = useRef(true);
  const callbacks = useRef({ done, preview, reconcile });
  callbacks.current = { done, preview, reconcile };
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  async function drain() {
    if (running.current) return;
    running.current = true;
    try {
      while (queued.current) {
        const choice: Choice = queued.current;
        queued.current = null;
        const result = await command(
          `/api/v1/polls/${id}/vote/`,
          'PUT',
          { choice },
          { notify: false },
        );
        if (
          !isMotion(result) ||
          result.id !== id ||
          result.ended_at !== null ||
          !('own_choice' in result) ||
          result.own_choice !== choice
        )
          throw new Error('Unable to confirm your vote. Check results before retrying.');
        if (mounted.current) callbacks.current.done(result);
        notifySaved('polls');
        // The same choice clicked again is already acknowledged; only send a changed intent.
        if (queued.current === choice) queued.current = null;
        if (!queued.current && mounted.current) {
          callbacks.current.preview(null);
          setSync({ phase: 'saved', choice, error: '', retryable: false });
        }
      }
    } catch (error) {
      queued.current = null;
      if (mounted.current) {
        const retryable = !(
          error instanceof CommandError && [401, 403, 404, 409].includes(error.status)
        );
        callbacks.current.preview(null);
        setSync({
          phase: 'failed',
          choice: intent.current,
          error: error instanceof Error ? error.message : 'Vote not saved.',
          retryable,
        });
        callbacks.current.reconcile();
      }
    } finally {
      running.current = false;
    }
  }
  function choose(choice: Choice) {
    intent.current = choice;
    queued.current = choice;
    callbacks.current.preview(choice);
    setSync({ phase: 'saving', choice, error: '', retryable: false });
    void drain();
  }
  return {
    sync,
    choose,
    retry: () => {
      if (sync.choice && sync.retryable) choose(sync.choice);
    },
  };
}
