# Admin forms, writes and malformed requests

Use business mode and [shared fixtures](../../../../docs/testing/fixture-contract.md).
Reverse model admin names; never assume the configured admin prefix.
`admin_staff` is make_user(username="admin-staff",is_staff=True,roles=()) with
view/add/change/delete permissions explicitly granted for the model under test.
Every write compares a second row, actor profile roles and unrelated model rows.
Admin success messages may change message transport, never session identity.

<a id="misc-t22a"></a>

### MISC-T22a — test_announcement_admin_exposes_only_title_and_content

Parent: `MISC-T22` | Operation: `MISC-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; A={title:"Notice",content:"Text",is_active:False}
  AND before=snapshot_scope([A])
WHEN actor GETs announcement add/change/changelist URLs
THEN forms expose only title/content as editable model fields
  AND is_active, PK, created_at and updated_at are absent as editable fields
  AND changelist has title and created_at columns
  AND assert_unchanged(before); no LogEntry is added
```

<a id="misc-t22b"></a>

### MISC-T22b — test_announcement_admin_add_sets_defaults_and_add_log

Parent: `MISC-T22` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; B={title:"Other",content:"Keep",is_active:False}
  AND before=snapshot_scope([B]); at_time(2026-01-02T12:00:00Z) includes model/log clocks
WHEN actor POSTs announcement add URL {title:"Notice",content:"Room 4",_save:"1"}
THEN response is 302 to announcement changelist
  AND exactly one new A has Notice, Room 4, is_active=True and both timestamps at frozen time
  AND exactly one ADDITION LogEntry names A PK/content type and admin_staff
  AND assert_unchanged(before); session identity and other model rows are unchanged
```

<a id="misc-t22c"></a>

### MISC-T22c — test_announcement_admin_edit_preserves_inactive_flag

Parent: `MISC-T22` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; inactive A={title:"Notice",content:"Room 4"} created 2026-01-01T12:00:00Z
  AND inactive B={title:"Other",content:"Keep"}; before=snapshot_scope([A,B])
WHEN at_time(2026-01-02T12:00:00Z) actor POSTs A change URL
  AND payload is {title:"Revised",content:"Room 5",_save:"1"}
THEN response is 302 to announcement changelist; fresh A remains inactive
  AND A title/content/updated_at change; created_at and PK remain unchanged
  AND one CHANGE LogEntry belongs to A/admin_staff with changed field names
  AND assert_unchanged(before,except_fields={A:{title,content,updated_at}})
```

<a id="misc-t22d"></a>

### MISC-T22d — test_announcement_admin_ignores_excluded_field_payloads

Parent: `MISC-T22` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; A has is_active separately False and True, created 2026-01-01T12:00:00Z
  AND B={title:"Other",content:"Keep"}; before=snapshot_scope([A,B])
WHEN at_time(2026-01-02T12:00:00Z) actor POSTs A change URL
  AND payload={title:"Revised",content:"Room 5",is_active:"0",id:B.pk,
  AND created_at:"1990-01-01T00:00:00Z",updated_at:"1990-01-01T00:00:00Z",_save:"1"}
THEN response is 302; A retains original active flag/created_at/PK
  AND updated_at uses frozen model clock, not supplied value
  AND only A title/content/updated_at plus one CHANGE LogEntry change
  AND assert_unchanged(before,except_fields={A:{title,content,updated_at}})
```

<a id="misc-t22e"></a>

### MISC-T22e — test_save_continue_and_addanother_have_concrete_redirects

Parent: `MISC-T22` | Operation: `MISC-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff and fresh A={title:"Notice",content:"Text"} for each variant
  AND B={title:"Other",content:"Keep"}; before=snapshot_scope([A,B])
WHEN actor POSTs A change URL with title="Revised",content="Room 5"
  AND flag separately {_save:"1"}, {_continue:"1"}, {_addanother:"1"}
THEN response is 302 to changelist, A change URL, add URL respectively
  AND exactly A is updated, no additional announcement is created
  AND one CHANGE LogEntry identifies A and actor
  AND assert_unchanged(before,except_fields={A:{title,content,updated_at}})
```

<a id="misc-t22f"></a>

### MISC-T22f — test_saveasnew_requires_add_permission_even_when_button_hidden

Parent: `MISC-T22` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN staff actor with announcement view/change but no add permission
  AND A={title:"Original",content:"Text"}; before=snapshot_scope([A])
WHEN actor POSTs A change URL {title:"Clone",content:"New",_saveasnew:"1"}
THEN response is 403 because Django interprets this as an add action
  AND A and announcement count are unchanged
  AND assert_unchanged(before); no addition/change LogEntry is written
  AND button visibility alone is not the authorization rule
```

