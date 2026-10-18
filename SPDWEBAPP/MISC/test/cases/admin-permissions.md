# Admin capability and action permissions

Use business mode from [shared fixtures](../../../../docs/testing/fixture-contract.md).
`A` denotes AnnouncementAlert; `S` denotes DayLightSavingsAlert.
For each parameterized model use its own existing target and untouched second row.
Reverse `admin:MISC_announcementalert_{changelist,add,change,delete,history}` or
`admin:MISC_daylightsavingsalert_{changelist,add,change,delete,history}` with target PK.
Grant actual permissions via ORM; fresh clients/users avoid permission-cache leakage.
No chapter role grants a Django admin permission.

<a id="misc-t21a"></a>

### MISC-T21a — test_anonymous_nonstaff_and_inactive_staff_cannot_enter_admin

Parent: `MISC-T21` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN actors separately anonymous, make_user(username="member",roles=("PRESIDENT",)),
  AND make_user(username="inactive-staff",is_staff=True,is_active=False)
  AND A={title:"Keep",content:"Text"}, S={name:"Keep",is_active:True}
  AND before=snapshot_scope([A,S]); all admin LogEntry rows are recorded
WHEN each actor GETs each model's changelist, add, change and delete URLs
THEN response is 302 to the reversed admin login with next equal requested path
  AND no target fields or admin content are disclosed in the redirect body
  AND assert_unchanged(before); no LogEntry or authenticated identity is created
```

<a id="misc-t21b"></a>

### MISC-T21b — test_staff_without_view_or_change_cannot_list_models

Parent: `MISC-T21` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="staff",is_staff=True,roles=()) with no permissions
  AND A={title:"Keep",content:"Text"}; S={name:"Keep",is_active:True}
  AND before=snapshot_scope([A,S])
WHEN staff GETs either model's changelist and existing change URL
THEN each response is 403
  AND assert_unchanged(before); no LogEntry is created
  AND session identity remains staff; chapter-role absence is not the permission check
```

<a id="misc-t21c"></a>

### MISC-T21c — test_view_permission_allows_read_without_writes

Parent: `MISC-T21` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="viewer",is_staff=True) granted only MISC.view_announcementalert
  AND A={title:"View me",content:"Text"}; B={title:"Other",content:"Keep"}
  AND before=snapshot_scope([A,B])
WHEN viewer GETs announcement changelist and A change URL
THEN both responses are 200; A detail is readonly with no save/add/delete capability
  AND viewer GETs DST changelist receives 403
  AND assert_unchanged(before); no LogEntry is created; identity remains viewer
```

<a id="misc-t21d"></a>

### MISC-T21d — test_add_permission_is_required_for_direct_add_post

Parent: `MISC-T21` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="no-add",is_staff=True) granted only model view permission
  AND model separately AnnouncementAlert and DayLightSavingsAlert
  AND A={title:"Keep",content:"Text"}; S={name:"Keep",is_active:True}
  AND before=snapshot_scope([A,S])
WHEN actor GETs add URL then POSTs {title:"New",content:"Text",_save:"1"} for announcement
  AND separately POSTs {name:"New",is_active:"on",_save:"1"} for DST
THEN all add responses are 403 and neither model count changes
  AND assert_unchanged(before); no LogEntry is created; session identity stays no-add
```

<a id="misc-t21e"></a>

### MISC-T21e — test_change_permission_is_required_for_direct_edit_post

Parent: `MISC-T21` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="no-change",is_staff=True) has only model view and add permissions
  AND parameterized A={title:"Keep",content:"Text"} or S={name:"Keep",is_active:True}
  AND before=snapshot_scope([A,S])
WHEN actor POSTs A change URL with {title:"Changed",content:"Changed",_save:"1"}
  AND separately S change URL with {name:"Changed",_save:"1"}
THEN each response is 403; adding a record does not grant edit capability
  AND assert_unchanged(before); no LogEntry or session-identity change occurs
