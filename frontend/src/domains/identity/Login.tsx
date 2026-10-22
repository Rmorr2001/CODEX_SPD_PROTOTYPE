import { Link } from 'react-router-dom';
import { chapterSite } from '../../app/links';
import { type SessionState, useSession } from './session';
import './identity.css';

function csrfCookie() {
  const cookie = document.cookie.split('; ').find((part) => part.startsWith('csrftoken='));
  try {
    return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : '';
  } catch {
    return '';
  }
}

export function AccessPanel({ state, retry }: { state: SessionState; retry: () => void }) {
  const session = state.kind === 'ready' ? state.data : null;
  const csrf = csrfCookie();
  return (
    <div className="access-page">
      <section className="access-intro">
        <p className="eyebrow">THE CHAPTER, CONNECTED</p>
        <h1>
          Good to have
          <br />
          you here.
        </h1>
        <p>Your people. Your chapter. Everything you need to stay involved.</p>
        <Link to="/">Back to the chapter homepage</Link>
      </section>
      <section className="access-card" aria-labelledby="access-title">
        <p className="eyebrow">MEMBER WORKSPACE</p>
        <h2 id="access-title">Member sign in</h2>
        {state.kind === 'loading' && <p role="status">Checking your session…</p>}
        {state.kind === 'failed' && (
          <>
            <p role="alert">We couldn’t check your session. Please try again.</p>
            <button type="button" onClick={retry}>
              Try again
            </button>
          </>
        )}
        {session?.authenticated && session.profile_available && (
          <>
            <p>
              You’re signed in as <strong>{session.member?.display_name}</strong>.
            </p>
            <Link className="button primary" to={session.landing_path.replace('/app', '')}>
              Open your workspace
            </Link>
          </>
        )}
        {session?.authenticated && !session.profile_available && (
          <>
            <p role="alert">
              Your member profile is unavailable. Please contact your chapter administrator.
            </p>
            <a href={`${chapterSite}auth/logout/`}>Sign out</a>
          </>
        )}
        {session && !session.authenticated && (
          <>
            <p>Use your chapter account to continue.</p>
            <a
              className="button primary"
              href={`${chapterSite}auth/login/?next=%2Fapp%2Fdashboard`}
            >
              Sign in to your chapter account
            </a>
          </>
        )}
        {session?.demo_enabled && (
          <div className="demo-entry">
            <h3>Explore the demo</h3>
            <p>
              Try a chapter role with fictional sample data. Demo changes are shared and may be
              reset.
            </p>
            {import.meta.env.DEV ? (
              <a href={`${chapterSite}app/login`}>Open demo entry on the chapter site</a>
            ) : csrf ? (
              <form action={`${chapterSite}demo/enter/`} method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value={csrf} />
                <input type="hidden" name="next" value="/app/dashboard" />
                <label htmlFor="persona">Explore as</label>
                <select id="persona" name="persona">
                  <option value="executive">Executive member</option>
                  <option value="active">Active member</option>
                  <option value="newmember">New member</option>
                  <option value="alumni">Alumnus</option>
                </select>
                <button className="button primary" type="submit">
                  Enter demo
                </button>
              </form>
            ) : (
              <a href={chapterSite}>Open demo entry on the chapter site</a>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

export function Login() {
  const { state, retry } = useSession();
  return <AccessPanel state={state} retry={retry} />;
}
