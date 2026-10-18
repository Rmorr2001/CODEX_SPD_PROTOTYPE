# Admin CSRF, deletion, audit and transaction boundaries

Use [shared fixtures](../../../../docs/testing/fixture-contract.md), business mode
unless explicitly testing demo boundary. Reverse admin model routes.
`admin_staff` is make_user(username="admin-staff",is_staff=True,roles=()) with
view/add/change/delete permissions explicitly attached for the parameterized model.
Announcement fixtures use title/content; DST fixtures use name/is_active.
No model has related business rows or files to cascade/compensate.

<a id="misc-t25a"></a>

### MISC-T25a — test_admin_mutations_reject_missing_or_bad_csrf_token

Parent: `MISC-T25` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff logged in using csrf_client() and login_actor
  AND A={title:"Keep",content:"Text"}; S={name:"Keep",is_active:True}
  AND before=snapshot_scope([A,S]); CSRF variants separately absent and "bad-token"
WHEN POSTing each model's add/change/delete/changelist action URL with that token
  AND announcement body={title:"New",content:"Text",_save:"1"}; DST={name:"New",_save:"1"}
  AND detail-delete body={post:"yes"}; bulk={action:"delete_selected",_selected_action:[target.pk],post:"yes"}
THEN every response is 403; assert_unchanged(before)
  AND no object or LogEntry is added/deleted/changed; actor session identity remains unchanged
```

<a id="misc-t25b"></a>

### MISC-T25b — test_admin_valid_csrf_pair_allows_intended_write

Parent: `MISC-T25` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN fresh csrf_client logged in as admin_staff for each model/action variant
  AND A={title:"Keep",content:"Text"}; S={name:"Keep",is_active:True}; untouched B/T
  AND GET corresponding form/changelist to acquire its real cookie/token pair
  AND before=snapshot_scope([A,S,B,T])
WHEN POSTing add/edit payload {title:"New",content:"Text",_save:"1"} or {name:"New",_save:"1"}
  AND separately detail delete {post:"yes"} or bulk {action:"delete_selected",_selected_action:[target.pk],post:"yes"}
  AND each POST supplies that rendered token and matching cookie
THEN response is 302 and exactly one intended create/update/delete occurs
  AND corresponding single ADDITION/CHANGE/DELETION LogEntry identifies actor and target
  AND unrelated B/T and other model rows remain unchanged; session identity is unchanged
```

<a id="misc-t25c"></a>

### MISC-T25c — test_demo_boundary_blocks_model_admin_even_with_permission

Parent: `MISC-T25` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN demo mode and synthetic make_user(username="demo-staff",is_staff=True)
  AND both models' view/add/change/delete permissions; login_actor authenticates user
  AND A={title:"Keep",content:"Text"}; S={name:"Keep",is_active:True}
  AND before=snapshot_scope([A,S])
WHEN HTTPS GETs /admin/ and each reversed model admin form/list URL
THEN responses are 403 under current demo admin prefix
  AND no model form or private alert content is disclosed
  AND assert_unchanged(before); no LogEntry or session-identity change occurs
  AND AUTHENTICATE owns full demo-boundary assertions
```

<a id="misc-t26a"></a>

### MISC-T26a — test_detail_delete_confirmation_get_is_read_only

Parent: `MISC-T26` | Operation: `MISC-O11` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff and target A={title:"Delete me",content:"Text"} or S={name:"Delete me"}
  AND untouched second row; before=snapshot_scope(target and second row)
WHEN GETting target's reversed delete URL
THEN response is 200 with target representation and confirmation form
  AND target remains in database with same fields
  AND assert_unchanged(before); no DELETION LogEntry is created
  AND session identity remains admin_staff
```

<a id="misc-t26b"></a>

### MISC-T26b — test_detail_delete_removes_only_target_and_logs_once

Parent: `MISC-T26` | Operation: `MISC-O11` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff, target A={title:"Delete me",content:"Text"} or S={name:"Delete me"}
  AND untouched second row B/T; before=snapshot_scope([B,T])
WHEN actor POSTs target delete URL {post:"yes"}
THEN response is 302 to model changelist and target no longer exists
  AND one DELETION LogEntry identifies target PK/content type/representation and actor
  AND assert_unchanged(before); other model rows and session identity are unchanged
  AND no file operation or unrelated cascade occurs
```

<a id="misc-t26c"></a>

### MISC-T26c — test_bulk_delete_confirmation_preserves_selected_rows

Parent: `MISC-T26` | Operation: `MISC-O11` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; model targets X/Y and untouched Z with concrete names "First","Second","Keep"
  AND announcement rows also have content="Text"; before=snapshot_scope([X,Y,Z])
WHEN POSTing model changelist {action:"delete_selected",index:"0",_selected_action:[X.pk,Y.pk]}
THEN response is 200 confirmation listing X and Y, not Z
  AND all three rows still exist with original fields
  AND assert_unchanged(before); no DELETION LogEntry is written
  AND session identity remains admin_staff
```

