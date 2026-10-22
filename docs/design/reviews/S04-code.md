# S04 and A01 correctness review

**Verdict: PASS after one demo-instruction clarity fix.** Authentication and
read-contract checks pass; no security or data-boundary defect was found.

Scope: [A01](../screen-specs.md#a01-session-and-access-states) and
[S04](../screen-specs.md#s04-member-dashboard), `/app/login` and
`/app/dashboard`, AUTHENTICATE session/dashboard APIs, member shell/client,
and the explicitly approved bounded return-path addition to demo entry.
Evidence is local seeded Django at `http://127.0.0.1:8871`, not live Railway.

## Initial clarification and correction

The seeded dashboard announcement instructs visitors to “Switch personas above,”
but the React dashboard has no persona selector above it. Preserve authentic demo
entry and make this instruction true: for example, neutral shared seed wording
pointing to demo sign-in plus a clearly labeled demo-only link to `/app/login`.
Do not add a fake local role switch or expose demo entry outside demo mode.

Resolved: the shared seed now says “Use demo sign-in to choose a role and explore
fictional workflows.” The member rail exposes Change demo role only when the
server reports demo mode. It navigates to `/app/login`, whose native CSRF form
creates the real replacement session. Independently ran the added active → role
selection → alumni browser regression: **1 passed** (6.0s). Source review confirms
the copy and demo-only gate. No further required findings remain.

## Independently verified

- **17 Python tests passed**: AUTHENTICATE's eight read-contract tests, five
  shared public-link tests and four demo-return tests. Standalone settings and
  synthetic media were used; system checks were clean.
- The tests exercise anonymous session status, caller-only identity/roles,
  missing profiles, actual ACTIVE/ALUMNI/NEW_MEMBER capabilities, no-store,
  active announcement and safe ordered resource fields, empty feeds, session
  expiry, NEW_MEMBER precedence and rejected write methods.
- Demo tests verify actual CSRF rejection without a token, successful entry with
  a real token/session, exact allowlisted returns, unchanged absent/invalid-return
  defaults, NEW_MEMBER landing precedence and 404 outside demo mode.
- **8 Playwright tests passed** against the real built application (22.6s).
  Independent run covered anonymous denial, actual native demo login and seeded
  data, refresh/mobile overflow, real new-member landing, alumni navigation and
  actual logout, session error/retry, missing profile, dashboard 403 and empty/
  unavailable reads. Only exceptional states use network interception.
- Source inspection confirms normal SessionAuthentication, caller-only profile
  lookup, no confidential payload flash, bounded/abortable requests, explicit
  denied versus failed states and actual legacy sign-in/logout links. Server
  permissions are retained independently of navigation capability flags.
- The demo endpoint remains POST-only and constrained to seeded unprivileged
  accounts with unusable passwords. Return values are exact local allowlist
  matches; arbitrary `next` values preserve existing defaults.
- Shared safe URL validation moved to framework composition while HOME retains
  its compatibility import. No new business policies or fake statistics/forms
  are introduced. Summary counts derive from actual response arrays.
- All new application files remain under 400 physical lines; tests under 600.
  Domain READMEs, singular `test/` directories and endpoint contracts are present.

The temporary new-member bridge honestly opens legacy tools until S09. It is
not represented as an implemented React marks screen. Builder build/typecheck/
format checks and visual comparison remain separate evidence.
