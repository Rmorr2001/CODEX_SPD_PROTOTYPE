import { Link } from 'react-router-dom';
import { chapterSite } from '../../app/links';
import { useLiveDecisions } from './useLiveDecisions';
import { CreateMotion, PollActions } from './PollActions';
import { MotionCard } from './MotionCard';
import './decisions.css';

export function Decisions() {
  const { state, retry, saved } = useLiveDecisions();
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
      <div className="decisions-heading">
        <h1>Chapter decisions.</h1>
        <div>
          <button className="refresh-results" onClick={retry}>
            Refresh results
          </button>{' '}
          ·{' '}
          <a href={`${chapterSite}poll/`} aria-label="Legacy poll">
            Legacy
          </a>
        </div>
      </div>
      {state.stale && (
        <p role="status">
          Updates paused. <button onClick={retry}>Retry</button>
        </p>
      )}
      <section className="decisions-section" aria-labelledby="current-motion-title">
        <div className="decisions-section-title">
          <h2 id="current-motion-title">Current motion</h2>
        </div>
        {current ? (
          <>
            <MotionCard motion={current} current />
            <PollActions
              id={current.id}
              ownChoice={own_choice}
              canManage={can_manage}
              done={saved}
            />
          </>
        ) : (
          <div className="motion-empty">
            <p>No open motion.</p>
            {can_manage && <CreateMotion done={saved} />}
          </div>
        )}
      </section>
      <section className="decisions-section" aria-labelledby="closed-motion-title">
        <div className="decisions-section-title">
          <h2 id="closed-motion-title">Recent results</h2>
        </div>
        {closed.length ? (
          <div className="closed-motion-list">
            {closed.map((motion) => (
              <MotionCard motion={motion} key={motion.id} />
            ))}
          </div>
        ) : (
          <p className="motion-empty">No results yet.</p>
        )}
      </section>
    </>
  );
}
