import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useLiveDecisions } from './useLiveDecisions';
import { CreateMotion, PollActions } from './PollActions';
import { MotionCard } from './MotionCard';

export function Decisions() {
  const { state, retry, saved, preview } = useLiveDecisions();
  if (state.kind === 'loading') return <p role="status">Loading polls…</p>;
  if (state.kind === 'denied')
    return (
      <section className="member-notice">
        <h1>Active member access required</h1>
        <Link to="/login">Sign in</Link>
      </section>
    );
  if (state.kind === 'failed')
    return (
      <section className="member-notice">
        <h1>Polls unavailable</h1>
        <p role="alert">Couldn’t load polls.</p>
        <button onClick={retry}>Try again</button>
      </section>
    );
  const { current, closed, can_manage, own_choice } = state.data;
  return (
    <>
      <div className="mb-8 flex items-center justify-between gap-4">
        <h1>Polls</h1>
        <Button variant="outline" onClick={retry}>
          Refresh results
        </Button>
      </div>
      {state.stale && (
        <p role="status">
          Updates paused. <button onClick={retry}>Retry</button>
        </p>
      )}
      <section className="mb-8" aria-labelledby="current-motion-title">
        <div className="mb-4">
          <h2 id="current-motion-title">Current motion</h2>
        </div>
        {current ? (
          <MotionCard motion={current} current>
            <PollActions
              key={current.id}
              id={current.id}
              ownChoice={own_choice}
              canManage={can_manage}
              done={saved}
              preview={(choice) => preview(current.id, choice)}
              reconcile={retry}
            />
          </MotionCard>
        ) : (
          <div className="rounded-xl border border-border bg-white p-6">
            <p>No open motion.</p>
            {can_manage && <CreateMotion done={saved} />}
          </div>
        )}
      </section>
      <section className="mb-8" aria-labelledby="closed-motion-title">
        <div className="mb-4">
          <h2 id="closed-motion-title">Recent results</h2>
        </div>
        {closed.length ? (
          <div className="closed-motion-list grid gap-4">
            {closed.map((motion) => (
              <MotionCard motion={motion} key={motion.id} />
            ))}
          </div>
        ) : (
          <p className="rounded-xl border border-border bg-white p-6">No results yet.</p>
        )}
      </section>
    </>
  );
}
