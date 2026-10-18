# Admin case designs

Use [the shared fixture contract](../../../../docs/testing/fixture-contract.md) and
[local fixture vocabulary and scope rules](../regression-spec.md#local-fixture-vocabulary).
All fixtures are created independently inside each case; none carry from earlier cases.
Non-admin relative routes in blocks are under `/newmember/`.
[Source, defects and decisions](../regression-spec.md) supply the linked policy gates.

### NM-C03-01a — test_admin_nonstaff_redirects_even_with_board_role

Parent: `NM-C03-01` | Operation: `NM-C03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/admin.py:6–15`

```text
GIVEN business mode, NM_BOARD nonstaff A, existing M and unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs reversed admin marks changelist/add/change/delete URLs for M
THEN each response redirects to admin login with next URL
  AND no model data or successful action form is disclosed
  AND no app-role-to-admin permission promotion occurs
  AND M/Z/users/profiles/roles remain unchanged
  AND authenticated session identity remains A
  AND mark count is unchanged
  AND assert_unchanged(before)
```

### NM-C03-01b — test_admin_changelist_shows_configured_columns

Parent: `NM-C03-01` | Operation: `NM-C03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/admin.py:8–15`

```text
GIVEN business mode and superuser S without domain roles
  AND approved M1 Oct16 and requested M2 Oct15
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN S GETs reversed marks admin changelist URL
THEN response is 200 and displays title,target,requester,status,value,event date columns
  AND M1 precedes M2 by model event-date descending order
  AND no domain role is silently added to S
  AND the named fixture rows remains unchanged
  AND demo middleware behavior is not used to infer this result
  AND assert_unchanged(before)
```

### NM-C03-01c — test_admin_staff_without_permissions_is_forbidden

Parent: `NM-C03-01` | Operation: `NM-C03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/admin.py:6–15`

```text
GIVEN business mode, staff S with no model permissions, M and unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN S GETs reversed admin marks changelist/add/change/delete URLs for M
THEN every response is 403
  AND no successful action form or protected mark details appear
  AND M/Z/users/profiles/roles remain unchanged
  AND S permission relations remain empty
  AND authenticated session identity remains S
  AND mark count is unchanged
  AND assert_unchanged(before)
```

### NM-C03-01d — test_admin_staff_explicit_permission_allows_corresponding_page

Parent: `NM-C03-01` | Operation: `NM-C03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/admin.py:6–15`

```text
GIVEN business mode, staff S and existing M plus unrelated Z
  AND permission/page pairs are view/changelist,add/add,change/change,delete/delete
  AND S receives that explicit Django permission before the snapshot
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN each fresh permitted S GETs the corresponding URL
THEN response is 200 for that page
  AND view permission permits read-only change GET but does not authorize writes
  AND no domain roles are added and no domain role substitutes for the permission
  AND M/Z/users/profiles/roles/permissions remain unchanged after request
  AND authenticated session identity remains S
  AND assert_unchanged(before)
```

### NM-C03-01e — test_admin_staff_without_write_permission_cannot_add_or_change

Parent: `NM-C03-01` | Operation: `NM-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/admin.py:6–15`

```text
GIVEN business mode, staff S with view but no add/change permission, M and unrelated Z
  AND T1 is NEW_MEMBER; requester B is distinct from S
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN S POSTs reversed admin add/change URLs with Workshop/2/2026-10-16,
  status requested,requesting_user B.id,target_user T1.id and _save="Save"
THEN each response is 403, never a successful change redirect
  AND no new row appears; every M/Z content/status/requester/target/audit field is unchanged
  AND all users/profiles/roles/permission relations and session identity remain unchanged
  AND assert_unchanged(before)
```

### NM-C03-01f — test_admin_nonstaff_cannot_add_or_change_through_admin

Parent: `NM-C03-01` | Operation: `NM-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/admin.py:6–15`

```text
GIVEN business mode, NM_BOARD nonstaff A, M and unrelated Z
  AND T1 is NEW_MEMBER; requester B is distinct from A
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A POSTs reversed admin add/change URLs with Workshop/2/2026-10-16,
  status requested,requesting_user B.id,target_user T1.id and _save="Save"
THEN each response is 302 to admin login, never a successful change redirect
  AND no new row appears; every M/Z content/status/requester/target/audit field is unchanged
  AND all users/profiles/roles/permission relations and session identity remain unchanged
  AND assert_unchanged(before)
```

### NM-C03-02a — test_admin_forms_reject_invalid_model_fields

Parent: `NM-C03-02` | Operation: `NM-C03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/admin.py:6–15; models.py:11–39`

```text
GIVEN business mode and staff S with add/change model permissions; existing M
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST admin add/change overrides one Workshop/2/2026-10-16/requested/requester/target field
  WITH value="abc",date="2026-02-30",status="unknown",requester omitted,or target omitted
THEN response is 200 with field errors, not a successful change redirect
  AND no new row is added; every existing M field remains unchanged
  AND users/profiles/roles and permission relations stay unchanged
  AND authenticated identity remains S
  AND each invalid field is an independent fresh fixture variant
  AND assert_unchanged(before)
```

### NM-C03-02b — test_admin_write_audit_and_transition_parity_need_policy

Parent: `NM-C03-02` | Operation: `NM-C03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q10 admin authorization/transition/audit parity
Source: `SPDWEBAPP/NEWMEMBER/admin.py:6–15; models.py:24–53`

```text
GIVEN business mode and permitted staff S with no domain roles; A's requested M for T1
  AND declare T2,Z using the linked local fixture vocabulary
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN S adds approved Workshop/2/2026-10-16 or changes M target to T2/status approved
THEN Q10 chooses standard model-permission write versus domain role/transition enforcement
  AND Q10 chooses explicit audit fields versus actor-derived required audit
  AND allowed write changes only chosen content/status/target/audit fields
  AND rejected write preserves M and creates no new row
  AND unrelated Z/users/roles/session identity stay unchanged
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-C03-02c — test_mark_string_representation_names_target

Parent: `NM-C03-02` | Operation: `NM-C03` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/models.py:55–56`

```text
GIVEN NEW_MEMBER target username="target-one" and mark title="Workshop",value=-3
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN str(mark) is evaluated with real ORM relationships
THEN string is "Workshop - target-one (-3)"
  AND status/approval/editor audit do not alter this representation
  AND requester name is not substituted for target username
  AND refreshed mark and requester/target/profile/role rows remain unchanged
  AND no database writes occur
  AND no files or sessions are required
  AND assert_unchanged(before)
```

### NM-C03-03a — test_admin_mark_delete_removes_only_selected_mark

Parent: `NM-C03-03` | Operation: `NM-C03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/admin.py:6–15; models.py:11–20`

```text
GIVEN business mode, staff S with delete/view permissions, M and unrelated Z
  AND before = snapshot_scope(scope_rows excluding M, relations=scope_relations, files=scope_files)
WHEN S GETs reversed M delete confirmation then POSTs {post:"yes"}
THEN confirmation is 200 and successful deletion redirects to permitted changelist
  AND M no longer exists; Z remains identical after refresh
  AND requester/target/editor users/profiles/roles are unchanged
  AND no unrelated mark is deleted
  AND session identity remains S
  AND actual Django permissions are attached explicitly
  AND assert_unchanged(before)
```

### NM-C03-03b — test_foreign_key_deletion_retention_needs_policy

Parent: `NM-C03-03` | Operation: `NM-C03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q10 retention/cascade policy
Source: `SPDWEBAPP/NEWMEMBER/models.py:11–20,47–53`

```text
GIVEN M with distinct requester A,target T1,editor R; unrelated Z belongs to B/T2
  AND before = snapshot_scope(scope_rows excluding A,T1,R,M,
      relations=scope_relations excluding deletion subjects, files=scope_files)
WHEN A,T1,or R is deleted through authorized admin/local ORM in separate fixtures
THEN Q10 chooses whether requester/target cascades remain or retention must protect marks
  AND current editor deletion sets last_edited_by=None; remaining audit/content stays intact
  AND under retained cascade policy M disappears only for requester/target deletion
  AND under protective policy chosen protected rows must remain intact
  AND Z/B/T2 and surviving users/roles are unchanged
  AND no accidental deletion of unrelated historical records is permitted
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-C03-03c — test_admin_delete_without_permission_preserves_records

Parent: `NM-C03-03` | Operation: `NM-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/admin.py:6–15`

```text
GIVEN business mode and staff S with view but no delete permission
  AND M with requester A,target T1,editor R plus unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN S GETs and POSTs reversed M delete URL with {post:"yes"}
THEN each response is 403
  AND M/Z still exist with every field unchanged after refresh
  AND A/T1/R/users/profiles/roles remain unchanged
  AND S permission relations are unchanged
  AND authenticated identity stays S
  AND assert_unchanged(before)
```
