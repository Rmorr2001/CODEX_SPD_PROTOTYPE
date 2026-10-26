import { useCallback } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { ServiceNavigation } from './ServiceNavigation';
import { useMember } from '../identity/MemberLayout';
import { memberJson, useMemberRead } from '../../api/read';
import { serviceRecord, type ServiceRecord } from './transactions';

export function ServiceHistory() {
  const member = useMember();
  const canEdit = member.roles.some((role) => role.code === 'PHIL_CHAIR');
  const { userId } = useParams();
  const load = useCallback(
    async (signal: AbortSignal) => {
      const value = await memberJson(
        `/api/v1/service/history/${userId ? `${userId}/` : ''}`,
        signal,
      );
      const data = value as { events?: unknown; approved_hours?: unknown };
      if (
        !data ||
        !Array.isArray(data.events) ||
        !data.events.every(serviceRecord) ||
        typeof data.approved_hours !== 'number'
      )
        throw new Error('Invalid history');
      return data as { events: ServiceRecord[]; approved_hours: number };
    },
    [userId],
  );
  const { state, retry } = useMemberRead(load, { resource: 'service', refreshMs: 3000 });
  return (
    <section>
      <ServiceNavigation />
      <h1>Approved service history</h1>
      {state.kind === 'ready' && state.stale && (
        <p role="status">
          Updates paused. <button onClick={retry}>Retry</button>
        </p>
      )}
      {state.kind === 'ready' ? (
        <>
          <p>Lifetime approved: {state.data.approved_hours} hours</p>
          {state.data.events.map((entry) => (
            <article key={entry.id} className="transaction-panel">
              <h2>{entry.title}</h2>
              <p>
                {entry.date} · {entry.hours} hours · Approved by{' '}
                {entry.reviewed_by || 'Not recorded'}
              </p>
              {canEdit && <Link to={`/service/events/${entry.id}/edit`}>Chair edit</Link>}
            </article>
          ))}
          {!state.data.events.length && <p>No approved service entries.</p>}
        </>
      ) : (
        <p role={state.kind === 'loading' ? 'status' : 'alert'}>
          {state.kind === 'loading' ? 'Loading history…' : 'History unavailable or access denied.'}{' '}
          <button onClick={retry}>Refresh history</button>
        </p>
      )}
    </section>
  );
}

type Chapter = {
  members: { user_id: number; name: string; approved_hours: number }[];
  approved_hours: number;
  average_hours: number;
  members_meeting_goal: number;
};
export function ServiceChapter() {
  const [params, setParams] = useSearchParams();
  const year = params.get('year') || '';
  const load = useCallback(
    async (signal: AbortSignal) => {
      const value = await memberJson(
        `/api/v1/service/chapter/${year ? `?year=${encodeURIComponent(year)}` : ''}`,
        signal,
      );
      const data = value as Chapter;
      if (
        !data ||
        !Number.isFinite(data.approved_hours) ||
        !Number.isFinite(data.average_hours) ||
        !Number.isInteger(data.members_meeting_goal) ||
        !Array.isArray(data.members) ||
        !data.members.every(
          (m) =>
            Number.isInteger(m.user_id) &&
            typeof m.name === 'string' &&
            Number.isFinite(m.approved_hours),
        )
      )
        throw new Error('Invalid chapter totals');
      return data;
    },
    [year],
  );
  const { state, retry } = useMemberRead(load, { resource: 'service', refreshMs: 3000 });
  return (
    <section>
      <ServiceNavigation />
      <h1>Chapter service</h1>
      {state.kind === 'ready' && state.stale && (
        <p role="status">
          Updates paused. <button onClick={retry}>Retry</button>
        </p>
      )}
      <form
        className="transaction-panel"
        onSubmit={(e) => {
          e.preventDefault();
          const data = new FormData(e.currentTarget);
          setParams({ year: String(data.get('year')) });
        }}
      >
        <label htmlFor="report-year">Academic year starting year</label>
        <input
          id="report-year"
          name="year"
          type="number"
          min="1900"
          max={new Date().getFullYear() + 1}
          defaultValue={year}
          required
        />
        <button>View year</button>
      </form>
      {state.kind === 'ready' ? (
        <>
          <p>
            Approved chapter hours: {state.data.approved_hours} · Average:{' '}
            {state.data.average_hours.toFixed(2)} · Members meeting 10 hours:{' '}
            {state.data.members_meeting_goal}
          </p>
          {state.data.members.map((m) => (
            <p key={m.user_id}>
              <Link to={`/service/history/${m.user_id}`}>{m.name}</Link>: {m.approved_hours} hours
            </p>
          ))}
        </>
      ) : (
        <p role={state.kind === 'loading' ? 'status' : 'alert'}>
          {state.kind === 'loading'
            ? 'Loading chapter totals…'
            : 'Chapter totals unavailable or access denied.'}{' '}
          <button onClick={retry}>Refresh totals</button>
        </p>
      )}
    </section>
  );
}
