# History Filter case designs

Use [the shared fixture contract](../../../../docs/testing/fixture-contract.md) and
[local fixture vocabulary and scope rules](../regression-spec.md#local-fixture-vocabulary).
All fixtures are created independently inside each case; none carry from earlier cases.
Non-admin relative routes in blocks are under `/newmember/`.
[Source, defects and decisions](../regression-spec.md) supply the linked policy gates.

### NM-06-01a — test_history_helper_returns_approved_target_total

Parent: `NM-06-01` | Operation: `NM-N06` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:177–188`

```text
GIVEN NEW_MEMBER T1 approved +4 Oct14/-7 Oct16 and requested/denied +99
  AND NEW_MEMBER T2 approved +20; unrelated Z exists
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN get_member_mark_history(T1.id) runs
THEN rows are T1 approved Oct16 then Oct14 and total=-3
  AND no T2 or unapproved row is included
  AND fresh fields on every named mark and user/profile/role remain unchanged
  AND no session or file writes occur
  AND signed values remain negative/positive integers
  AND assert_unchanged(before)
```

### NM-06-01b — test_history_view_audience_and_edit_flags_need_policy

Parent: `NM-06-01` | Operation: `NM-N06` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q07 cross-member history visibility
Source: `SPDWEBAPP/NEWMEMBER/views.py:93–117; templates/newmember_marks_history.html:35–47`

```text
GIVEN NEW_MEMBER T1 approved +4/-7 and edit audit on the -7 row; NEW_MEMBER T2 has +20
  AND viewers T1, other NEW_MEMBER, ACTIVE, no-role and NM_BOARD R
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN each viewer GETs history/T1.id/ under /newmember/
THEN Q07 chooses owner-only, role-restricted or all-login audience
  AND permitted response is 200,total=-3,is_negative=True, approved rows only
  AND permitted board viewer gets edit links; edited row gets [EDITED] marker
  AND denied audience cannot see T1 content; all named rows/roles stay unchanged
  AND each authenticated identity stays unchanged
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-06-02a — test_missing_or_non_new_member_history_redirects

Parent: `NM-06-02` | Operation: `NM-N06` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:95–117`

```text
GIVEN ACTIVE viewer A, unrelated M, ALUMNI target B and profileless C
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs history/999999/, history/B.id/, history/C.id/ under /newmember/
  AND ID 999999 is absent
THEN each response redirects to newmember_dashboard
  AND error message says New Member not found
  AND no mark details or success message appear
  AND the named fixture rows and mark count are unchanged
  AND session identity remains A
  AND assert_unchanged(before)
```

### NM-06-02b — test_empty_target_history_helper_returns_zero

Parent: `NM-06-02` | Operation: `NM-N06` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:177–188`

```text
GIVEN NEW_MEMBER T1 has no marks; T2 has approved M
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN get_member_mark_history(T1.id) runs
THEN rows are empty and total is 0, not None
  AND direct helper on T2.id returns only M and its signed value
  AND helper does not take or mutate a viewer actor
  AND the named fixture rows is unchanged
  AND mark count is unchanged
  AND no files or session writes occur
  AND assert_unchanged(before)
```

### NM-06-02c — test_empty_history_view_needs_audience_policy

Parent: `NM-06-02` | Operation: `NM-N06` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q07 history audience
Source: `SPDWEBAPP/NEWMEMBER/views.py:95–113`

```text
GIVEN NEW_MEMBER T1 has no marks and ACTIVE viewer A has a profile
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs /newmember/history/T1.id/
THEN Q07 decides whether A may view this other target
  AND allowed output is 200 with empty marks,total_marks=0,is_negative=False
  AND denied output reveals no protected target data
  AND no new marks or audit records are created
  AND the named fixture rows is unchanged
  AND authenticated identity stays A
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-08-01a — test_hours_remaining_converts_numbers_and_floors_zero

Parent: `NM-08-01` | Operation: `NM-N08` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/templatetags/newmember_extras.py:5–7`

```text
GIVEN numeric pairs (10,3),(10,12),(0,0),("10","2.5"),(-2,-5)
WHEN hours_remaining(goal,current) runs and a template loads newmember_extras
THEN results are 7.0,0,0,7.5,3.0 respectively
  AND the registered filter yields the corresponding numeric value
  AND no models or users need to be constructed
  AND no database, file or session writes occur
  AND numeric strings use float conversion
  AND this local filter is separate from PHILANTHROPY's identically named filter
```

### NM-08-01b — test_invalid_and_nonfinite_filter_operands_need_policy

Parent: `NM-08-01` | Operation: `NM-N08` | Priority: P2
Status: `POLICY_BLOCKED` | Blockers: Q08 invalid/nonfinite filter behavior
Source: `SPDWEBAPP/NEWMEMBER/templatetags/newmember_extras.py:6–7`

```text
GIVEN operand pairs (None,1),("abc",1),("nan",1),("inf",1),(10,"-inf")
WHEN hours_remaining and rendered template filter receive each pair separately
THEN Q08 chooses controlled rejection or a documented fallback/nonfinite result
  AND direct and template behavior must be consistent with that choice
  AND no arbitrary exception or NaN value is asserted as approved policy
  AND no database users/marks need to be constructed
  AND no files or session writes occur
  AND the unused-filter removal question remains distinct from numeric behavior
```
