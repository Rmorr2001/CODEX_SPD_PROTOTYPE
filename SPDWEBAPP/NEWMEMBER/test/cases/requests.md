# Requests case designs

Use [the shared fixture contract](../../../../docs/testing/fixture-contract.md) and
[local fixture vocabulary and scope rules](../regression-spec.md#local-fixture-vocabulary).
All fixtures are created independently inside each case; none carry from earlier cases.
Non-admin relative routes in blocks are under `/newmember/`.
[Source, defects and decisions](../regression-spec.md) supply the linked policy gates.

### NM-01-01a — test_request_form_lists_new_member_targets

Parent: `NM-01-01` | Operation: `NM-N01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:66–68`

```text
GIVEN ACTIVE A; NEW_MEMBER T1/T2 with last names Able/Zed; ALUMNI B
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs /newmember/request/
THEN response is 200 using newmember_marks_request.html
  AND target_users is a required multiple select with IDs T1,T2 in that order
  AND B is absent; mark_value, mark_reason, mark_date and CSRF fields exist
  AND action submit is present
  AND named rows/roles, mark count and authenticated identity remain unchanged
  AND assert_unchanged(before)
```

### NM-01-01b — test_signed_multi_target_submission_creates_requested_marks

Parent: `NM-01-01` | Operation: `NM-N01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:52–65; views_functions.py:116–135`

```text
GIVEN ACTIVE A, NEW_MEMBER T1/T2, unrelated mark Z and at_time(2026-10-17T12:00Z)
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A POSTs /newmember/request/ with target_users=[T1.id,T2.id],
  mark_value parameterized as "-3","0","4", mark_reason="Workshop",
  mark_date="2026-10-16"; each value uses a fresh fixture
THEN response redirects to marks dashboard with success for 2 new members
  AND exactly two new rows have requester A, respective targets, supplied value/date/reason
  AND both are requested with submission time frozen and null approval/editor audit
  AND Z, users/profiles/roles and session identity remain unchanged
  AND assert_unchanged(before)
```

### NM-01-02a — test_board_submission_autoapproves_and_ignores_forged_audit

Parent: `NM-01-02` | Operation: `NM-N01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:119–135`

```text
GIVEN ACTIVE+NM_BOARD A with profile name "Alex Able", NEW_MEMBER T1/T2, no-role B and unrelated Z
  AND at_time(2026-10-17T12:00Z)
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A POSTs request/ with target_users=[T1.id,T2.id], mark_value="2",
  mark_reason="Workshop",mark_date="2026-10-16",requesting_user=B.id,
  mark_approval_status="denied",mark_approver_name="Forged",last_edited_by=B.id
THEN response redirects to marks dashboard with success
  AND two rows are approved, requester A, approver "Alex Able", approval/submission time frozen
  AND supplied targets/content persist and editor fields are null
  AND Z, A/B/T1/T2 profiles/roles and session identity remain unchanged
  AND assert_unchanged(before)
```

### NM-01-03a — test_malformed_request_fields_never_crash_or_insert

Parent: `NM-01-03` | Operation: `NM-N01` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D02 raw parsing and unsafe exception text; safe error transport not prescribed
Source: `SPDWEBAPP/NEWMEMBER/views.py:53–58; views_functions.py:136–137`

```text
GIVEN ACTIVE A, NEW_MEMBER T1/T2 and unrelated Z; base payload is Workshop/2/2026-10-16/[T1,T2]
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST request/ overrides one field per fresh fixture:
  mark_value omitted,"","abc","1.5"; mark_date omitted,"","bad","2026-02-30";
  mark_reason omitted; direct helper separately receives value="abc" or date="bad"
THEN malformed inputs produce controlled non-success without raw exception details
  AND no target row is inserted, including the first target
  AND the named fixture rows plus mark count remain unchanged
  AND requester session identity remains A
  AND assert_unchanged(before)
```

### NM-01-03b — test_request_content_boundaries_require_policy

Parent: `NM-01-03` | Operation: `NM-N01` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q02 content/value/date limits; backend range differences
Source: `SPDWEBAPP/NEWMEMBER/models.py:23–31; views.py:53–58`

```text
GIVEN ACTIVE A, NEW_MEMBER T1 and unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN each request overrides Workshop/2/2026-10-16/T1 with reason "", 100 or 101 x's,
  value "2147483647","2147483648","-2147483649", or date "2026-10-18"
THEN Q02 must choose content limits and future-date allowance
  AND accepted variants persist exact content; rejected variants insert nothing
  AND rejection cannot disclose database exception text
  AND Z, actor/target profiles/roles and authenticated identity remain unchanged
  AND each backend-boundary outcome is checked with fresh rows
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-01-04a — test_empty_and_duplicate_target_batches_require_policy

Parent: `NM-01-04` | Operation: `NM-N01` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q01 empty and duplicate batch semantics
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:121–135`

```text
GIVEN ACTIVE A, NEW_MEMBER T1 and unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST request/ and direct create_mark_requests separately use targets [] or [T1.id,T1.id]
  AND value=2, reason="Workshop", date="2026-10-16"
THEN Q01 chooses empty reject/no-op and duplicate reject/deduplicate/multiple-row behavior
  AND response count must match committed row count under that choice
  AND a rejected batch leaves mark count and named rows unchanged
  AND accepted rows keep requester A and supplied content, never mutate Z
  AND profiles/roles/session identity remain unchanged
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-01-04b — test_ineligible_and_self_targets_require_policy

Parent: `NM-01-04` | Operation: `NM-N01` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q01 eligibility/self and Q03 mixed-batch integrity
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:121–134`

```text
GIVEN ACTIVE A, NEW_MEMBER T1, ALUMNI B and profileless user C
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN request POST and direct helper separately target [B.id],[C.id],[A.id],
  [T1.id,B.id] with value=2,reason="Workshop",date="2026-10-16"
THEN Q01 chooses target role/profile/self eligibility and mixed-batch handling
  AND rejection leaves all rows/count unchanged; acceptance stores only allowed target IDs
  AND requester must remain A and no existing mark content may change
  AND user/profile/role relations and session identity remain unchanged
  AND UI options alone are not evidence of server authorization
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-01-04c — test_invalid_target_identifiers_cannot_partially_persist

Parent: `NM-01-04` | Operation: `NM-N01` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D02 unsafe error exposure; Q03 for mixed-batch contract
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:121–137`

```text
GIVEN ACTIVE A, NEW_MEMBER T1, nonexistent user ID 999999 and unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN request POST and direct helper separately use ["abc"],[999999],[""],
  [T1.id,999999] with value=2,reason="Workshop",date="2026-10-16"
THEN invalid identifiers never result in a successful persisted invalid target
  AND no raw database/exception detail is exposed in the failure result
  AND inspect commit boundary before asserting completion, including deferred FK error
  AND direct helper additionally receives [None]; existing Z/users/roles/session identity are
      unchanged
  AND mixed-batch rollback versus partial acceptance is tracked separately under Q03
  AND assert_unchanged(before)
```

### NM-01-05a — test_request_helper_enforces_actor_authorization

Parent: `NM-01-05` | Operation: `NM-N01` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D03 helper lacks ACTIVE authorization
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:116–137`

```text
GIVEN A has roles (), (NEW_MEMBER), or (NM_BOARD), parameterized separately
  AND T1 is NEW_MEMBER; Z is B's existing mark
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN create_mark_requests(A,[T1.id],2,"Workshop","2026-10-16") is called directly
THEN result must deny actor lacking ACTIVE instead of inserting a mark
  AND no board-only auto-approved row can bypass the request view gate
  AND the named fixture rows is unchanged
  AND total mark count is unchanged
  AND helper execution creates no session or file changes
  AND assert_unchanged(before)
```

### NM-01-06a — test_batch_commit_failure_requires_atomicity_policy

Parent: `NM-01-06` | Operation: `NM-N01` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q03 transaction/error containment; PostgreSQL needed for backend-specific commit proof
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:118–137`

```text
GIVEN ACTIVE A, NEW_MEMBER T1/T2 and unrelated Z; use TransactionTestCase
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN multi-target creation Workshop/2/2026-10-16 fails at later bulk insert
  or deferred FK commit, parameterized deliberate database boundary failures
THEN Q03 chooses all-or-nothing rejection versus explicitly reported partial acceptance
  AND response/result must describe committed rows, never falsely claim full success
  AND rejected all-or-nothing outcome leaves mark count and Z unchanged
  AND partial outcome must identify exact persisted target set under chosen policy
  AND users/roles/files/session identity are unchanged after fresh committed reads
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```
