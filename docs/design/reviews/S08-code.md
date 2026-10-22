# S08 correctness review

**Verdict: PASS.** No required correctness fixes found.

Scope: [S08 specification](../screen-specs.md#s08-service-hours), `/app/service`,
PHILANTHROPY read adapter/tests, React service UI/client and member navigation.
Evidence uses the real seeded local Django fixture at `http://127.0.0.1:8871`,
not live Railway.

## Independently verified

- **7 Python tests passed** with standalone settings:
  `manage.py test PHILANTHROPY.test.test_read_api --noinput`. They cover anonymous,
  missing-profile, ALUMNI and chair-only denial; own-event scoping despite a
  supplied other-user selector; inclusive July 1–June 30 boundaries; approved-only
  arithmetic with all own statuses listed; safe own-history URL/no-store/exact
  event fields; default/empty years; malformed/extreme year rejection; chair
  **and** ACTIVE capability; actual integer storage; and rejected submissions.
- **3 Playwright tests passed** against the built fixture (12.0s). They verify
  actual caller totals/statuses and review/request links, working academic-year
  selection/deep-link refresh/empty year, narrow layout with independently
  scrollable status table, actual ALUMNI API denial, read-failure/retry and the
  real legacy request form containing its hours input.
- Source inspection confirms reuse of existing date and own-event/approved-total
  helpers, ACTIVE gate before domain reads and PHIL_CHAIR conjunction for review
  navigation. The API does not expose another member's events or allow new writes.
- Year input uses four ASCII digits and a documented bounded range. Invalid
  query values fail with 400; the UI can return to the current year rather than
  inventing an empty success. Client validates shape/status/integer/date fields
  before showing results and uses bounded/abortable authenticated reads.
- UI totals explicitly count approved entries only; pending and denied status
  labels remain visible in the history table. Date-only values render with an
  explicit timezone so calendar days do not shift across browser timezones.
- No invented 20/40-hour requirement, notes field, fake progress ring, inert form
  or simulated submission is presented. Legacy request/history/approval actions
  use clear real navigation labels. Shared role checks and existing routes remain
  authoritative for mutations.
- All application files are under 400 physical lines and tests under 600;
  domain README and singular `test/` contracts are present. `git diff --check`
  passed. No schema or legacy transaction changes were introduced.

Preserved limitation: fractional legacy input is stored in an IntegerField and
truncates. The new adapter displays actual stored integers and tests that behavior;
this review does not approve a precision fix or imply fractional totals work.
Build/typecheck/Prettier and screenshot comparison are separate evidence.
