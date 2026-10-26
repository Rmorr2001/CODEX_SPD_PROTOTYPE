import { MarksFrame } from './MarksFrame';
import { useSearchParams } from 'react-router-dom';
import { Link, Navigate } from 'react-router-dom';
import { chapterSite } from '../../app/links';
import { useMemberRead } from '../../api/read';
import { fetchMarks } from './content';
import { ActiveMarks, PersonalMarks } from './MarksPanels';
import './marks.css';
import './marks-responsive.css';

export function NewMemberMarks() {
  const [params] = useSearchParams();
  const { state, retry } = useMemberRead(fetchMarks, { resource: 'marks', refreshMs: 3000 });
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
  if (data.mode === 'review') return <Navigate to="/new-members/review" replace />;
  return (
    <>
      <MarksFrame title="New-member marks" legacy="/newmember/marks/">
        {params.get('submitted') === '1' && <p role="status">Marks saved.</p>}
        {state.stale && (
          <p role="status">
            Updates paused. <button onClick={retry}>Retry</button>
          </p>
        )}
        {data.personal && <PersonalMarks personal={data.personal} />}
        {data.analytics && <ActiveMarks data={data} />}
        <footer className="marks-footer">
          <a href={`${chapterSite}newmember/`}>New-member resources (legacy)</a>
        </footer>
      </MarksFrame>
    </>
  );
}
