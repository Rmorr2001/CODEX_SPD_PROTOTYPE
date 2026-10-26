import { Link } from 'react-router-dom';
import { chapterSite } from '../../app/links';
import { useLiveDecisions } from './useLiveDecisions';
import { CreateMotion, PollActions } from './PollActions';
import { MotionCard } from './MotionCard';
import './decisions.css';

export function Decisions() {
  const { state, retry } = useLiveDecisions();
  if (state.kind === 'loading') return <p role="status">Loading chapter decisions…</p>;
  if (state.kind === 'denied')
    return (
      <section className="member-notice">
        <h1>Active member access required</h1>
        <p role="alert">
          Chapter decisions are available to active members. Sign in with an eligible account to
          continue.
        </p>
        <Link to="/login">Member sign in</Link>
      </section>
    );
  if (state.kind === 'failed')
    return (
      <section className="member-notice">
        <h1>Chapter decisions are unavailable</h1>
        <p role="alert">We couldn’t load the motion results. Please try again.</p>
        <button onClick={retry}>Try again</button>
      </section>
    );
  const { current, closed, can_manage, own_choice } = state.data;
  return (
    <>
      <div className="decisions-heading">
        <div>
          <p className="eyebrow">THE CHAPTER, MOVING FORWARD</p>
          <h1>Chapter decisions.</h1>
          <p>A stronger chapter starts with a voice in its future.</p>
        </div>
        <button className="refresh-results" onClick={retry}>
          Refresh results
        </button>
      </div>
      <div className="decisions-layout">
        <div>
          <section className="decisions-section" aria-labelledby="current-motion-title">
            <div className="decisions-section-title">
              <h2 id="current-motion-title">Current motion</h2>
              <span>{current ? '1 open motion' : 'No open motion'}</span>
            </div>
            {current ? (
              <>
                <MotionCard motion={current} current />
                <Link to={`/polls/${current.id}`}>Motion details</Link>
                <PollActions
                  id={current.id}
                  ownChoice={own_choice}
                  canManage={can_manage}
                  done={retry}
                />
                <a className="button primary vote-action" href={`${chapterSite}poll/`}>
                  Vote in chapter site
                </a>
              </>
            ) : (
              <div className="motion-empty">
                <h3>The floor is clear.</h3>
                <p>
                  There is no open motion right now. Check back after the chapter opens its next
                  vote.
                </p>
              </div>
            )}
          </section>
          <section className="decisions-section" aria-labelledby="closed-motion-title">
            <div className="decisions-section-title">
              <h2 id="closed-motion-title">Recent results</h2>
              <span>{closed.length} closed motions</span>
            </div>
            {closed.length ? (
              <div className="closed-motion-list">
                {closed.map((motion) => (
                  <div key={motion.id}>
                    <MotionCard motion={motion} />
                    <Link to={`/polls/${motion.id}`}>View motion details</Link>
                  </div>
                ))}
              </div>
            ) : (
              <p className="motion-empty">No closed motions have been recorded yet.</p>
            )}
          </section>
        </div>
        <aside className="decisions-info">
          <p className="eyebrow">YOUR VOICE MATTERS</p>
          <h2>Stay part of the conversation.</h2>
          <p>
            Current tallies use the chapter’s current vote records. Closed motions show saved final
            totals.
          </p>
          <p>Results refresh every five seconds while this page is visible.</p>
          <a href={`${chapterSite}poll/past_polls/`}>View past polls in chapter site</a>
          {can_manage && (
            <div className="motion-management">
              <span className="eyebrow">EXECUTIVE TOOLS</span>
              <p>One chapter motion can be open at a time.</p>
              {!current && <CreateMotion done={retry} />}
              <a href={`${chapterSite}poll/start_vote/`}>Create a motion in chapter site</a>
            </div>
          )}
        </aside>
      </div>
    </>
  );
}
