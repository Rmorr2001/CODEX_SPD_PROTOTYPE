# Decisions case designs

Use [the shared fixture contract](../../../../docs/testing/fixture-contract.md) and
[local fixture vocabulary and scope rules](../regression-spec.md#local-fixture-vocabulary).
All fixtures are created independently inside each case; none carry from earlier cases.
Non-admin relative routes in blocks are under `/newmember/`.
[Source, defects and decisions](../regression-spec.md) supply the linked policy gates.

### NM-02-01a — test_pending_review_lists_only_requested_marks

Parent: `NM-02-01` | Operation: `NM-N02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:87–91; views_functions.py:160–172`

```text
GIVEN NM_BOARD R; requested M1=2026-10-15 and M2=2026-10-16 by A/B for T1/T2
  AND approved M3 and denied M4; all profiles have distinct names
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R GETs /newmember/approve/
THEN response is 200 using newmember_marks_approve.html
  AND pending_requests contains exactly M2,M1 in that order
  AND requester and target profile names and action/mark_id fields render
  AND the named fixture rows is unchanged
  AND authenticated identity remains R
  AND assert_unchanged(before)
```

### NM-02-01b — test_board_approves_another_request

Parent: `NM-02-01` | Operation: `NM-N02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:140–154`

```text
GIVEN NM_BOARD R named "Rae Reviewer", A's requested M for T1 and unrelated Z
  AND at_time(2026-10-17T12:00Z); R is neither requester nor target
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R POSTs /newmember/approve/ with {mark_id:M.id,action:"approve"}
THEN response is 200 review template with success and M absent from pending list
  AND M status is approved, approver "Rae Reviewer", approval time frozen
  AND requester/target/title/value/event date/submission/editor fields are unchanged
  AND only M's status/approval audit differ after refresh
  AND Z/users/profiles/roles/session identity remain unchanged
  AND assert_unchanged(before,
      except_fields={M:{mark_approval_status,mark_approver_name,mark_submission_approval_date}})
```

### NM-02-01c — test_board_denies_another_request

Parent: `NM-02-01` | Operation: `NM-N02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:140–154`

```text
GIVEN NM_BOARD R named "Rae Reviewer", A's requested M for T1 and unrelated Z
  AND at_time(2026-10-17T12:00Z); R is neither requester nor target
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R POSTs /newmember/approve/ with {mark_id:M.id,action:"deny"}
THEN response is 200 review template with success and M absent from pending list
  AND M status is denied, approver "Rae Reviewer", approval time frozen
  AND requester/target/title/value/event date/submission/editor fields are unchanged
  AND only M's status/approval audit differ after refresh
  AND Z/users/profiles/roles/session identity remain unchanged
  AND assert_unchanged(before,
      except_fields={M:{mark_approval_status,mark_approver_name,mark_submission_approval_date}})
```

### NM-02-02a — test_unknown_mark_id_reports_not_found

Parent: `NM-02-02` | Operation: `NM-N02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:143,155–156`

```text
GIVEN NM_BOARD R and unrelated requested Z; ID 999999 does not exist
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R POSTs approve/ with {mark_id:"999999",action:"approve"}
  AND call process_mark_approval directly with the same ID/action
THEN view returns 200 review page with "Mark not found" error
  AND helper returns (False,"Mark not found")
  AND pending Z remains visible and unchanged
  AND the named fixture rows and mark count are unchanged
  AND session identity remains R
  AND assert_unchanged(before)
```

### NM-02-02b — test_unknown_approval_action_never_claims_success

Parent: `NM-02-02` | Operation: `NM-N02` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D04 unknown action saved and reported as denied success
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:144–154`

```text
GIVEN NM_BOARD R and A's requested M for T1 with null approval audit
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST approve/ and direct helper each use action omitted,"","archive"
  AND mark_id=M.id, with a fresh fixture per variant
THEN unknown action is rejected without success-approved or success-denied message
  AND no status, approval time/name or editor/content field is saved differently
  AND the named fixture rows plus mark count is unchanged
  AND authenticated identity remains R
  AND response must not imply a denial that did not occur
  AND assert_unchanged(before)
```

### NM-02-02c — test_malformed_approval_ids_fail_without_exception_details

Parent: `NM-02-02` | Operation: `NM-N02` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D02 unsafe generic exception text
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:143,157–158`

```text
GIVEN NM_BOARD R and requested M for T1
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST approve/ and direct helper use mark_id omitted,"","abc" with action="approve"
THEN result is a controlled non-success without raw exception details
  AND view still presents requested M rather than claiming a successful review
  AND refreshed M status/content/approval/editor/submission fields are unchanged
  AND R/T1 users, profiles and roles remain unchanged
  AND mark count and authenticated session identity remain unchanged
  AND direct helper result cannot expose database conversion internals
  AND assert_unchanged(before)
```

### NM-02-03a — test_approval_helper_enforces_board_authorization

Parent: `NM-02-03` | Operation: `NM-N02` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D05 approval helper lacks board authorization
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:140–158`

```text
GIVEN R has only ACTIVE or no roles, parameterized separately
  AND requested M belongs to A for T1; unrelated Z exists
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN direct process_mark_approval(request_for_R,M.id,action) uses "approve" or "deny"
THEN non-board caller is denied before any status/approval write
  AND the named fixture rows is unchanged
  AND M remains requested with original approval/editor audit
  AND mark count is unchanged
  AND helper creates no files or session identity changes
  AND assert_unchanged(before)
```

### NM-02-03b — test_profileless_direct_reviewer_fails_safely

Parent: `NM-02-03` | Operation: `NM-N02` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D01 missing profile and D02 exception disclosure
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:146–158`

```text
GIVEN R=make_user(username="reviewer",with_profile=False), requested M and unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN process_mark_approval(request_for_R,M.id,"approve") is called directly
THEN result is non-success without relation exception details
  AND M's fresh status/approval/content/editor/submission fields remain unchanged
  AND Z, R and target/requester records remain unchanged
  AND mark count is unchanged
  AND no files or authenticated identity changes occur
  AND failure does not report successful approval
  AND assert_unchanged(before)
```

### NM-02-04a — test_repeat_and_reverse_review_need_transition_policy

Parent: `NM-02-04` | Operation: `NM-N02` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q04 repeated/reverse transitions and audit retention
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:143–153`

```text
GIVEN NM_BOARD R and another actor's M, at_time first noon then 13:00 UTC
  AND declare Z using the linked local fixture vocabulary
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN status/action pairs are (approved,approve),(denied,deny),
  (approved,deny),(denied,approve), separately POST approve/ and direct helper
THEN Q04 chooses rejection, idempotence or override for each transition
  AND status/name/time response and persisted audit must agree with that choice
  AND no-op/rejected variants retain original audit; overrides record chosen review audit
  AND M requester/target/value/title/event/submission/editor and unrelated Z are unchanged
  AND roles/session identity remain unchanged
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-02-04b — test_self_review_needs_actor_policy

Parent: `NM-02-04` | Operation: `NM-N02` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q04 self-review policy
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:140–153`

```text
GIVEN NM_BOARD R requested M for T1; separate variant makes R the target
  AND declare Z using the linked local fixture vocabulary
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R POSTs approve/ with M.id and action "approve" or "deny"
THEN Q04 chooses self-review denial or permitted review
  AND denied outcome preserves every M field and returns no success
  AND allowed outcome changes only status/approval name/time per actor R
  AND requester/target/content/submission/editor stay unchanged
  AND unrelated Z/users/roles/session identity remain unchanged
  AND target-self and requester-self are separate concrete variants
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-02-05a — test_simultaneous_review_needs_conflict_policy

Parent: `NM-02-05` | Operation: `NM-N02` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q04 winner/conflict contract; PostgreSQL facility also missing
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:143–153`

```text
GIVEN PostgreSQL independent connections, pending M, board R1/R2 and unrelated Z
  AND bounded barrier synchronizes both readers before writing
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R1 approves and R2 denies through separate requests with 5-second bounded waits
THEN Q04 chooses conflict rejection, first-writer or authorized override semantics
  AND final status/approver/time and each response agree with that choice
  AND no approval audit from one actor is paired with the other actor's decision
  AND M content/requester/target/submission/editor and Z/users/roles stay unchanged
  AND SQLite execution is not evidence of this concurrency guarantee
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-02-05b — test_approval_save_failure_keeps_original_row

Parent: `NM-02-05` | Operation: `NM-N02` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:153–158`

```text
GIVEN board R, pending M for T1 and unrelated Z
  AND deliberately inject RuntimeError("synthetic write failure") at M.save before SQL
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN direct process_mark_approval(request_for_R,M.id,"approve") runs
THEN helper returns False and an error result, never success
  AND M remains requested with original approval audit after fresh read
  AND M requester/target/content/submission/editor fields remain unchanged
  AND the named fixture rows and mark count remain unchanged
  AND no session identity or file changes occur
  AND assert_unchanged(before)
```
