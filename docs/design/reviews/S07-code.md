# S07 correctness review

**Verdict: PASS.** No required correctness fixes found.

Scope: [S07 specification](../screen-specs.md#s07-chapter-decisions),
`/app/polls`, PARLEYPRO read adapter/tests, React decision cards/client/states,
member navigation and the shared AUTHENTICATE role boundary. Checks ran against
the local seeded fixture at `http://127.0.0.1:8871`; no live Railway claim.

## Independently verified

- **14 Python tests passed**: six PARLEYPRO read API tests and eight identity
  read-contract tests affected by the shared profile-helper extraction.
  Command: `manage.py test PARLEYPRO.test.test_read_api AUTHENTICATE.test.test_read_api --noinput`
  with standalone testing settings.
- Tests cover anonymous/missing-profile/ALUMNI/EXEC-only denial, ACTIVE reads,
  newest open motion, real global Aye/Nay store totals, saved closed counts and
  descending end order, empty/zero state, exact aggregate-only field whitelist,
  no-store, EXEC **and** ACTIVE management capability and rejected ballot writes.
- **3 Playwright tests passed** against actual seeded data (17.4s): actual
  current/closed result rendering and refresh, real legacy voting/creation links,
  role-sensitive creation visibility and actual alumni denial, empty/no-motion/
  zero-safe bars, read-failure/retry, refresh/deep link and mobile overflow.
- Source review confirms `require_member_roles` requires an authenticated
  profile and all specified roles. The API requires ACTIVE before checking EXEC
  management capability; it never exposes voter identities or accepts ballots.
  The extracted profile helper retains its existing caller-only behavior.
- Current counts deliberately reuse `count_all_current_votes` over the global
  current vote store; saved historical motions use their stored totals. UI
  explains this distinction and labels results as a refreshable snapshot.
  Generated multiple-choice options/deadlines were correctly replaced by the
  existing Aye/Nay motion semantics, not implemented as invented product rules.
- Controls are real refresh and navigation actions. No inert ballot choices,
  fake success messages or simulated React transactions appear. Native links
  hand off to the original vote/create/past-results flows with explicit labels.
- Client validates dates, count integers, current/closed distinction and management
  flag. Read states use bounded/abortable same-origin authenticated requests,
  fail visibly and do not render protected cards after denied responses.
- Files are under the 400-line application and 600-line test limits; domain
  docs and singular `test/` boundaries are present. `git diff --check` passed.

Original ballot/closure behavior, including unresolved legacy policies, was not
rewritten. Build/typecheck/Prettier and image comparison are separate evidence;
this pass delivers a real React read experience with legacy mutation links.
