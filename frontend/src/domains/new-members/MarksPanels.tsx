import { type MarksContent, type Mark, markDate, signed } from './content';
import { chapterSite } from '../../app/links';

function originalLink(path: string) {
  return path.startsWith('/') ? `${chapterSite}${path.slice(1)}` : path;
}

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
          <p id="personal-marks-title">YOUR APPROVED MARKS</p>
          <strong>{signed(personal.total_marks)}</strong>
          <span>Approved total</span>
        </div>
        <div className="marks-standing">
          <p className="eyebrow">CURRENT STANDING</p>
          <h2>{personal.standing}</h2>
          <p>
            Standing reflects your approved mark total. A total of zero or higher is Good Standing.
          </p>
          <a href={originalLink(personal.history_url)}>View your history in chapter site</a>
        </div>
        <div className="marks-class-average">
          <strong>{personal.class_average}</strong>
          <span>Current class average</span>
          <p>Approved marks per new member</p>
        </div>
      </section>
      <div className="marks-personal-grid">
        <section className="marks-card">
          <div className="marks-card-title">
            <h2>Your approved history</h2>
            <span>{personal.history.length} entries</span>
          </div>
          <MarkList marks={personal.history} empty="You don’t have any approved marks yet." />
        </section>
        <aside className="marks-latest marks-card">
          <p className="eyebrow">MOST RECENT APPROVED MARK</p>
          {personal.latest_mark ? (
            <>
              <strong className="latest-mark-value">{signed(personal.latest_mark.value)}</strong>
              <h2>{personal.latest_mark.title}</h2>
              <time dateTime={personal.latest_mark.date}>
                {markDate(personal.latest_mark.date)}
              </time>
            </>
          ) : (
            <>
              <h2>A fresh start.</h2>
              <p>Your latest approved mark will appear here.</p>
            </>
          )}
          <p>
            Only approved entries affect this total. Contact your new-member board with questions
            about a record.
          </p>
        </aside>
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
                  <a
                    href={originalLink(member.history_url)}
                    aria-label={`View ${member.display_name} history in chapter site`}
                  >
                    History <span aria-hidden="true">→</span>
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <p className="marks-empty">No current new members are listed.</p>
          )}
        </section>
        <aside className="marks-note">
          <p className="eyebrow">A CLEARER VIEW</p>
          <h2>Support the next chapter.</h2>
          <p>
            Class totals include approved marks only, ordered from lowest to highest. Individual
            reasons stay in the chapter history workflow.
          </p>
          <a href={`${chapterSite}newmember/marks/`}>Open original marks dashboard</a>
        </aside>
      </div>
      <section className="marks-card marks-submissions">
        <div className="marks-card-title">
          <h2>Your submissions</h2>
          <span>Pending & recent denied</span>
        </div>
        <p className="marks-explanation">
          Pending requests and your denied submissions from the past 14 days are shown by event
          date. Approved entries are included in class totals.
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
