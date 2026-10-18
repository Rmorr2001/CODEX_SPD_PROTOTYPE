# PARLEYPRO Wave 2 implementation findings

Implementation baseline: `4b103f6`; frozen designs are in
[wave-2-inventory.json](../../../docs/testing/wave-2-inventory.json).
All 58 frozen READY IDs have one named method in [case-map.json](case-map.json).
The 56 non-READY designs retain their frozen statuses and have no passing-test credit.

## Approved transport/design clarifications

### PP-31b: view-only admin Result column is index 6

The original design requests `?o=7` for an actor with only `view_vote_poll`.
`PARLEYPRO/admin.py:10–18` defines seven list-display fields. Django prepends
`action_checkbox` only when available actions exist. A view-only actor has no delete
permission, so no action checkbox exists and Result is column index 6.

Observed first run: `?o=7` left PK order `[4, 3, 2]` instead of expected Yes-count order
`[4, 2, 3]`. The coordinator explicitly approved changing the selector to `?o=6` and
asserting the real seven-field layout. The test continues to prove ascending Yes-count
sorting with a losing 3/4 poll ordered after a passing 2/0 poll. No delete permission
was added, and no behavior/status/case mapping was downgraded.

### PP-27c: Chicago date display zero-pads the day

The design prose says `Nov 1, 2026`; the actual template at
`SPDWEBAPP/PARLEYPRO/templates/past_polls.html:46` uses `M d, Y g:i A`.
Its `d` directive renders `Nov 01, 2026`. The coordinator approved asserting the
literal source format. The test observes two `Ended: Nov 01, 2026 1:30 AM` displays
for 06:30Z/07:30Z and independently verifies descending UTC end ordering. DST and
stored-timestamp assertions remain intact; no business rule was changed.

## Shared setup issue resolved by coordinator

The initial business-mode run found the demo context processor unconditionally returned
`demo_enabled=True`, causing HOME/main.html to include a banner reversing `demo_enter`,
which is absent from core-only business routes. The coordinator corrected the standalone
business harness context setup. Domain tests do not override templates, mock rendering,
change app code, or enable public-demo routes to hide that issue.

The remaining test-development failures were corrected in test setup: anonymous GET
payloads must not accidentally add query parameters to `next`, and authorization
snapshots are taken after `login_actor` updates the synthetic user's `last_login`.
These changes preserve all post-action unchanged-user assertions.

## Verification

Final package scope: 58 discovered methods, 58 tests passed, zero skips/expected failures.
App-wide discovery independently ran the same 58 tests and passed; zero skips or
expected failures. System checks emitted no issues. Actual commands and durations are in
[README](README.md). No app fixes, schema/config/dependency changes, real data, network,
or deployment actions were performed. The only removed app-root file is obsolete
empty `PARLEYPRO/tests.py`; singular test-package discovery replaces it.

Unauthorized ACTIVE close (PP-17a), transaction/race safety, ambiguous dispatch/no-open/
eligibility policies, admin retention/lifecycle and browser facilities remain blocked.
Global mutation probes and combined-suite validation belong to the coordinator.
