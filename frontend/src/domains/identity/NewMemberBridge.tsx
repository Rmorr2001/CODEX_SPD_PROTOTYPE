import { chapterSite } from '../../app/links';
import { useMember } from './MemberLayout';

/** Temporary real-workflow handoff until the new-member React read screen lands. */
export function NewMemberBridge() {
  const member = useMember();
  if (!member.capabilities.new_members)
    return (
      <section className="member-notice">
        <h1>Member access required</h1>
        <p role="alert">New-member tools are unavailable for your current role.</p>
      </section>
    );
  return (
    <section className="newmember-handoff">
      <p className="eyebrow">YOUR NEXT CHAPTER</p>
      <h1>Welcome, {member.display_name.split(' ')[0]}.</h1>
      <p>Continue with your new-member tools on the chapter site.</p>
      <a className="button primary" href={`${chapterSite}newmember/`}>
        Open your new-member dashboard
      </a>
      <a href={`${chapterSite}newmember/marks/`}>View your marks</a>
    </section>
  );
}
