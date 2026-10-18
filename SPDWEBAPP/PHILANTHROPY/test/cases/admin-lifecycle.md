# Domain admin C03 and model lifecycle

Use the [shared fixture contract](../../../../docs/testing/fixture-contract.md) and
[domain decisions](../regression-spec.md#decisions-and-defects).
Business settings are the default; no fixture uses real people, network or uploads.
Named event fixtures use real ORM rows. T0/T1/T2/T3 denote distinct aware UTC times;
when an exact instant is shown, at_time patches each clock that consumes it.
Use snapshot_scope on each named row and role/permission relation before acting;
assert_unchanged refreshes it, allowing only explicitly named successful changes.
Compare authenticated user identity, not the complete messages/CSRF session blob.
For authenticated request designs, GIVEN uses login_actor(client, the named actor);
csrf_client() constructs an enforcing client and never authenticates by itself.
Profile-role snapshots exclude users explicitly created without a profile.
A_profile (and each corresponding user_profile alias) is read through that User's
brother_profile ORM relation; profile defaults never confer additional roles.

### PH-C30a — test_admin_list_obeys_staff_and_model_permissions

Parent: `PH-C30` | Operation: `PH-C03-A` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; B owns E and F; chair_no_staff has ACTIVE+PHIL_CHAIR but no staff
  AND S_none is staff/no permissions, S_view is staff/view permission, S_super is staff superuser
  AND permissions reference PHILANTHROPY.philanthropy_hours_event_and_request
  AND before = snapshot_scope([chair_no_staff,S_none,S_view,S_super,B,E,F],
      relations=(chair_no_staff_profile.roles, S_none_profile.roles, S_view_profile.roles,
      S_super_profile.roles, B_profile.roles, S_none.user_permissions, S_view.user_permissions,
      S_super.user_permissions))
WHEN each actor GETs
      reverse("admin:PHILANTHROPY_philanthropy_hours_event_and_request_changelist")
THEN nonstaff redirects302 to admin login and staff without model permission gets403
  AND view-only staff and superuser get200 with title/user/status/hours/date columns
  AND E/F, actors, profiles, roles, permissions and admin LogEntry count are unchanged
```

### PH-C30b — test_admin_permission_denied_add_and_change_do_not_write

Parent: `PH-C30` | Operation: `PH-C03-A` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; staff A has view permission only; B owns requested E and approved F
  AND before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles, A.user_permissions))
WHEN A POSTs admin add with {user:B.id,philanthropy_event_title:"Park",
      philanthropy_event_hours:"2",philanthropy_event_date:"2026-07-01",
      philanthropy_approval_status:"requested"}
  AND separately POSTs E change with those fields and title:"Edited"
THEN both responses are 403; neither event nor LogEntry is inserted
  AND E/F, actors, profile roles and permission relations remain unchanged
```

### PH-C30c — test_admin_permission_sets_do_not_imply_domain_roles

Parent: `PH-C30` | Operation: `PH-C03-A` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; staff S_add/S_change/S_delete have exactly add/change/delete permissions
  AND no actor has a domain role; B owns requested E and unrelated F
  AND before = snapshot_scope([S_add,S_change,S_delete,B,E,F],
      relations=(S_add_profile.roles, S_change_profile.roles, S_delete_profile.roles,
      B_profile.roles, S_add.user_permissions, S_change.user_permissions,
      S_delete.user_permissions))
WHEN each actor GETs model add and E change/delete confirmation URLs
THEN add actor may GET add200, change actor may GET E change200, delete actor may GET delete200
  AND missing add/change/delete permissions deny the corresponding edit operation403
  AND any read-only change-form access follows Django view-or-change permissions explicitly
  AND E/F, actor roles/permissions and LogEntry count remain unchanged
```

### PH-C31a — test_admin_adds_integer_event_and_django_log

Parent: `PH-C31` | Operation: `PH-C03-A` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; staff S has add and view model permissions; ACTIVE B owns unrelated F
  AND at_time("2026-07-02T12:00:00Z"); before = snapshot_scope([S,B,F],
      relations=(S_profile.roles, B_profile.roles, S.user_permissions))
WHEN S POSTs admin add {user:B.id,philanthropy_event_title:"Park",
      philanthropy_event_hours:"2",philanthropy_event_date:"2026-07-01",
      philanthropy_approval_status:"requested",_save:"Save"}
THEN response redirects302 to model changelist; exactly one requested B event is created
  AND title/hours/date are "Park"/2/2026-07-01; submission time is frozen time
  AND decision/editor fields are null and one ADDITION LogEntry names S/new event
  AND F, actors, profile roles and permission relations remain unchanged
```

### PH-C31b — test_admin_change_authority_and_domain_audit_need_policy

Parent: `PH-C31` | Operation: `PH-C03-A` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q11 staff owner/status/audit authority; Q1/Q3/Q4 parity
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; staff S has change permission; B owns approved E with decision D/T1
  AND E has old editor C/T2; A owns unrelated F
  AND before = snapshot_scope([S,B,A,C,E,F],
      relations=(S_profile.roles, B_profile.roles, A_profile.roles, C_profile.roles,
      S.user_permissions, A.user_permissions))
WHEN S POSTs E change {user:A.id,philanthropy_event_title:"Updated",
      philanthropy_event_hours:"3",philanthropy_event_date:"2026-07-03",
      philanthropy_approval_status:"denied",_save:"Save"}
THEN Q11 chooses permitted owner/status changes and required domain editor/decision audit
  AND rejection preserves every E field and adds no LogEntry
  AND accepted changes match the policy whitelist and create one CHANGE LogEntry for S
  AND F, actors, roles and permissions remain unchanged; Django log is not domain audit
```

### PH-C31c — test_admin_model_form_rejects_invalid_fields_without_logs

Parent: `PH-C31` | Operation: `PH-C03-A` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; staff S has add/change permissions; B owns requested E and approved F
  AND base form is {user:B.id,philanthropy_event_title:"Park",philanthropy_event_hours:"2",
      philanthropy_event_date:"2026-07-01",philanthropy_approval_status:"requested"}
  AND before = snapshot_scope([S,B,E,F],
      relations=(S_profile.roles, B_profile.roles, S.user_permissions))
WHEN S POSTs add or E change independently with philanthropy_approval_status:"bogus",
      omitted user/title/date/hours key, philanthropy_event_title as 101 "x" characters,
      philanthropy_event_hours:"1.5"/"NaN"/"abc", or philanthropy_event_date:"abc"/"2026-02-30"
THEN response is 200 form with field errors, never save success
  AND E/F and event count remain unchanged; no LogEntry is added
  AND S, B, profile roles and permission relations remain unchanged
```

### PH-C31d — test_admin_negative_hours_need_business_parity_policy

Parent: `PH-C31` | Operation: `PH-C03-A` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q1 shared minimum; Q11 admin exception versus parity
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; staff S has add/change permissions; B owns requested E and approved F
  AND before = snapshot_scope([S,B,E,F],
      relations=(S_profile.roles, B_profile.roles, S.user_permissions))
WHEN S POSTs admin add and separately E change with {user:B.id,
      philanthropy_event_title:"Park",philanthropy_event_hours:"-1",
      philanthropy_event_date:"2026-07-01",philanthropy_approval_status:"requested"}
THEN Q1/Q11 choose whether admin must enforce the member-operation minimum
  AND rejection creates no event/LogEntry and preserves E
  AND any explicit exception must be documented before negative values are accepted
  AND F, actors, profile role relations and permissions remain unchanged
```

### PH-C32a — test_admin_delete_confirmation_does_not_delete

Parent: `PH-C32` | Operation: `PH-C03-A` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; staff S has delete permission; B owns E and unrelated F
  AND before = snapshot_scope([S,B,E,F],
      relations=(S_profile.roles, B_profile.roles, S.user_permissions))
WHEN S GETs reverse("admin:PHILANTHROPY_philanthropy_hours_event_and_request_delete",args=[E.id])
THEN response is 200 confirmation describing E
  AND E/F still exist with every field unchanged
  AND S/B, roles, permissions and LogEntry count remain unchanged
  AND confirmation is distinct from authorizing hard-delete retention policy
```

### PH-C32b — test_admin_single_delete_needs_retention_policy

Parent: `PH-C32` | Operation: `PH-C03-A` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q11 hard deletion/audit retention
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; staff S has delete permission; B owns E and unrelated F
  AND before = snapshot_scope([S,B,E,F],
      relations=(S_profile.roles, B_profile.roles, S.user_permissions))
WHEN S POSTs E admin delete confirmation with {post:"yes"}
THEN Q11 chooses hard deletion or refusal/retained audit representation
  AND permitted deletion removes only E and records S's DELETION LogEntry
  AND refused deletion leaves E intact with no successful-deletion log
  AND F, actors, role relations and permissions remain unchanged
```

### PH-C32c — test_admin_bulk_delete_needs_retention_policy

Parent: `PH-C32` | Operation: `PH-C03-A` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q11 bulk deletion/audit retention
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; staff S has delete permission; B owns selected E1/E2 and unselected F
  AND before = snapshot_scope([S,B,E1,E2,F],
      relations=(S_profile.roles, B_profile.roles, S.user_permissions))
WHEN S POSTs changelist {action:"delete_selected",_selected_action:[E1.id,E2.id]}
  AND confirms with {action:"delete_selected",_selected_action:[E1.id,E2.id],post:"yes"}
THEN Q11 chooses whether bulk hard deletion is allowed or refused
  AND allowed deletion removes exactly E1/E2 and records matching Django deletion logs
  AND refusal preserves both selected rows; F is unchanged in either outcome
  AND actors, profile roles, permission relations and unrelated logs are unchanged
```

### PH-C32d — test_admin_delete_denial_preserves_events_and_logs

Parent: `PH-C32` | Operation: `PH-C03-A` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN business settings; staff S has view/change but no delete permission
  AND B owns E/F; before = snapshot_scope([S,B,E,F],
      relations=(S_profile.roles, B_profile.roles, S.user_permissions))
WHEN S POSTs E delete {post:"yes"}
  AND separately tries bulk {action:"delete_selected",_selected_action:[E.id],post:"yes"}
THEN single deletion gets403; bulk action is unavailable/rejected without deletion
  AND E/F retain all fields and event count is unchanged
  AND no DELETION LogEntry appears; users, roles and permission relations are unchanged
```

### PH-C32e — test_owner_deletion_cascade_needs_retention_policy

Parent: `PH-C32` | Operation: `PH-C03-A` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q11 event retention after owner deletion
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN B owns E and F; A owns unrelated G
  AND B's profile exists; before = snapshot_scope([A,B,E,F,G],
      relations=(A_profile.roles, B_profile.roles, A.user_permissions))
WHEN a real ORM operation deletes User B
THEN source FK behavior cascades E/F and B's profile
  AND Q11 chooses preserving this cascade versus retained historical/audit records
  AND G and A's profile/roles remain unchanged
  AND any permitted cascade deletes exactly the rows linked by the approved retention rule
```

### PH-C32f — test_editor_deletion_sets_null_on_other_owners_event

Parent: `PH-C32` | Operation: `PH-C03-A` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/admin.py:8–16; SPDWEBAPP/PHILANTHROPY/models.py:5–44`

```text
GIVEN B owns approved E last edited by User C; A owns unrelated F
  AND C owns no event and has no profile; before = snapshot_scope([A,B,C,E,F],
      relations=(A_profile.roles, B_profile.roles, A.user_permissions))
WHEN ORM deletes C
THEN E survives with last_edited_by null and original last_edited_at retained
  AND E owner/title/hours/date/status/submission/decision fields remain unchanged
  AND F, A, B and their profile roles remain unchanged
  AND no domain approval audit or Django admin LogEntry is manufactured
```
