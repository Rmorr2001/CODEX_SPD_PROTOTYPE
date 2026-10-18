# Boundaries case designs

Use [the shared fixture contract](../../../../docs/testing/fixture-contract.md) and
[local fixture vocabulary and scope rules](../regression-spec.md#local-fixture-vocabulary).
All fixtures are created independently inside each case; none carry from earlier cases.
Non-admin relative routes in blocks are under `/newmember/`.
[Source, defects and decisions](../regression-spec.md) supply the linked policy gates.

### NM-00-01a — test_landing_renders_public_navigation

Parent: `NM-00-01` | Operation: `NM-N00` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:9–10`

```text
GIVEN business mode and actor A with no roles, plus anonymous client
  AND mark M belongs to requester B and target T1
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN each client GETs /newmember/
THEN response is 200 with newmember_dashboard.html
  AND marks, roster and alumni-roster links are present
  AND no external navigation is followed
  AND the named fixture rows is unchanged after fresh reads
  AND authenticated session identity is unchanged
  AND assert_unchanged(before)
```

### NM-SEC-01a — test_anonymous_routes_redirect_to_login

Parent: `NM-SEC-01` | Operation: `NM-N01–NM-N07` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:12–188`

```text
GIVEN anonymous csrf_client(), mark M=41 and target T1=51
  AND a real CSRF cookie/token pair is acquired from the login form
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN GET and token-bearing POST are sent separately to /newmember/marks/,
  /request/, /approve/, /edit/41/, /history/51/, /export-newmember-marks/
THEN each response redirects to configured login with the matching next URL
  AND response bodies disclose none of M's reason, value or requester name
  AND the named fixture rows is unchanged; no authenticated identity is created
  AND route suffixes above are all relative to /newmember/
  AND assert_unchanged(before)
```

### NM-SEC-02a — test_request_requires_explicit_active_role

Parent: `NM-SEC-02` | Operation: `NM-N01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:46–50`

```text
GIVEN A has roles parameterized as (), (ALUMNI), (EXEC), (NME), (NM_BOARD)
  AND T1 is NEW_MEMBER; M is another requester's mark
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN login_actor(client,A); GET then POST /newmember/request/
  AND POST has target_users=[T1.id], mark_value="2", mark_reason="Workshop",
      mark_date="2026-10-16"
THEN each response redirects to newmember_marks_dashboard with active-only error
  AND no mark is inserted; the named fixture rows is unchanged
  AND session authenticated user remains A
  AND assert_unchanged(before)
```

### NM-SEC-02b — test_review_and_regular_edit_require_board_role

Parent: `NM-SEC-02` | Operation: `NM-N02,NM-N03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:70–74,121–126`

```text
GIVEN A has roles parameterized as (), (ACTIVE), (ALUMNI), (EXEC), (NME)
  AND M is requested by B for T1; another variant makes A the requester
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs and POSTs /newmember/approve/ and /newmember/edit/M.id/
  AND approval payload is {mark_id:M.id,action:"approve"}
  AND edit payload is {action:"update",mark_reason:"Lab",mark_value:"-2",
      mark_date:"2026-10-16",target_user:T1.id}
THEN responses redirect to marks dashboard with board-only error
  AND the named fixture rows and session identity are unchanged
  AND assert_unchanged(before)
```

### NM-SEC-02c — test_edit_deny_requires_both_roles

Parent: `NM-SEC-02` | Operation: `NM-N04` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:124–136`

```text
GIVEN A has only NM_BOARD or only NME, parameterized separately
  AND M is requested by B for T1, with own-request variant B=A
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A POSTs /newmember/edit/M.id/ with {action:"deny"}
THEN response redirects to marks dashboard with permission error
  AND board-only actor receives educator-only error
  AND NME-only actor receives board-only error
  AND the named fixture rows is unchanged
  AND session identity remains A
  AND assert_unchanged(before)
```

### NM-SEC-03a — test_mutating_routes_reject_missing_or_bad_csrf

Parent: `NM-SEC-03` | Operation: `NM-N01–NM-N04` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/templates/newmember_marks_request.html:11–12`

```text
GIVEN csrf_client() logged in as ACTIVE+NM_BOARD+NME A
  AND M is pending for T1; obtain cookie/token from each corresponding GET form
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST request/, approve/, or edit/M.id/ under /newmember/
  AND each payload uses csrfmiddlewaretoken absent or "wrong-token"
  AND use create Workshop/2/2026-10-16/T1, approve M, update M, and deny M variants
THEN every response is 403 without successful operation message
  AND no new marks exist; the named fixture rows is unchanged
  AND authenticated session identity remains A
  AND assert_unchanged(before)
```

### NM-SEC-03b — test_create_accepts_acquired_csrf_token

Parent: `NM-SEC-03` | Operation: `NM-N01–NM-N04` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/templates/newmember_marks_approve.html:58–63`

```text
GIVEN csrf_client() logged in as ACTIVE+NM_BOARD+NME A
  AND B's pending M for NEW_MEMBER T1; A differs from B/T1; unrelated Z exists
  AND at_time(2026-10-17T12:00Z); GET corresponding form for real cookie/token
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST /newmember/request/ uses acquired token and
      {target_users:[T1.id],mark_reason:"Workshop",mark_value:"2",mark_date:"2026-10-16"}
THEN response redirects to marks dashboard with success
  AND new row is approved with requester A,target T1,value 2,Workshop,Oct16 and A approval audit
  AND mark count increases exactly one; M remains unchanged
  AND Z/users/profiles/roles and session identity remain unchanged
  AND assert_unchanged(before)
```

### NM-SEC-03c — test_approve_accepts_acquired_csrf_token

Parent: `NM-SEC-03` | Operation: `NM-N01–NM-N04` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/templates/newmember_marks_approve.html:58–63`

```text
GIVEN csrf_client() logged in as ACTIVE+NM_BOARD+NME A
  AND B's pending M for NEW_MEMBER T1; A differs from B/T1; unrelated Z exists
  AND at_time(2026-10-17T12:00Z); GET corresponding form for real cookie/token
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST /newmember/approve/ uses acquired token and {mark_id:M.id,action:"approve"}
THEN response is 200 review template with success
  AND M becomes approved with A profile name and frozen approval time
  AND mark count is unchanged; M requester/submission time remain unchanged
  AND Z/users/profiles/roles and session identity remain unchanged
  AND assert_unchanged(before,
      except_fields={M:{mark_approval_status,mark_approver_name,mark_submission_approval_date}})
```

### NM-SEC-03d — test_update_accepts_acquired_csrf_token

Parent: `NM-SEC-03` | Operation: `NM-N01–NM-N04` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/templates/newmember_marks_approve.html:58–63`

```text
GIVEN csrf_client() logged in as ACTIVE+NM_BOARD+NME A
  AND B's pending M for NEW_MEMBER T1; A differs from B/T1; unrelated Z exists
  AND at_time(2026-10-17T12:00Z); GET corresponding form for real cookie/token
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST /newmember/edit/M.id/ uses acquired token and
      {action:"update",mark_reason:"Lab",mark_value:"-2",mark_date:"2026-10-16",target_user:T1.id}
THEN response redirects to T1 history with success
  AND M content becomes Lab/-2/Oct16, target remains T1 and editor is A at frozen time
  AND mark count is unchanged; M requester/submission time remain unchanged
  AND Z/users/profiles/roles and session identity remain unchanged
  AND assert_unchanged(before,
      except_fields={M:{mark_event_title,mark_value,mark_event_date,last_edited_by,last_edited_at}})
```

### NM-SEC-03e — test_edit_deny_accepts_acquired_csrf_token

Parent: `NM-SEC-03` | Operation: `NM-N01–NM-N04` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/templates/newmember_marks_approve.html:58–63`

```text
GIVEN csrf_client() logged in as ACTIVE+NM_BOARD+NME A
  AND B's pending M for NEW_MEMBER T1; A differs from B/T1; unrelated Z exists
  AND at_time(2026-10-17T12:00Z); GET corresponding form for real cookie/token
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST /newmember/edit/M.id/ uses acquired token and {action:"deny"}
THEN response redirects to marks dashboard with success
  AND M becomes denied with A approval name/time and A editor/time
  AND mark count is unchanged; M requester/submission time remain unchanged
  AND Z/users/profiles/roles and session identity remain unchanged
  AND assert_unchanged(before,
      except_fields={M:{mark_approval_status,mark_approver_name,mark_submission_approval_date,last_edited_by,last_edited_at}})
```

### NM-SEC-04a — test_profileless_actor_fails_safely

Parent: `NM-SEC-04` | Operation: `NM-N01–NM-N07` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D01 missing-profile dereference; response adapter follows shared error policy
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:190–192`

```text
GIVEN A=make_user(username="profileless",with_profile=False)
  AND B requested M for NEW_MEMBER T1; snapshot_scope([A,B,M,T1])
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs marks/, request/, approve/, edit/M.id/, history/T1.id/,
  and export-newmember-marks/?pclass=Current under /newmember/
THEN no response exposes a relation exception or traceback
  AND protected operations return a controlled non-success result
  AND fresh named rows and mark count remain unchanged
  AND session identity remains A; /newmember/ still renders 200
  AND assert_unchanged(before)
```
