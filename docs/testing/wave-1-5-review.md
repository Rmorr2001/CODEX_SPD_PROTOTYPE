# Wave 1.5 implementation handoff

Wave 1.5 replaces dense scenario groups with independently named case designs.
Application source remains at `7e25ac2`; the original 217-group specification is
preserved in Git commit `c8bbc4e`. No executable tests or runtime fixes are added.

All 217 original groups are traceable to 677 named designs. Their primary
statuses are 393 READY, 41 NEEDS_FIX, 237 POLICY_BLOCKED and 6 INFRA_BLOCKED.
See [the domain readiness table](case-readiness.md) and linked case indexes.

## What changed

- Each domain's `test/README.md` is an entry point; `regression-spec.md` holds
  the inventory, decisions and links to workflow files under `test/cases/`.
- Every detailed case has a proposed `test_...` name, original parent ID,
  operation, priority, primary status, blockers, source reference and short
  GIVEN / WHEN / THEN pseudocode.
- Equivalent inputs can be explicit parameter sets. Different contracts,
  actions, failure boundaries or readiness states are separate cases.
- The [shared fixture contract](fixture-contract.md) replaces conflicting
  helper proposals. It defines the design interface, not installed helpers.
- Original-to-new mappings make it possible to audit the rewrite for omissions.
  A higher design count does not establish additional implemented coverage.

For example, original `PP-07` bundled initial votes, changing choices and repeat
submissions. Its replacement separates Aye creation, Nay creation, changing the
existing row and repeated-choice stability. Each names response and database
assertions instead of relying on a paragraph of implicit conditions.

## Implementation gates

`READY` means the expected result is specified without unresolved policy or a
known defect, subject to the common Wave 2 harness and source verification.
It does not mean the proposed test ran or that all business policy is approved.

`NEEDS_FIX` cases expose a specific defect. `POLICY_BLOCKED` cases require a named
decision before the final result can be asserted. `INFRA_BLOCKED` cases need a
specific facility beyond the ordinary harness. Additional blockers remain listed
even when a case has a different primary status.

Wave 2 first establishes fixture behavior, safe settings and test discovery,
then implements reviewed READY cases. Defect regressions and authorized fixes
remain separately reviewable. Policy-blocked cases do not become passing tests
by encoding an arbitrary current behavior or by using skip/expected-failure.

## Verification boundary

This documentation change does not rerun application tests or claim new coverage.
The unchanged application baseline has nine passing demo tests, as recorded in
[the Wave 1 review](wave-1-review.md). Documentation verification checks case
schema, unique IDs/names, original-parent traceability, status counts, file links,
heading anchors and documentation-only diff scope. These checks supplement,
not replace, source review or execution of future assertions.

Coordinator samples also caught unspecified actors/targets and unclear snapshot
timing; domain definitions now make fresh fixture creation and pre-action state
capture explicit. CSRF client creation is separate from authentication and token
acquisition. Those clarifications do not implement the proposed helpers.
