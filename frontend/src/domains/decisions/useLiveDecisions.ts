import { useMemberRead } from '../../api/read';
import { fetchDecisions, isMotion } from './content';

/** Show a confirmed mutation immediately, then reconcile authoritative shared tallies. */
export function useLiveDecisions() {
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
  return { ...query, saved };
}
