import { Link, NavLink, Outlet, useOutletContext } from 'react-router-dom';
import { chapterSite } from '../../app/links';
import { AccessPanel } from './Login';
import { type Member, useSession } from './session';
import './member.css';

export function useMember(): Member {
  return useOutletContext<Member>();
}

export function MemberLayout() {
  const { state, retry } = useSession();
  if (state.kind !== 'ready' || !state.data.authenticated || !state.data.member)
    return <AccessPanel state={state} retry={retry} />;
  const member = state.data.member;
  const initials = member.display_name
    .split(' ')
    .map((name) => name[0])
    .slice(0, 2)
    .join('');
  return (
    <div className="member-shell">
      <a className="skip-link" href="#member-content">
        Skip to content
      </a>
      <aside className="member-sidebar">
        <Link className="member-brand" to="/">
          ΣΦΔ
        </Link>
        <p className="member-chapter">
          Beta-Omicron
          <br />
          <span>Mizzou</span>
        </p>
        <nav aria-label="Member navigation">
          <NavLink to="/dashboard">
            <span className="nav-mark" aria-hidden="true" />
            Dashboard
          </NavLink>
          <NavLink to="/members">
            <span className="nav-mark" aria-hidden="true" />
            Members
          </NavLink>
          {member.capabilities.polls && (
            <a href={`${chapterSite}poll/`}>
              <span className="nav-mark" aria-hidden="true" />
              Polls
            </a>
          )}
          {member.capabilities.service_hours && (
            <a href={`${chapterSite}philanthropy/`}>
              <span className="nav-mark" aria-hidden="true" />
              Service hours
            </a>
          )}
          {member.capabilities.new_members && (
            <a href={`${chapterSite}newmember/marks/`}>
              <span className="nav-mark" aria-hidden="true" />
              New members
            </a>
          )}
          <NavLink to="/profile">
            <span className="nav-mark" aria-hidden="true" />
            Profile
          </NavLink>
        </nav>
        <div className="member-rail-bottom">
          {state.data.demo_enabled && <Link to="/login">Change demo role</Link>}
          <Link to="/">Chapter homepage</Link>
          <Link to="/connection">Connection</Link>
          <a href={`${chapterSite}auth/logout/`}>Sign out</a>
        </div>
        <p className="rail-signature">
          PEOPLE.
          <br />
          PROGRESS.
          <br />A STRONGER TOMORROW.
        </p>
      </aside>
      <div className="member-workspace">
        <header className="member-topbar">
          <span>Member workspace</span>
          <div>
            <span className="avatar-initials" aria-hidden="true">
              {initials}
            </span>
            <span>{member.display_name}</span>
          </div>
        </header>
        <main className="member-main" id="main">
          <div id="member-content">
            <Outlet context={member} />
          </div>
        </main>
        <footer className="member-footer">Sigma Phi Delta · Beta-Omicron Chapter</footer>
      </div>
    </div>
  );
}
