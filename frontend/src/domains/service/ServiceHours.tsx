import { useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { chapterSite } from '../../app/links';
import { useMemberRead } from '../../api/read';
import { fetchService } from './content';
import './service.css';

const labels = { approved: 'Approved', requested: 'Pending', denied: 'Denied' };
function eventDate(date: string) {
  // Date-only events must keep their calendar day across browser time zones.
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${date}T12:00:00Z`));
}

export function ServiceHours() {
  const [params, setParams] = useSearchParams();
  const year = params.get('year');
  const load = useCallback((signal: AbortSignal) => fetchService(year, signal), [year]);
  const { state, retry } = useMemberRead(load);
  if (state.kind === 'loading') return <p role="status">Loading your service hours…</p>;
  if (state.kind === 'denied')
    return (
      <section className="member-notice">
        <h1>Active member access required</h1>
        <p role="alert">
          Service hours are available to active members. Sign in with an eligible account to
          continue.
        </p>
        <Link to="/login">Member sign in</Link>
      </section>
    );
  if (state.kind === 'failed')
    return (
      <section className="member-notice">
        <h1>Service hours are unavailable</h1>
        <p role="alert">We couldn’t load service hours for this academic year. Please try again.</p>
        <button onClick={retry}>Try again</button>
        {year && (
          <Link className="reset-year" to="/service">
            Return to the current academic year
          </Link>
        )}
      </section>
    );
  const data = state.data;
  const pending = data.events.filter((event) => event.status === 'requested').length;
  const history = data.history_url.startsWith('/')
    ? `${chapterSite}${data.history_url.slice(1)}`
    : data.history_url;
  return (
    <>
      <div className="service-heading">
        <div>
          <p className="eyebrow">SERVICE THAT ADDS UP</p>
          <h1>Make your impact count.</h1>
          <p>Give back to the community. Keep track of the work you do.</p>
        </div>
        <a className="button primary" href={`${chapterSite}philanthropy/request/`}>
          Log hours in chapter site
        </a>
      </div>
      <section className="service-summary" aria-labelledby="service-total-title">
        <div>
          <p className="eyebrow">APPROVED SERVICE HOURS</p>
          <h2 id="service-total-title">
            <strong>{data.approved_hours}</strong>
            <span>hours</span>
          </h2>
          <p>
            Recorded for the {data.year}–{data.year + 1} academic year
          </p>
        </div>
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
          <span>July 1 – June 30</span>
        </div>
        <div className="pending-summary">
          <strong>{pending}</strong>
          <span>pending {pending === 1 ? 'request' : 'requests'}</span>
          <p>Awaiting chapter review</p>
        </div>
      </section>
      <div className="service-records-heading">
        <div>
          <h2>Your service hours</h2>
          <p>
            Approved totals include approved entries only. Pending and denied entries remain listed
            below.
          </p>
        </div>
        <a href={history}>View your service history</a>
      </div>
      {data.events.length > 0 && (
        <p id="service-table-hint" className="service-table-hint">
          Scroll horizontally to see hours and status.
        </p>
      )}
      {data.events.length ? (
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
      ) : (
        <section className="service-empty">
          <h2>No service entries for this year.</h2>
          <p>
            Your service records will appear here after they’re submitted through the chapter site.
          </p>
          <a href={`${chapterSite}philanthropy/request/`}>Log your first service hours</a>
        </section>
      )}
      <div className="service-bottom">
        <section>
          <p className="eyebrow">KEEP MAKING A DIFFERENCE</p>
          <h2>Every contribution matters.</h2>
          <p>
            Use the chapter site to submit an event and its hours. You can return here to check its
            review status.
          </p>
          <a href={`${chapterSite}philanthropy/`}>Open the original service dashboard</a>
        </section>
        {data.can_review && (
          <aside className="service-review">
            <p className="eyebrow">PHILANTHROPY CHAIR</p>
            <h2>Review chapter requests</h2>
            <p>Review chapter submissions through the existing approval workflow.</p>
            <a href={`${chapterSite}philanthropy/approve/`}>
              Review service requests in chapter site
            </a>
          </aside>
        )}
      </div>
    </>
  );
}