<a id="misc-t26d"></a>

### MISC-T26d — test_confirmed_bulk_delete_keeps_unselected_records

Parent: `MISC-T26` | Operation: `MISC-O11` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; model targets X/Y and untouched Z with names "First","Second","Keep"
  AND announcement rows have content="Text"; before=snapshot_scope([Z])
WHEN POSTing changelist {action:"delete_selected",_selected_action:[X.pk,Y.pk],post:"yes"}
THEN response is 302 to model changelist; exactly X/Y no longer exist
  AND exactly two DELETION LogEntry rows identify X/Y and admin_staff
  AND assert_unchanged(before); other model and session identity are unchanged
  AND no file operation or unrelated cascade occurs
```

<a id="misc-t26e"></a>

### MISC-T26e — test_repeated_stale_delete_is_non_mutating

Parent: `MISC-T26` | Operation: `MISC-O11` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; X was explicitly deleted and its deletion log is recorded
  AND untouched second row Z; before=snapshot_scope([Z])
WHEN POSTing stale X delete URL {post:"yes"} and then repeating it
THEN both responses are 302 to admin index with object-does-not-exist warning
  AND no additional DELETION LogEntry or replacement object is created
  AND assert_unchanged(before); no file/session-identity changes occur
```

<a id="misc-t26f"></a>

### MISC-T26f — test_last_setting_delete_requires_product_visibility_choice

Parent: `MISC-T26` | Operation: `MISC-O11` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q2 absent-setting fallback; Q9 delete/deactivate policy
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff and sole S={is_active:False,name:"Disabled"}
  AND at_time(2026-01-01T12:00:00Z)
WHEN staff confirms S deletion then eligible reader loads /auth/dashboard/
THEN admin delete itself removes S and creates its DELETION LogEntry
  AND Q2/Q9 must choose visible computed default, disabled empty state or forbid last deletion
  AND no chosen behavior may silently recreate a saved setting on read
  AND announcements, unrelated users and reader identity remain unchanged
```

<a id="misc-t27a"></a>

### MISC-T27a — test_admin_save_log_failure_rolls_back_model_write

Parent: `MISC-T27` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN TransactionTestCase, admin_staff, existing A/S and untouched second row
  AND before=snapshot_scope(existing target and second row)
  AND deliberate RuntimeError injected in log_addition or log_change after real model save
WHEN posting model add/edit {title:"New",content:"Text",_save:"1"} or {name:"New",_save:"1"}
THEN test client raises injected RuntimeError within stock changeform atomic block
  AND inserted object is absent or existing target restored to original fields
  AND assert_unchanged(before); no partial ADDITION/CHANGE LogEntry survives
  AND independent fresh query on selected database alias confirms rollback
```

<a id="misc-t27b"></a>

### MISC-T27b — test_admin_model_save_failure_creates_no_audit_entry

Parent: `MISC-T27` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN TransactionTestCase, admin_staff, target A/S and untouched second row
  AND before=snapshot_scope(target and second row)
  AND deliberate RuntimeError at ModelAdmin.save_model before persistence
WHEN posting model add/edit {title:"New",content:"Text",_save:"1"} or {name:"New",_save:"1"}
THEN test client raises injected RuntimeError and no insert/edit is committed
  AND assert_unchanged(before); no ADDITION/CHANGE LogEntry survives
  AND fresh database state contains no fallback/default records or file effects
```

<a id="misc-t27c"></a>

### MISC-T27c — test_detail_delete_failure_rolls_back_preceding_delete_log

Parent: `MISC-T27` | Operation: `MISC-O11` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN TransactionTestCase, admin_staff, target A/S and untouched second row
  AND before=snapshot_scope(target and second row)
  AND RuntimeError injected in delete_model after standard log_deletions
  AND separately inject before real delete and after real delete returns
WHEN posting target delete URL {post:"yes"}
THEN test client raises injected RuntimeError within stock delete-view atomic block
  AND target and other row remain unchanged in fresh queries
  AND assert_unchanged(before); no DELETION LogEntry survives
  AND no file callback or unrelated state mutation occurs
```

<a id="misc-t27d"></a>

### MISC-T27d — test_bulk_delete_failure_audit_contract_needs_decision

