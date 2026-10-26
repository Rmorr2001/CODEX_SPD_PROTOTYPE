import { useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useMemberRead } from '../../api/read';
import { useMember } from '../identity/MemberLayout';
import { Card } from '@/components/ui/card';
import { ServiceQuickEntry } from './ServiceQuickEntry';
import { fetchService, type ServiceContent } from './content';
import './service.css';
import { ServiceNavigation } from './ServiceNavigation';

const labels = { approved: 'Approved', requested: 'Pending', denied: 'Denied' };
function eventDate(date: string) {
  // Date-only events retain their calendar day across browser time zones.
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${date}T12:00:00Z`));
}

function ServiceActivity({ data }: { data: ServiceContent }) {
  return (
    <>
      <div className="service-records-heading">
        <h2>Your activity</h2>
      </div>
      {data.events.length ? (
        <>
          <p id="service-table-hint" className="service-table-hint">
            Scroll horizontally to see hours and status.
          </p>
          <div
            className="service-table-wrap"
            role="region"
            aria-label="Your service hours table"
            aria-describedby="service-table-hint"
            tabIndex={0}
          >
            <table className="service-table">
              <thead>
                <tr>
                  <th scope="col">Event</th>
                  <th scope="col">Date</th>
                  <th scope="col">Hours</th>
                  <th scope="col">Status</th>
                </tr>
              </thead>
              <tbody>
                {data.events.map((event) => (
                  <tr key={event.id}>
                    <th scope="row">{event.title}</th>
                    <td>
                      <time dateTime={event.date}>{eventDate(event.date)}</time>
                    </td>
                    <td>{event.hours}</td>
                    <td>
                      <span className={`service-status ${event.status}`}>
                        <span aria-hidden="true">
                          {event.status === 'approved'
                            ? '+'
                            : event.status === 'requested'
                              ? '…'
                              : '−'}
                        </span>
                        {labels[event.status]}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <Card className="p-6">
          <h2>No service entries for this year.</h2>
        </Card>
      )}
    </>
  );
}

export function ServiceHours() {
  const member = useMember();
  const [params, setParams] = useSearchParams();
  const year = params.get('year');
  const load = useCallback((signal: AbortSignal) => fetchService(year, signal), [year]);
  const { state, retry } = useMemberRead(load, { resource: 'service', refreshMs: 3000 });
  const data = state.kind === 'ready' ? state.data : null;
  return (
    <>
      <header className="service-heading">
        <h1>Service hours</h1>
        {data && (
          <div className="service-year">
            <label htmlFor="academic-year">Academic year</label>
            <select
              id="academic-year"
              value={String(data.year)}
              onChange={(event) => setParams({ year: event.target.value })}
            >
              {data.available_years.map((value) => (
                <option value={value} key={value}>
                  {value}–{value + 1}
                </option>
              ))}
            </select>
          </div>
        )}
      </header>
      <ServiceNavigation />
      {params.get('submitted') === '1' && data && (
        <p role="status">Service hours submitted for review.</p>
      )}
      {state.kind === 'ready' && state.stale && (
        <p role="status">
          Updates paused. <button onClick={retry}>Retry</button>
        </p>
      )}
      <Card className="service-summary">
        <div className="service-summary-data">
          {data && (
            <>
              <div>
                <h2 id="service-total-title">
                  <strong>{data.approved_hours}</strong>
                  <span>approved hours</span>
                </h2>
              </div>
              <div className="pending-summary">
                <strong>
                  {data.events.filter((event) => event.status === 'requested').length}
                </strong>
                <span>pending requests</span>
              </div>
            </>
          )}
          {state.kind === 'loading' && <p role="status">Loading your service hours…</p>}
          {state.kind === 'failed' && (
            <div>
              <h2>Service hours are unavailable</h2>
              <p role="alert">
                We couldn’t load service hours for this academic year. Please try again.
              </p>
              <button onClick={retry}>Try again</button>
              {year && (
                <Link className="reset-year" to="/service">
                  Return to the current academic year
                </Link>
              )}
            </div>
          )}
          {state.kind === 'denied' && (
            <div>
              <h2>Active member access required</h2>
              <p role="alert">Service hours are available to active members.</p>
              <Link to="/login">Member sign in</Link>
            </div>
          )}
        </div>
        {/* Keep the entry mounted through refresh/year changes so reads cannot erase a draft. */}
        {member.capabilities.service_hours && state.kind !== 'denied' && (
          <div className="service-entry-action">
            <ServiceQuickEntry />
          </div>
        )}
      </Card>
      {data && (
        <>
          <ServiceActivity data={data} />
        </>
      )}
    </>
  );
}
