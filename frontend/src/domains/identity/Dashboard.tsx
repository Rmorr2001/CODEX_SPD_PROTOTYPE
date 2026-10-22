import { Navigate } from 'react-router-dom';
import './dashboard.css';
import { useEffect, useState } from 'react';
import { chapterSite } from '../../app/links';
import { fetchDashboard, MemberAccessError, type DashboardContent } from './dashboardContent';
import { useMember } from './MemberLayout';

function originalLink(url: string) {
  return url.startsWith('/') ? `${chapterSite}${url.slice(1)}` : url;
}

export function Dashboard() {
  const member = useMember();
  const [state, setState] = useState<
    | { kind: 'loading' }
    | { kind: 'failed' }
    | { kind: 'denied' }
    | { kind: 'ready'; data: DashboardContent }
  >({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    setState({ kind: 'loading' });
    fetchDashboard(controller.signal)
      .then((data) => {
        if (active) setState({ kind: 'ready', data });
      })
      .catch((error: unknown) => {
        if (active) setState({ kind: error instanceof MemberAccessError ? 'denied' : 'failed' });
      })
      .finally(() => window.clearTimeout(timeout));
    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timeout);
    };
  }, [attempt]);
  if (state.kind === 'loading') return <p role="status">Loading your chapter dashboard…</p>;
  if (state.kind === 'denied')
    return (
      <section className="member-notice">
        <h1>Member access required</h1>
        <p role="alert">
          Your session may have ended or your profile is unavailable. Sign in again to continue.
        </p>
        <a href={`${chapterSite}auth/login/?next=%2Fapp%2Fdashboard`}>
          Sign in to your chapter account
        </a>
      </section>
    );
  if (state.kind === 'failed')
    return (
      <section className="member-notice">
        <h1>Your dashboard is unavailable</h1>
        <p role="alert">We couldn’t load your chapter updates. Please try again.</p>
        <button onClick={() => setAttempt((value) => value + 1)}>Try again</button>
      </section>
    );
  if (state.data.landing_path === '/app/new-members') return <Navigate to="/new-members" replace />;
  return (
    <>
      <div className="dashboard-intro">
        <p className="eyebrow">YOUR CHAPTER AT A GLANCE</p>
        <h1>Welcome back, {member.display_name.split(' ')[0]}.</h1>
        <p>Stay connected to the people and work that move our chapter forward.</p>
      </div>
      <div className="dashboard-summary">
        <article>
          <span className="summary-number">{state.data.announcements.length}</span>
          <h2>Chapter announcements</h2>
          <p>Active updates from your chapter</p>
        </article>
        <article>
          <span className="summary-number">{state.data.links.length}</span>
          <h2>Chapter resources</h2>
          <p>Helpful links selected by the chapter</p>
        </article>
        <article>
          <span className="summary-label">YOUR ROLE</span>
          <h2>
            {member.roles.find((role) => role.code === 'EXEC')?.label ??
              member.roles[0]?.label ??
              'Member'}
          </h2>
          <p>Connected to the Beta-Omicron chapter</p>
        </article>
      </div>
      <div className="dashboard-columns">
        <section className="member-card" aria-labelledby="announcements-title">
          <div className="member-section-heading">
            <h2 id="announcements-title">Announcements</h2>
            <span className="small-tag">CHAPTER UPDATES</span>
          </div>
          {state.data.announcements.length ? (
            state.data.announcements.map((item) => (
              <article className="announcement" key={item.id}>
                <span className="announcement-rule" aria-hidden="true" />
                <div>
                  <h3>{item.title}</h3>
                  <time dateTime={item.created_at}>
                    {new Intl.DateTimeFormat('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    }).format(new Date(item.created_at))}
                  </time>
                  <p>{item.content}</p>
                </div>
              </article>
            ))
          ) : (
            <p className="member-empty">There are no active chapter announcements.</p>
          )}
        </section>
        <section className="member-card" aria-labelledby="resources-title">
          <h2 id="resources-title">Chapter resources</h2>
          <p className="card-intro">Find your next step.</p>
          {state.data.links.length ? (
            <div className="resource-list">
              {state.data.links.map((link, index) => (
                <a href={originalLink(link.url)} key={`${link.url}-${index}`}>
                  {link.text}
                  <span aria-hidden="true">/</span>
                </a>
              ))}
            </div>
          ) : (
            <p className="member-empty">No chapter resources have been published yet.</p>
          )}
          <div className="legacy-tools">
            <p>Looking for your familiar tools?</p>
            <a href={`${chapterSite}auth/dashboard/`}>Open the original chapter dashboard</a>
          </div>
        </section>
      </div>
    </>
  );
}