```

<a id="misc-t21f"></a>

### MISC-T21f — test_delete_permission_is_required_for_detail_delete

Parent: `MISC-T21` | Operation: `MISC-O11` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="no-delete",is_staff=True) with model view/add/change but no delete
  AND A={title:"Keep",content:"Text"}; S={name:"Keep",is_active:True}
  AND before=snapshot_scope([A,S])
WHEN actor GETs each target delete URL then POSTs {post:"yes"} to each
THEN every response is 403; target rows remain present
  AND assert_unchanged(before); no deletion LogEntry is written
  AND session identity stays no-delete
```

<a id="misc-t21g"></a>

### MISC-T21g — test_hidden_bulk_delete_cannot_bypass_delete_permission

Parent: `MISC-T21` | Operation: `MISC-O11` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN staff no-delete with only view/change permission for each parameterized model
  AND existing target A or S and another unchanged row of that model
  AND before=snapshot_scope(target and other row)
WHEN actor POSTs changelist {action:"delete_selected",_selected_action:[target.pk],post:"yes"}
THEN response is 200 changelist because delete_selected is excluded from permitted actions
  AND no delete confirmation or success message is generated
  AND assert_unchanged(before); target and other row remain; no LogEntry is added
  AND session identity stays no-delete
```

<a id="misc-t21h"></a>

### MISC-T21h — test_permissions_are_isolated_by_model

Parent: `MISC-T21` | Operation: `MISC-O10` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="a-manager",is_staff=True) with all four announcement permissions only
  AND make_user(username="s-manager",is_staff=True) with all four DST permissions only
  AND A={title:"Keep",content:"Text"}; S={name:"Keep",is_active:True}
  AND before=snapshot_scope([A,S])
WHEN each actor GETs the other model's list/add/change/delete/history URLs
THEN every response is 403
  AND crafted other-model add/change/delete POSTs are also 403
  AND assert_unchanged(before); no LogEntry is added; actor identities remain unchanged
```

<a id="misc-t21i"></a>

### MISC-T21i — test_chapter_role_and_record_creator_do_not_restrict_admin_read

Parent: `MISC-T21` | Operation: `MISC-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="editor",roles=(),is_staff=True) with model view/change permissions
  AND A and B were created by two other synthetic staff via admin
  AND each row has a corresponding LogEntry creator but no owner field
  AND before=snapshot_scope([A,B])
WHEN editor GETs announcement list and A/B change URLs
THEN every response is 200 and both records are available to editor
  AND assert_unchanged(before); creator LogEntry rows and session identity are unchanged
```

<a id="misc-t21j"></a>

### MISC-T21j — test_delete_only_permission_does_not_grant_changelist

Parent: `MISC-T21` | Operation: `MISC-O11` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="deleter",is_staff=True) with only per-model delete permission
  AND target A or S plus untouched second row; before=snapshot_scope(those rows)
WHEN deleter GETs target delete URL and model changelist separately
THEN delete confirmation is 200 but changelist is 403 without view/change
  AND no record is deleted by either GET
  AND assert_unchanged(before); no deletion LogEntry is added
```

<a id="misc-t21k"></a>

### MISC-T21k — test_synthetic_superuser_can_read_both_models

Parent: `MISC-T21` | Operation: `MISC-O09` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="root-test",is_staff=True,is_superuser=True,roles=())
  AND A={title:"Notice",content:"Text"}; S={name:"Clock",is_active:True}
  AND before=snapshot_scope([A,S])
WHEN root-test GETs each model's list/add/change/delete/history URLs
THEN every existing-target/read/form response is 200
  AND assert_unchanged(before); no LogEntry is added by reads
  AND this smoke does not replace narrow-permission cases
```

<a id="misc-t21l"></a>

### MISC-T21l — test_admin_does_not_require_member_profile

Parent: `MISC-T21` | Operation: `MISC-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/admin.py:4–12`

```text
GIVEN make_user(username="profileless-staff",is_staff=True,with_profile=False)
  AND only MISC.view_announcementalert and MISC.change_announcementalert are granted
  AND A={title:"Before",content:"Text"}; B={title:"Other",content:"Keep"}
  AND before=snapshot_scope([A,B])
WHEN actor GETs A change URL then POSTs {title:"After",content:"Text",_save:"1"}
THEN GET is 200 and POST is 302; only A title/updated_at and one CHANGE log change
  AND actor still has no Brother_Profile; no implicit roles are created
  AND assert_unchanged(before,except_fields={A:{title,updated_at}})
```
