import { useCallback } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { memberJson, useMemberRead } from '../../api/read';
import { useMember } from '../identity/MemberLayout';
import { isMark, type MarkRecord } from './contracts';
import { MarksFrame } from './MarksFrame';
import { signed, markDate } from './content';

type History = { target_id: number; target_name: string; total: number; marks: MarkRecord[] };
export function MarkHistory() {
  const { userId } = useParams();
  const member = useMember();
  const board = member.roles.some((role) => role.code === 'NM_BOARD');
  const load = useCallback(
    async (signal: AbortSignal): Promise<History> => {
      const data = (await memberJson(`/api/v1/new-members/history/${userId}/`, signal)) as History;
      if (
        !data ||
        !Number.isInteger(data.target_id) ||
        typeof data.target_name !== 'string' ||
        !Number.isInteger(data.total) ||
        !Array.isArray(data.marks) ||
        !data.marks.every((mark) => isMark(mark) && mark.status === 'approved')
      )
        throw new Error('Invalid history.');
      return data;
    },
    [userId],
  );
  const { state, retry } = useMemberRead(load, { resource: 'marks', refreshMs: 3000 });
  return (
    <MarksFrame title="Mark history" legacy={`/newmember/history/${userId}/`}>
      {state.kind === 'ready' && state.stale && (
        <p role="status">
          Updates paused.{' '}
          <Button variant="outline" onClick={retry}>
            Retry
          </Button>
        </p>
      )}
      {state.kind === 'ready' ? (
        <>
          <Card className="mb-6 p-6">
            <h2>{state.data.target_name}</h2>
            <p className="mb-0 text-2xl font-semibold">
              {signed(state.data.total)}{' '}
              <span className="text-sm font-normal text-muted-foreground">approved marks</span>
            </p>
          </Card>
          <div className="grid gap-4">
            {state.data.marks.map((mark) => (
              <Card key={mark.id} className="p-5 sm:p-6" data-mark-id={mark.id}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <h2>{mark.title}</h2>
                  <strong>{signed(mark.value)}</strong>
                </div>
                <p className="text-sm">
                  {markDate(mark.date)} · Submitted by {mark.requester_name}
                </p>
                <p className="mb-0 text-xs text-muted-foreground">
                  Approved by {mark.reviewed_by || 'Not recorded'}
                  {mark.reviewed_at ? ` · ${markDate(mark.reviewed_at.slice(0, 10))}` : ''}
                  {mark.edited_by
                    ? ` · Edited by ${mark.edited_by}${mark.edited_at ? ` (${markDate(mark.edited_at.slice(0, 10))})` : ''}`
                    : ''}
                </p>
                {board && (
                  <Button asChild variant="outline" className="mt-4">
                    <Link
                      to={`/new-members/marks/${mark.id}/edit`}
                      aria-label={`Edit ${mark.title}`}
                    >
                      Edit mark
                    </Link>
                  </Button>
                )}
              </Card>
            ))}
            {!state.data.marks.length && <Card className="p-6">No approved marks.</Card>}
          </div>
        </>
      ) : (
        <p role={state.kind === 'loading' ? 'status' : 'alert'}>
          {state.kind === 'loading'
            ? 'Loading history…'
            : 'Mark history is unavailable or access is denied.'}{' '}
          {state.kind === 'failed' && (
            <Button variant="outline" onClick={retry}>
              Try again
            </Button>
          )}
        </p>
      )}
    </MarksFrame>
  );
}
