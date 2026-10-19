import { chapterSite } from '../app/links';
import { ServiceConnection } from '../components/ServiceConnection';

export function Workspace() {
  return (
    <>
      <p className="eyebrow">Sigma Phi Delta · Beta Omicron</p>
      <h1>Chapter workspace</h1>
      <p className="intro">
        The new workspace is taking shape. Your existing chapter tools are available on the chapter
        site.
      </p>
      <a className="primary" href={chapterSite}>
        Open chapter site
      </a>
      <div className="workspace-grid">
        <section className="card">
          <p className="eyebrow">Available now</p>
          <h2>Your chapter site</h2>
          <p>
            Continue using the roster, your profile, polls, service hours, and new-member tools.
          </p>
          <a href={`${chapterSite}auth/login/`}>Go to sign in</a>
        </section>
        <ServiceConnection />
      </div>
    </>
  );
}
