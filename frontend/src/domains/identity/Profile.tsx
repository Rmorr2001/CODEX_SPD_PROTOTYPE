import { Link } from 'react-router-dom';
import { chapterSite } from '../../app/links';
import { useMemberRead } from '../../api/read';
import { MemberAvatar } from './MemberAvatar';
import { fetchOwnProfile } from './profileContent';
import './profile.css';

export function Profile() {
  const { state, retry } = useMemberRead(fetchOwnProfile);
  if (state.kind === 'loading') return <p role="status">Loading your profile…</p>;
  if (state.kind === 'denied')
    return (
      <section className="member-notice">
        <h1>Member access required</h1>
        <p role="alert">Your profile is unavailable. Sign in again to continue.</p>
        <Link to="/login">Member sign in</Link>
      </section>
    );
  if (state.kind === 'failed')
    return (
      <section className="member-notice">
        <h1>Your profile is unavailable</h1>
        <p role="alert">We couldn’t load your profile. Please try again.</p>
        <button onClick={retry}>Try again</button>
      </section>
    );
  const profile = state.data;
  return (
    <>
      <div className="profile-heading">
        <div>
          <p className="eyebrow">YOUR PLACE IN THE CHAPTER</p>
          <h1>Your profile.</h1>
          <p>Your details, your interests, your chapter identity.</p>
        </div>
        <a className="button primary" href={`${chapterSite}auth/profile/`}>
          Edit in chapter site
        </a>
      </div>
      <div className="profile-columns">
        <section className="member-card personal-details" aria-labelledby="personal-title">
          <h2 id="personal-title">Personal information</h2>
          <p className="card-intro">The information on your chapter profile.</p>
          <dl className="profile-fields">
            <div>
              <dt>First name</dt>
              <dd>{profile.first_name || 'Not listed'}</dd>
            </div>
            <div>
              <dt>Last name</dt>
              <dd>{profile.last_name || 'Not listed'}</dd>
            </div>
            <div>
              <dt>Username</dt>
              <dd>{profile.username}</dd>
            </div>
            <div>
              <dt>Email</dt>
              <dd>{profile.email || 'Not listed'}</dd>
            </div>
            <div>
              <dt>Hometown</dt>
              <dd>{profile.hometown || 'Not listed'}</dd>
            </div>
            <div>
              <dt>Member class</dt>
              <dd>{profile.pclass || 'Not listed'}</dd>
            </div>
          </dl>
          <div className="profile-majors">
            <h3>Areas of study</h3>
            {profile.majors.length ? (
              <div className="major-badges">
                {profile.majors.map((major, index) => (
                  <span key={`${major}-${index}`}>{major}</span>
                ))}
              </div>
            ) : (
              <p>No majors have been listed yet.</p>
            )}
          </div>
          <div className="profile-edit-note">
            <p>Want to update something?</p>
            <a href={`${chapterSite}auth/profile/`}>
              Edit your details, photo, and majors on the chapter site
            </a>
          </div>
        </section>
        <div className="profile-side">
          <section className="member-card profile-identity" aria-labelledby="profile-name">
            <MemberAvatar name={profile.display_name} image={profile.image} large />
            <h2 id="profile-name">{profile.display_name}</h2>
            <p>Beta-Omicron · Mizzou</p>
            <div className="profile-role-badges">
              {profile.roles.map((role) => (
                <span key={role.code}>{role.label}</span>
              ))}
            </div>
          </section>
          <section className="member-card profile-account" aria-labelledby="account-title">
            <h2 id="account-title">Your account</h2>
            <p>Manage your account details and password through your chapter profile.</p>
            <a href={`${chapterSite}auth/profile/`}>Open account settings</a>
          </section>
          <aside className="profile-privacy">
            <span className="eyebrow">YOUR ACCOUNT</span>
            <p>
              Keep your details current so your chapter can stay connected. Open your chapter
              profile whenever something changes.
            </p>
          </aside>
        </div>
      </div>
    </>
  );
}
