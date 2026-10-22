# S09 correctness review

**Verdict: PASS, with the transient browser timeout recorded below.** No required
source-correctness fix found.

Scope: [S09 specification](../screen-specs.md#s09-new-member-marks),
`/app/new-members`, NEWMEMBER API/tests, role-specific React marks UI/client,
session capabilities, member navigation and updated S04 landing coverage.
Evidence is from local seeded Django at `http://127.0.0.1:8871`, not live Railway.

## Independently verified

- **8 Python tests passed** with standalone settings:
  `manage.py test NEWMEMBER.test.test_read_api --noinput`. They cover anonymous,
  ALUMNI/unclassified/missing-profile denial; caller-only approved history and
  target-parameter injection; signed arithmetic, latest/history order, zero/
  positive/negative standing and class average; NEW_MEMBER precedence for dual
  roles; ACTIVE ordered class totals/analytics and own submission scope; existing
  requested/recent-denied filtering; board-only review handoff; NM_BOARD review
  capability versus EXEC/NME; empty data; and rejected writes.
- First independent browser run: **4 passed, 1 timed out** (47.4s). The timeout
  occurred waiting for the demo-role selector during initial `/app/login`, before
  the ordinary-active marks assertions. Other checks covered real personal
  data/history/standing and legacy history navigation, actual ACTIVE class data/
  submissions and request form, read-failure/retry/session loss, and S04 native
  new-member landing.
- Isolated rerun of that single case with a separate artifact directory:
  **1 passed** (17.9s). It verified ordinary ACTIVE has no review action and
  ALUMNI API/UI denial without marks. Concurrent root verification created load
  during the first run, but the timeout's cause was not proven; no silent retries
  or source changes were used to erase that observation. Initial default browser
  artifacts were overwritten by another runner, so the rerun used
  `/workspace/work/s09-review-browser`.
- Source review confirms real helper reuse for approved signed totals, standing,
  latest/history, class progress/analytics and own requested/denied submissions.
  Other users' reasons are absent from serialized class rows; own approved
  reasons and own submissions are exposed only in their intended caller scope.
- NEW_MEMBER personal mode takes precedence, ACTIVE gets class/submission mode,
  NM_BOARD-only gets a minimal review handoff, and unrelated roles are denied.
  Review requires NM_BOARD, not a misleading EXEC/NME substitute. Server gates
  and no-store remain independent of navigation capability flags.
- Client validates role-specific shape and mode consistency, safe legacy links,
  finite/signed counts, dates and statuses. UI renders meaningful loading, empty,
  failure, denial and expiry states through bounded/abortable authenticated reads.
- No invented checklist, initiation eligibility, milestone percentage, fake
  transaction or inert form. Legacy request/review/history links are explicit,
  preserve Django's domain origin in development and open genuine workflows.
- New source files are below 400 physical lines; tests below 600. Domain README
  and singular `test/` contracts exist; `git diff --check` passed. The superseded
  temporary bridge was removed, and S04's landing test now checks actual marks.

Preserved limitation: own denied submissions use the existing **14-day event-date**
cutoff, despite the old helper's inaccurate “month” comment. No mutation, model,
schema or broader marks policy was changed. Final combined verification and
visual acceptance remain separate evidence and must retain any repeated timeout.
