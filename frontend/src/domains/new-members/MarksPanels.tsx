import { type MarksContent, type Mark, markDate, signed } from './content';
import { Link } from 'react-router-dom';
import { historyPath } from './contracts';

export function MarkList({ marks, empty }: { marks: Mark[]; empty: string }) {
  if (!marks.length) return <p className="marks-empty">{empty}</p>;
  return (
    <ol className="marks-history">
      {marks.map((mark) => (
        <li key={mark.id}>
          <span className={`mark-value ${mark.value < 0 ? 'negative' : ''}`}>
            {signed(mark.value)}
            <span>marks</span>
          </span>
          <div>
            <h3>{mark.title}</h3>
            <time dateTime={mark.date}>{markDate(mark.date)}</time>
            <span className={`mark-status ${mark.status}`}>
              {mark.status === 'requested'
                ? 'Pending'
                : mark.status === 'approved'
                  ? 'Approved'
                  : 'Denied'}
            </span>
          </div>
        </li>
      ))}
    </ol>
  );
}

export function PersonalMarks({ personal }: { personal: NonNullable<MarksContent['personal']> }) {
  return (
    <>
      <section className="marks-personal-summary" aria-labelledby="personal-marks-title">
        <div className="marks-total">
          <p id="personal-marks-title">Approved marks</p>
          <strong>{signed(personal.total_marks)}</strong>
        </div>
        <div className="marks-standing">
          <h2>{personal.standing}</h2>
          <Link to={historyPath(personal.history_url)}>View your history</Link>
        </div>
        <div className="marks-class-average">
          <strong>{personal.class_average}</strong>
          <span>Current class average</span>
          <p>Approved marks per new member</p>
        </div>
      </section>
      <div className="marks-personal-grid">
        <section className="marks-card" id="approved-marks">
          <div className="marks-card-title">
            <h2>Your approved history</h2>
            <span>{personal.history.length} entries</span>
          </div>
          <MarkList marks={personal.history} empty="You don’t have any approved marks yet." />
        </section>
      </div>
    </>
  );
}

export function ActiveMarks({ data }: { data: MarksContent }) {
  const analytics = data.analytics!;
  return (
    <>
      <section className="marks-analytics" aria-label="Current class approved marks">
        <div>
          <strong>{analytics.total_new_members}</strong>
          <span>New members</span>
        </div>
        <div>
          <strong>{analytics.members_in_good_standing}</strong>
          <span>In Good Standing</span>
        </div>
        <div>
          <strong>{analytics.average_marks}</strong>
          <span>Average approved marks</span>
        </div>
        <div>
          <strong>{analytics.marks_this_week}</strong>
          <span>Approved entries this week</span>
        </div>
      </section>
      <div className="marks-active-grid">
        <section className="marks-card">
          <div className="marks-card-title">
            <h2>Current class</h2>
            <span>Approved totals</span>
          </div>
          {data.members.length ? (
            <ul className="class-marks-list">
              {data.members.map((member) => (
                <li key={member.history_url}>
                  <div>
                    <h3>{member.display_name}</h3>
                    <span>{member.is_negative ? 'Needs Improvement' : 'Good Standing'}</span>
                  </div>
                  <strong className={member.is_negative ? 'negative' : ''}>
                    {signed(member.total_marks)}
                  </strong>
                  <Link
                    to={historyPath(member.history_url)}
                    aria-label={`View ${member.display_name} history`}
                  >
                    History <span aria-hidden="true">→</span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="marks-empty">No current new members are listed.</p>
          )}
        </section>
      </div>
      <section className="marks-card marks-submissions">
        <div className="marks-card-title">
          <h2>Your submissions</h2>
          <span>Pending & recent denied</span>
        </div>
        <p className="marks-explanation">
          Pending requests and denied entries from the past 14 days.
        </p>
        {data.submissions.length ? (
          <ul className="marks-submission-list">
            {data.submissions.map((mark) => (
              <li key={mark.id}>
                <div>
                  <h3>{mark.title}</h3>
                  <p>
                    {mark.target_name} <span aria-hidden="true">·</span>{' '}
                    <time dateTime={mark.date}>{markDate(mark.date)}</time>
                  </p>
                </div>
                <strong className={mark.value < 0 ? 'negative' : ''}>{signed(mark.value)}</strong>
                <span className={`mark-status ${mark.status}`}>
                  {mark.status === 'requested' ? 'Pending' : 'Denied'}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="marks-empty">You have no pending or recent denied submissions.</p>
        )}
      </section>
    </>
  );
}
