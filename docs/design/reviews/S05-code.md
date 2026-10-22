# S05 correctness review

**Verdict: PASS.** No required correctness fixes found.

Scope: [S05 specification](../screen-specs.md#s05-member-directory),
`/app/members`, AUTHENTICATE directory adapter/tests, directory UI/client/avatar,
shared authenticated-read helper, and member navigation. Independent checks
targeted the real seeded fixture at `http://127.0.0.1:8871`, not Railway.

## Independently verified

- Follow-up after visual review: deliberate member-card selection now reveals
  and focuses the chosen detail in narrow layouts, with `aria-controls` linking
  the control to its result. Automatic initial selection and filtering do not
  trigger that scroll. Independently ran the new mobile selection regression:
  **1 passed** (6.1s), asserting correct member, focused detail and heading overlap
  with the viewport rather than an impossible exact-top scroll near page end.

- **5 Python tests passed** using standalone settings:
  `manage.py test AUTHENTICATE.test.test_directory_api --noinput`.
  Anonymous/missing-profile requests are denied; current roster excludes anyone
  with ALUMNI, alumni roster includes dual-role members, results are distinct and
  ordered by last name, invalid group is rejected, empty groups are explicit,
  and POST is unavailable.
- Payload tests assert the exact member whitelist: profile ID, display name,
  role labels/codes, majors, class and safe image. Username, email, hometown,
  password and full User records are not exposed. Successful reads are no-store.
- **3 Playwright tests passed** against the actual built application (14.1s):
  `FRONTEND_TEST_URL=http://127.0.0.1:8871 PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium npm run test:e2e -- --grep directory --reporter=line`.
  These verify real current/alumni data, name search, selected-member detail,
  role filtering, clear/no-result behavior, tab switching, refresh, narrow mobile
  overflow, empty/error/retry and denied reads without member cards.
- Source review confirms consistent server-enforced authentication/profile
  boundaries, explicit group validation, safe URLs and React text rendering.
  The shared helper distinguishes 401/403 from failed reads, clears state on a
  new load, aborts stale requests and bounds attempts to 15 seconds. Directory
  additionally checks response group before showing a newly selected group.
- No decorative pagination, fabricated contacts, editable controls pretending
  to save, or business/schema changes. Native labeled search/select controls,
  pressed group/card buttons, visible feedback and image/major/class fallbacks
  support real use without relying on generated faces or placeholder claims.
- All application source files are below 400 physical lines, tests below 600;
  domain docs and singular `test/` ownership are present. `git diff --check`
  passed. Dashboard changes only share the common access-error class.

Visual fidelity and screenshot approval are recorded separately by the comparison
agent. Builder build/typecheck/Prettier results are not counted as independently
rerun checks here. Current implementation is a read-only directory, not a new
member-editing or contact-permission policy.
