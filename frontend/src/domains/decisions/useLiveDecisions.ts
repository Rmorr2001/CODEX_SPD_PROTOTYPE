import { useCallback, useState } from 'react';
import { useMemberRead } from '../../api/read';
import { fetchDecisions, isMotion, previewMotion } from './content';

/** Show a confirmed mutation immediately, then reconcile authoritative shared tallies. */
export function useLiveDecisions() {
  const [pending, setPending] = useState<{ id: number; choice: string } | null>(null);
  const preview = useCallback(
    (id: number, choice: string | null) => setPending(choice ? { id, choice } : null),
    [],
  );
  const query = useMemberRead(fetchDecisions, { resource: 'polls', refreshMs: 3000 });
  function saved(result: unknown) {
    if (isMotion(result))
      query.update((data) =>
        result.ended_at
          ? {
              ...data,
              current: data.current?.id === result.id ? null : data.current,
              closed: [result, ...data.closed.filter((motion) => motion.id !== result.id)],
              own_choice: null,
            }
          : {
              ...data,
              current: result,
              own_choice:
                'own_choice' in result && typeof result.own_choice === 'string'
                  ? result.own_choice
                  : null,
            },
      );
  }
  const state = query.state;
  const display =
    state.kind === 'ready' && state.data.current && pending?.id === state.data.current.id
      ? {
          ...state,
          data: {
            ...state.data,
            current: previewMotion(state.data.current, state.data.own_choice, pending.choice),
          },
        }
      : state;
  return { ...query, state: display, saved, preview };
}