<a id="misc-t22g"></a>

### MISC-T22g — test_authorized_saveasnew_creates_separate_announcement

Parent: `MISC-T22` | Operation: `MISC-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; inactive A={title:"Original",content:"Text"}
  AND before=snapshot_scope([A]); at_time(2026-01-02T12:00:00Z)
WHEN actor POSTs A change URL {title:"Clone",content:"New",_saveasnew:"1"}
THEN response is 302 to new object's change URL
  AND exactly one new active B has title Clone, content New and new timestamps/PK
  AND assert_unchanged(before); A remains inactive with Original/Text
  AND one ADDITION LogEntry names B rather than A; hidden button does not disable POST
```

<a id="misc-t22h"></a>

### MISC-T22h — test_announcement_activation_ui_needs_product_decision

Parent: `MISC-T22` | Operation: `MISC-O09` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q9 announcement activation/deactivation UI
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN inactive A={title:"Hidden",content:"Text"} and admin_staff
WHEN specifying an admin action to activate or deactivate A
THEN Q9 must choose add is_active field, explicit action or retain trusted-ORM-only control
  AND current title/content-only form cannot change active state
  AND until implemented no new activation URL or payload contract is invented
  AND unrelated announcements, timestamps and actor session identity must stay unchanged
```

<a id="misc-t22i"></a>

### MISC-T22i — test_add_only_staff_can_create_without_list_permission

Parent: `MISC-T22` | Operation: `MISC-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="adder",is_staff=True) with only MISC.add_announcementalert
  AND B={title:"Other",content:"Keep"}; before=snapshot_scope([B])
WHEN adder GETs announcement add URL then POSTs {title:"Added",content:"Text",_save:"1"}
THEN GET is 200 and POST is 302 to reversed admin index without list permission
  AND exactly one active announcement Added/Text and one ADDITION LogEntry are created
  AND subsequent changelist GET is 403
  AND assert_unchanged(before); session identity remains adder
```

<a id="misc-t23a"></a>

### MISC-T23a — test_dst_admin_form_and_list_expose_name_and_active

Parent: `MISC-T23` | Operation: `MISC-O10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff and S={is_active:False,name:"Clock"}; before=snapshot_scope([S])
WHEN actor GETs DST add/change/changelist URLs
THEN editable model fields are exactly is_active and name
  AND changelist columns include is_active and name
  AND no owner, timestamp or invented setting field is editable
  AND assert_unchanged(before); no LogEntry is added
```

<a id="misc-t23b"></a>

### MISC-T23b — test_dst_admin_add_records_active_name_and_log

Parent: `MISC-T23` | Operation: `MISC-O10` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff and T={is_active:False,name:"Other"}; before=snapshot_scope([T])
WHEN actor POSTs DST add URL {name:"Clock",is_active:"on",_save:"1"}
THEN response is 302 to DST changelist
  AND exactly one new S has is_active=True and name="Clock"
  AND one ADDITION LogEntry identifies S, DST content type and admin_staff
  AND assert_unchanged(before); session identity and announcement rows are unchanged
```

<a id="misc-t23c"></a>

### MISC-T23c — test_dst_admin_edit_omitted_checkbox_disables_setting

Parent: `MISC-T23` | Operation: `MISC-O10` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; S={name:"Before",is_active:True}; T={name:"Other",is_active:True}
  AND before=snapshot_scope([S,T])
WHEN actor POSTs S change URL {name:"After",_save:"1"} without is_active
THEN response is 302 to DST changelist; fresh S has name After and is_active=False
  AND one CHANGE LogEntry names S/admin_staff and changed fields
  AND assert_unchanged(before,except_fields={S:{name,is_active}})
  AND setting count and session identity remain unchanged
```

<a id="misc-t23d"></a>

### MISC-T23d — test_dst_admin_name_normalization_accepts_blank_values

Parent: `MISC-T23` | Operation: `MISC-O10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff and fresh S={name:"Before",is_active:True} for each variant
  AND T={name:"Other",is_active:False}; before=snapshot_scope([S,T])
WHEN actor POSTs S change URL with is_active="on",_save="1" and name separately
  AND omitted, "", "   ", "  Clock  "
THEN response is 302; fresh name is None, None, None, "Clock" respectively
  AND active remains True; only S.name plus CHANGE LogEntry may change
  AND assert_unchanged(before,except_fields={S:{name}}); count is unchanged
```

<a id="misc-t23e"></a>

### MISC-T23e — test_repeated_dst_edit_does_not_insert_duplicate

Parent: `MISC-T23` | Operation: `MISC-O10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; S={name:"Before",is_active:True}; T={name:"Other",is_active:False}
  AND before=snapshot_scope([S,T])
