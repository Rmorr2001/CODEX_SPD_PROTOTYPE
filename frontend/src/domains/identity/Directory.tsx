import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useMemberRead } from '../../api/read';
import { fetchDirectory, type DirectoryMember } from './directoryContent';
import { MemberAvatar } from './MemberAvatar';
import './directory.css';

function MemberDetails({ member }: { member: DirectoryMember }) {
  return (
    <aside
      className="directory-detail"
      id="directory-member-detail"
      tabIndex={-1}
      aria-labelledby="member-detail-title"
    >
      <MemberAvatar name={member.display_name} image={member.image} large />
      <h2 id="member-detail-title">{member.display_name}</h2>
      <p className="member-major">{member.majors.join(' · ') || 'Major not listed'}</p>
      <div className="role-badges">
        {member.roles.map((role) => (
          <span key={role.code}>{role.label}</span>
        ))}
      </div>
      <dl>
        <dt>Member class</dt>
        <dd>{member.pclass || 'Not listed'}</dd>
        <dt>Chapter</dt>
        <dd>Beta-Omicron · Mizzou</dd>
      </dl>
      <p className="directory-privacy">A chapter directory, built around the people who make it.</p>
    </aside>
  );
}

export function Directory() {
  const [group, setGroup] = useState<'current' | 'alumni'>('current');
  const [query, setQuery] = useState('');
  const [role, setRole] = useState('');
  const [selected, setSelected] = useState<number | null>(null);
  const [focusRequest, setFocusRequest] = useState(0);
  useEffect(() => {
    // Narrow layouts place details below the list; a deliberate selection must reveal its result.
    if (focusRequest && window.matchMedia('(max-width: 1100px)').matches) {
      const details = document.getElementById('directory-member-detail');
      details?.focus({ preventScroll: true });
      details?.scrollIntoView({ block: 'start' });
    }
  }, [focusRequest]);
  const load = useCallback((signal: AbortSignal) => fetchDirectory(group, signal), [group]);
  const { state, retry } = useMemberRead(load);
  const changeGroup = (next: 'current' | 'alumni') => {
    setGroup(next);
    setQuery('');
    setRole('');
    setSelected(null);
  };
  if (state.kind === 'denied')
    return (
      <section className="member-notice">
        <h1>Member access required</h1>
        <p role="alert">Sign in again to open the chapter directory.</p>
        <Link to="/login">Member sign in</Link>
      </section>
    );
  if (state.kind === 'failed')
    return (
      <section className="member-notice">
        <h1>The directory is unavailable</h1>
        <p role="alert">We couldn’t load the chapter directory. Please try again.</p>
        <button onClick={retry}>Try again</button>
      </section>
    );
  const ready = state.kind === 'ready' && state.data.group === group;
  const members = ready ? state.data.members : [];
  const visible = members.filter(
    (member) =>
      `${member.display_name} ${member.majors.join(' ')} ${member.roles.map((item) => item.label).join(' ')}`
        .toLowerCase()
        .includes(query.trim().toLowerCase()) &&
      (!role || member.roles.some((item) => item.code === role)),
  );
  const roles = [
    ...new Map(
      members.flatMap((member) => member.roles.map((item) => [item.code, item.label] as const)),
    ).entries(),
  ];
  const focused = visible.find((member) => member.id === selected) ?? visible[0];
  return (
    <>
      <div className="directory-heading">
        <p className="eyebrow">PEOPLE WHO BUILD TOGETHER</p>
        <h1>The chapter.</h1>
        <p>Dedicated people. Shared purpose. Lasting connections.</p>
      </div>
      <div className="directory-tools">
        <div className="directory-tabs" role="group" aria-label="Roster group">
          <button
            className={group === 'current' ? 'selected' : ''}
            aria-pressed={group === 'current'}
            onClick={() => changeGroup('current')}
          >
            Current members
          </button>
          <button
            className={group === 'alumni' ? 'selected' : ''}
            aria-pressed={group === 'alumni'}
            onClick={() => changeGroup('alumni')}
          >
            Alumni
          </button>
        </div>
        <div className="directory-filters">
          <label>
            <span>Search the chapter</span>
            <input
              type="search"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setSelected(null);
              }}
              placeholder="Search name, major, or role…"
            />
          </label>
          <label>
            <span>Filter by role</span>
            <select
              value={role}
              onChange={(event) => {
                setRole(event.target.value);
                setSelected(null);
              }}
            >
              <option value="">All roles</option>
              {roles.map(([code, label]) => (
                <option value={code} key={code}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>
      {!ready ? (
        <p role="status">Loading the chapter directory…</p>
      ) : (
        <>
          <p className="directory-count" role="status">
            {visible.length} of {members.length} {group === 'alumni' ? 'alumni' : 'current members'}
          </p>
          {visible.length ? (
            <div className="directory-layout">
              <div className="directory-grid">
                {visible.map((member) => (
                  <button
                    type="button"
                    className={`directory-member${focused?.id === member.id ? ' selected' : ''}`}
                    key={member.id}
                    aria-pressed={focused?.id === member.id}
                    aria-controls="directory-member-detail"
                    onClick={() => {
                      setSelected(member.id);
                      setFocusRequest((value) => value + 1);
                    }}
                  >
                    <MemberAvatar name={member.display_name} image={member.image} />
                    <span className="directory-card-copy">
                      <strong>{member.display_name}</strong>
                      <span className="card-major">
                        {member.majors.join(' · ') || 'Major not listed'}
                      </span>
                      <span className="card-role">{member.roles[0]?.label || 'Member'}</span>
                    </span>
                  </button>
                ))}
              </div>
              {focused && <MemberDetails member={focused} />}
            </div>
          ) : (
            <section className="directory-empty">
              <h2>{members.length ? 'No matching members' : 'No members to show yet'}</h2>
              <p>
                {members.length
                  ? 'Try another name, major, or role.'
                  : 'This roster has no published member profiles.'}
              </p>
              {(query || role) && (
                <button
                  onClick={() => {
                    setQuery('');
                    setRole('');
                  }}
                >
                  Clear filters
                </button>
              )}
            </section>
          )}
        </>
      )}
    </>
  );
}
