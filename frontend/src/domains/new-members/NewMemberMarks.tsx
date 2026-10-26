import { Link } from 'react-router-dom';
import { chapterSite } from '../../app/links';
import { useMemberRead } from '../../api/read';
import { fetchMarks } from './content';
import { ActiveMarks, PersonalMarks } from './MarksPanels';
import './marks.css';
import './marks-responsive.css';

export function NewMemberMarks() {
  const { state, retry } = useMemberRead(fetchMarks);
  if (state.kind === 'loading')
    return (
      <section className="member-notice">
        <p role="status">Loading new-member marks…</p>
      </section>
    );
  if (state.kind === 'denied')
    return (
      <section className="member-notice">
        <h1>Member access required</h1>
        <p role="alert">
          New-member tools are available to new members, active members and the new-member board.
        </p>
        <Link to="/login">Sign in with your chapter account</Link>
      </section>
    );
  if (state.kind === 'failed')
    return (
      <section className="member-notice">
        <h1>New-member marks</h1>
        <p role="alert">We couldn’t load new-member marks. Please try again.</p>
        <button className="button primary" onClick={retry}>
          Try again
        </button>
      </section>
    );
  const data = state.data;
  return (
    <>
      <section className="marks-heading">
        <div>
          <h1>New-member marks</h1>
        </div>
        {data.can_submit && (
          <a className="button primary" href={`${chapterSite}newmember/request/`}>
            Submit marks in chapter site
          </a>
        )}
      </section>
      {data.personal && <PersonalMarks personal={data.personal} />}
      {data.analytics && <ActiveMarks data={data} />}
      {data.can_review && (
        <section className="marks-review">
          <div>
            <h2>Review mark requests</h2>
          </div>
          <a className="button primary" href={`${chapterSite}newmember/approve/`}>
            Review marks in chapter site
          </a>
        </section>
      )}
      <footer className="marks-footer">
        <a href={`${chapterSite}newmember/`}>Explore new-member resources in chapter site</a>
      </footer>
    </>
  );
}
