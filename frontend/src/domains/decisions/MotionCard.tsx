import type { Motion } from './content';

export function MotionCard({ motion, current = false }: { motion: Motion; current?: boolean }) {
  const total = motion.aye + motion.nay;
  const ayePercent = total ? Math.round((motion.aye / total) * 100) : 0;
  const nayPercent = total ? Math.round((motion.nay / total) * 100) : 0;
  const date = new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(motion.ended_at ?? motion.started_at));
  return (
    <article className={`motion-card${current ? ' current' : ''}`}>
      <div className="motion-top">
        <h3>{motion.title}</h3>
        <span className={`motion-status${current ? ' open' : ''}`}>
          {current ? 'OPEN' : 'CLOSED'}
        </span>
      </div>
      <p className="motion-date">
        {current ? 'Opened' : 'Closed'} {date}
      </p>
      <div className="vote-tallies">
        <div className="vote-row">
          <div>
            <strong>Aye</strong>
            <span>
              {motion.aye} votes · {ayePercent}%
            </span>
          </div>
          <div className="vote-track" aria-hidden="true">
            <span style={{ width: `${ayePercent}%` }} />
          </div>
        </div>
        <div className="vote-row nay">
          <div>
            <strong>Nay</strong>
            <span>
              {motion.nay} votes · {nayPercent}%
            </span>
          </div>
          <div className="vote-track" aria-hidden="true">
            <span style={{ width: `${nayPercent}%` }} />
          </div>
        </div>
      </div>
      <p className="vote-total">{total ? `${total} total votes` : 'No votes recorded'}</p>
    </article>
  );
}