Parent: `MISC-T27` | Operation: `MISC-O11` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q11 audit/transaction failure semantics; possible false-success logs
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN TransactionTestCase and admin_staff; selected X/Y, unselected Z
  AND before=snapshot_scope([X,Y,Z]); inject RuntimeError in delete_queryset after log_deletions
WHEN posting changelist {action:"delete_selected",_selected_action:[X.pk,Y.pk],post:"yes"}
THEN Q11 must choose atomic row+success-log rollback or explicit failed-attempt event semantics
  AND unselected Z and session identity must remain unchanged
  AND stock action has no enclosing view atomic block; surviving logs are not proof of deletion
  AND future success-only DELETION entries must not falsely claim deleted rows
  AND no compensation/file-transaction guarantee may be invented
```

<a id="misc-t28a"></a>

### MISC-T28a — test_stale_admin_write_requires_conflict_policy

Parent: `MISC-T28` | Operation: `MISC-O10` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q10 stale-write conflict semantics
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN synthetic staff A/B each has model view/change permissions
  AND both load S={name:"Initial",is_active:True}; unrelated T={name:"Keep",is_active:True}
WHEN A POSTs S change {name:"First",is_active:"on",_save:"1"}
  AND B then POSTs stale form {name:"Second",is_active:"on",_save:"1"}
THEN current sequential behavior ends with name Second and two CHANGE LogEntry rows
  AND Q10 must choose last-writer-wins or version conflict response for future contract
  AND S PK, T fields, announcement rows and both session identities stay unchanged
```

<a id="misc-t28b"></a>

### MISC-T28b — test_concurrent_admin_write_requires_policy_and_postgresql

Parent: `MISC-T28` | Operation: `MISC-O10` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q10 winner/conflict rule; Q11 audit; case-specific PostgreSQL/barriers
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN staff A/B with view/change and PostgreSQL independent connections with bounded barriers
  AND S={name:"Initial",is_active:True}; unrelated T={name:"Keep",is_active:True}
WHEN A/B concurrently POST S change with names First and Second and _save="1"
THEN Q10 must select acceptable winner or explicit conflict/retry behavior
  AND no outcome may corrupt PKs, alter T or associate a log with the wrong actor
  AND SQLite sequential requests do not establish these guarantees
  AND chosen model+audit atomicity follows Q11, not an invented locking guarantee
```

<a id="misc-t29a"></a>

### MISC-T29a — test_admin_history_is_scoped_to_object_and_actor

Parent: `MISC-T29` | Operation: `MISC-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff creates/edits target X and staff B creates unrelated target Y
  AND actor viewer has model view permission only; before=snapshot_scope([X,Y])
WHEN viewer GETs X history URL
THEN response is 200; action_list contains only X content type/object_id entries
  AND entries name admin_staff, exact ADDITION/CHANGE actions and aware action times
  AND Y actor/action entries do not appear in X history
  AND assert_unchanged(before); history reads create no LogEntry or identity change
```

<a id="misc-t29b"></a>

### MISC-T29b — test_admin_history_denies_staff_without_view_or_change

Parent: `MISC-T29` | Operation: `MISC-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="no-history",is_staff=True) with only model add permission
  AND target X with one prior LogEntry; before=snapshot_scope([X])
WHEN actor GETs X history URL
THEN response is 403 and history content is not disclosed
  AND prior LogEntry rows remain unchanged and no new entry is added
  AND assert_unchanged(before); session identity remains no-history
```

<a id="misc-t29c"></a>

### MISC-T29c — test_orm_and_reader_actions_do_not_create_admin_logs

Parent: `MISC-T29` | Operation: `MISC-O07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN A={title:"Initial",content:"Text"}; S={name:"Clock",is_active:True}
  AND logged-in make_user(username="reader",roles=()); at_time(2026-01-01T12:00:00Z)
  AND current LogEntry PK set is recorded
WHEN ORM saves A.content="Changed" and reader GETs /auth/dashboard/ twice
THEN both responses are 200; A content is Changed only because of explicit ORM save
  AND LogEntry PK set is unchanged; S and reader/profile roles are unchanged
  AND reads do not alter announcement updated_at beyond its explicit save
```

<a id="misc-t29d"></a>

### MISC-T29d — test_business_audit_retention_requires_shared_policy

Parent: `MISC-T29` | Operation: `MISC-O09` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q11 cumulative business audit/retention
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN current MISC has stock admin LogEntry but no custom business audit model
  AND synthetic add/edit/delete events for A and S can be described by actor/object/time
WHEN specifying cumulative migration audit and its retention/error behavior
THEN Q11 must choose event schema, retention, failed-attempt recording and access rules
  AND existing LogEntry does not establish coverage of direct ORM or reader events
  AND chosen records must not contain secrets/private fixture content
  AND this design introduces no audit model or new writes
```
