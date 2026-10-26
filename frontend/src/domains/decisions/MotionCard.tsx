import type { ReactNode } from 'react';
import { Card } from '@/components/ui/card';
import type { Motion } from './content';

export function MotionCard({
  motion,
  current = false,
  children,
}: {
  motion: Motion;
  current?: boolean;
  children?: ReactNode;
}) {
  const total = motion.aye + motion.nay;
  const date = new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(motion.ended_at ?? motion.started_at));
  return (
    <Card className={`motion-card p-5 sm:p-7${current ? ' current' : ''}`}>
      <div className="flex items-start justify-between gap-4">
        <h3 className="m-0 text-lg font-semibold leading-normal [overflow-wrap:anywhere]">
          {motion.title}
        </h3>
        <span
          className={`motion-status shrink-0 rounded-full border px-3 py-1 text-xs font-semibold ${current ? 'open border-primary/25 bg-primary/5 text-primary' : 'border-border text-muted-foreground'}`}
        >
          {current ? 'Open' : 'Closed'}
        </span>
      </div>
      <p className="mb-6 mt-2 text-xs text-muted-foreground">
        {current ? 'Opened' : 'Closed'} {date}
      </p>
      <div className="space-y-5">
        {(['Aye', 'Nay'] as const).map((choice) => {
          const count = choice === 'Aye' ? motion.aye : motion.nay;
          const percent = total ? Math.round((count / total) * 100) : 0;
          return (
            <div className="vote-row" key={choice}>
              <div className="mb-2 flex justify-between gap-4 text-sm">
                <strong className="font-medium">{choice}</strong>
                <span className="text-muted-foreground">
                  {count} votes · {percent}%
                </span>
              </div>
              <div
                className="vote-track h-2 overflow-hidden rounded-full bg-muted"
                aria-hidden="true"
              >
                <span
                  className={`block h-full ${choice === 'Aye' ? 'bg-primary' : 'bg-zinc-500'}`}
                  style={{ width: `${percent}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
      <p className="mb-0 mt-4 text-xs text-muted-foreground">
        {total ? `${total} total votes` : 'No votes recorded'}
      </p>
      {children && <div className="mt-6 border-t border-border pt-5">{children}</div>}
    </Card>
  );
}