WHEN actor twice POSTs S change URL {name:"After",is_active:"on",_save:"1"}
THEN both responses are 302; exactly original S and T remain
  AND S.name="After" with same PK and is_active=True
  AND two CHANGE LogEntry records refer to S, not new settings
  AND assert_unchanged(before,except_fields={S:{name}}); session identity is unchanged
```

<a id="misc-t23f"></a>

### MISC-T23f — test_dst_admin_save_flags_and_saveasnew_action

Parent: `MISC-T23` | Operation: `MISC-O10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff and fresh S={name:"Before",is_active:False} per variant
  AND before=snapshot_scope([S])
WHEN POSTing S change URL {name:"Clock",is_active:"on"} with flag separately
  AND {_save:"1"}, {_continue:"1"}, {_addanother:"1"}, {_saveasnew:"1"}
THEN redirects are DST list, S change, DST add, new setting change respectively
  AND first three update only S and create one CHANGE LogEntry
  AND saveasnew inserts one active Clock setting and ADDITION LogEntry, leaving S unchanged
  AND no announcement or session-identity change occurs
```

<a id="misc-t24a"></a>

### MISC-T24a — test_admin_invalid_fields_return_errors_without_writes

Parent: `MISC-T24` | Operation: `MISC-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff and B={title:"Other",content:"Keep"}, T={name:"Other",is_active:False}
  AND before=snapshot_scope([B,T])
WHEN POSTing announcement add/change with title/content separately
  AND ("","Text"), ("Notice",""), ("x" repeated 256,"Text")
  AND separately DST add/change with {name:"x" repeated 256,is_active:"on"}
THEN each response is 200 with required/max-length error on exact offending field
  AND no target field, row count or LogEntry changes
  AND assert_unchanged(before); session identity remains admin_staff
```

<a id="misc-t24b"></a>

### MISC-T24b — test_missing_and_malformed_admin_object_ids_do_not_mutate

Parent: `MISC-T24` | Operation: `MISC-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff; A={title:"Keep",content:"Text"}; S={name:"Keep",is_active:True}
  AND before=snapshot_scope([A,S]); missing IDs separately "999999" and "not-an-integer"
WHEN GET/POST change and delete URLs use each missing ID with model's concrete payload
  AND announcement payload={title:"No replacement",content:"Text",_save:"1"}
  AND DST payload={name:"No replacement",is_active:"on",_save:"1"}; delete={post:"yes"}
THEN each response is 302 to admin index with object-does-not-exist warning
  AND no replacement object or LogEntry is created
  AND assert_unchanged(before); session identity remains admin_staff
```

<a id="misc-t24c"></a>

### MISC-T24c — test_unknown_or_empty_bulk_action_has_no_state_effect

Parent: `MISC-T24` | Operation: `MISC-O11` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff with both models' permissions; target A or S and untouched second row
  AND before=snapshot_scope(target and second row)
WHEN POSTing model changelist separately with
  AND {action:"unknown_action",index:"0",_selected_action:[target.pk]}
  AND {action:"delete_selected",index:"0"} without selection
THEN each response is 302 back to changelist with action/selection warning
  AND no rows or LogEntry change; assert_unchanged(before)
  AND session identity remains admin_staff
```

<a id="misc-t22j"></a>

### MISC-T22j — test_announcement_add_flags_redirect_without_extra_inserts

Parent: `MISC-T22` | Operation: `MISC-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff, B={title:"Other",content:"Keep"}; before=snapshot_scope([B])
WHEN POSTing add URL {title:"Notice",content:"Text"} separately with
  AND {_save:"1"}, {_continue:"1"}, {_addanother:"1"} in independent fixtures
THEN redirects are announcement list, new A change URL, announcement add URL respectively
  AND each request inserts exactly one active Notice/Text row and one ADDITION LogEntry
  AND no second row is inserted by redirect construction
  AND assert_unchanged(before); session identity remains admin_staff
```

<a id="misc-t23g"></a>

### MISC-T23g — test_dst_add_flags_redirect_without_extra_inserts

Parent: `MISC-T23` | Operation: `MISC-O10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN admin_staff, T={name:"Other",is_active:False}; before=snapshot_scope([T])
WHEN POSTing DST add URL {name:"Clock",is_active:"on"} separately with
  AND {_save:"1"}, {_continue:"1"}, {_addanother:"1"} in independent fixtures
THEN redirects are DST list, new S change URL, DST add URL respectively
  AND each request inserts exactly one active Clock row and one ADDITION LogEntry
  AND no second setting is inserted by redirect construction
  AND assert_unchanged(before); announcement rows and session identity remain unchanged
```
