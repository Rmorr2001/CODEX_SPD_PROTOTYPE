import { Link, useParams } from 'react-router-dom';
import { useCallback } from 'react';
import { memberJson, useMemberRead } from '../../api/read';
import { isMotion, type Motion } from './content';
import { MotionCard } from './MotionCard';
import { PollActions } from './PollActions';

export function PollDetail() {
  const { id } = useParams();
  const load = useCallback(
    async (
      signal: AbortSignal,
    ): Promise<Motion & { own_choice: string | null; can_manage: boolean }> => {
      const result = await memberJson(`/api/v1/polls/${id}/`, signal);
      if (
        !isMotion(result) ||
        !('can_manage' in result) ||
        typeof result.can_manage !== 'boolean' ||
        !('own_choice' in result) ||
        !(result.own_choice === null || typeof result.own_choice === 'string')
      )
        throw new Error('Invalid poll detail');
      return {
        ...result,
        can_manage: Boolean(result.can_manage),
        own_choice: typeof result.own_choice === 'string' ? result.own_choice : null,
      };
    },
    [id],
  );
  const { state, retry } = useMemberRead(load, { resource: 'polls', refreshMs: 3000 });
  return (
    <section>
      <Link to="/polls">All chapter decisions</Link>
      <h1>Motion details</h1>
      {state.kind === 'ready' && state.stale && (
        <p role="status">
          Updates paused. <button onClick={retry}>Retry</button>
        </p>
      )}
      {state.kind === 'loading' && <p role="status">Loading motion…</p>}
      {state.kind === 'denied' && <p role="alert">Active member access required.</p>}
      {state.kind === 'failed' && (
        <p role="alert">
          Motion unavailable. <button onClick={retry}>Try again</button>
        </p>
      )}
      {state.kind === 'ready' && (
        <>
          <MotionCard motion={state.data} current={!state.data.ended_at}>
            {!state.data.ended_at && (
              <PollActions
                id={state.data.id}
                canManage={state.data.can_manage}
                ownChoice={state.data.own_choice}
                done={retry}
              />
            )}
          </MotionCard>
          <button onClick={retry}>Refresh results</button>
        </>
      )}
    </section>
  );
}
