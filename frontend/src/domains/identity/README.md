# Identity and member workspace

Owns `/app/login`, session/access states, the member shell and `/app/dashboard`.
The server owns authentication and permissions. `session.ts` reads the actual
cookie session with no browser-stored identity; `MemberLayout` renders protected
children only after a genuine authenticated profile. `Dashboard` reads active
announcements and safe ordered chapter links from AUTHENTICATE's read contracts.
Counts derive from those arrays; no events, tasks, hour requirements or charts
are invented. New members land separately at `/app/new-members`, temporarily
linked to the existing new-member tools until that screen is migrated.

Sign in and logout remain the original Django flows. On the disposable demo,
login offers a native CSRF-protected form to the existing `/demo/enter/` endpoint,
with a fixed allowlisted return. It creates a real server session; no password is
shared. The demo selector only appears when the session API reports demo mode.
Vite development links demo entry to the Django-served login page to preserve
same-origin CSRF validation; cross-origin demo submission is not supported.

`test/` owns browser contracts and `helpers.ts` exposes actual demo-entry setup
for subsequent member-screen tests. The shared runner imports these tests.
Build first, then use the frontend README's Playwright command. Tests cover real
entry/data/logout and anonymous, missing-profile, permission, empty and failed
read states. Synthetic HTTP interception is limited to those exceptional states.
No new environment/configuration keys or application credentials are needed.
