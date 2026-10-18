# Alert settings, tag selection and controls

Use [shared fixtures](../../../../docs/testing/fixture-contract.md), business settings,
and real setting rows. `at_time` must patch `MISC.utils.datetime.now(tz)`.

<a id="misc-t05a"></a>

### MISC-T05a — test_dst_model_default_optional_name_and_string

Parent: `MISC-T05` | Operation: `MISC-O08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/models.py:4–13`

```text
GIVEN B={name:"Other", is_active:False}; before=snapshot_scope([B])
WHEN creating A separately with name omitted, name=None, name="", name="x" repeated 255
THEN each fresh A has is_active=True and str(A)="DLS Alert - Active: True"
  AND omitted name becomes None; explicit None, empty and 255-char values persist
  AND exactly one row per independent variant is inserted
  AND assert_unchanged(before); no admin LogEntry is added
```

<a id="misc-t05b"></a>

### MISC-T05b — test_dst_model_update_keeps_other_settings

Parent: `MISC-T05` | Operation: `MISC-O08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/models.py:4–13`

```text
GIVEN A={name:"Before", is_active:True}; B={name:"Other", is_active:True}
  AND before=snapshot_scope([A,B])
WHEN A.name="After" and A.is_active=False are saved through ORM
THEN fresh A fields are After and False; str(A)="DLS Alert - Active: False"
  AND assert_unchanged(before, except_fields={A:{name,is_active}})
  AND setting count remains two; no admin LogEntry is added
```

<a id="misc-t05c"></a>

### MISC-T05c — test_dst_model_full_clean_rejects_long_name

Parent: `MISC-T05` | Operation: `MISC-O08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/models.py:4–6`

```text
GIVEN unsaved A with name="x" repeated 256 and is_active=True
  AND existing B={name:"Other", is_active:False}; before=snapshot_scope([B])
WHEN A.full_clean() runs
THEN ValidationError identifies name and A remains unsaved
  AND assert_unchanged(before); setting count remains one
  AND no admin LogEntry is added
```

<a id="misc-t06a"></a>

### MISC-T06a — test_tag_without_setting_shows_spring_message

Parent: `MISC-T06` | Operation: `MISC-O02` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templatetags/dls_tags.py:8–36`

```text
GIVEN no DayLightSavingsAlert rows and at_time(2026-01-01T12:00:00Z)
WHEN calling dls_alert() using real utility
THEN show_alert=True and next_change is aware with Chicago calendar date 2026-03-08
  AND message is "Next Daylight Saving Time: March 08, 2026. Clocks will move forward one hour!"
  AND no setting, announcement or admin LogEntry is created
```

<a id="misc-t06b"></a>

### MISC-T06b — test_tag_without_setting_shows_fall_message

Parent: `MISC-T06` | Operation: `MISC-O02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templatetags/dls_tags.py:8–36`

```text
GIVEN no DayLightSavingsAlert rows and at_time(2026-04-01T12:00:00Z)
WHEN calling dls_alert() using real utility
THEN show_alert=True and next_change has Chicago calendar date 2026-11-01
  AND message is "Next Daylight Saving Time: November 01, 2026. Clocks will move back one hour!"
  AND this case asserts date/wording, not physical fall UTC instant
  AND no setting, announcement or admin LogEntry is created
```

<a id="misc-t06c"></a>

### MISC-T06c — test_blank_override_preserves_computed_message

Parent: `MISC-T06` | Operation: `MISC-O02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templatetags/dls_tags.py:8–36`

```text
GIVEN one active setting S with name separately None and ""
  AND at_time(2026-01-01T12:00:00Z); before=snapshot_scope([S])
WHEN calling dls_alert()
THEN show_alert=True and message starts "Next Daylight Saving Time: March 08, 2026."
  AND next_change is non-null and aware
  AND assert_unchanged(before); no default row or admin LogEntry is created
```

<a id="misc-t07a"></a>

### MISC-T07a — test_active_override_replaces_message_and_newlines

Parent: `MISC-T07` | Operation: `MISC-O02` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templatetags/dls_tags.py:8–36`

```text
GIVEN S={is_active:True,name:"line1\nline2"} and at_time(2026-01-01T12:00:00Z)
  AND before=snapshot_scope([S])
WHEN calling dls_alert() and rendering its inclusion fragment
THEN context message is "line1<br>line2" and show_alert=True
  AND fragment text shows both lines separated by a br element
  AND next_change remains computed and aware; clockButton is present once
  AND assert_unchanged(before); no announcement or admin LogEntry changes
```

<a id="misc-t07b"></a>

### MISC-T07b — test_inactive_setting_hides_dst_fragment

Parent: `MISC-T07` | Operation: `MISC-O05` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templates/MISC/dls_alert.html:3–42`

```text
GIVEN S={is_active:False,name:"Hidden message"}; at_time(2026-01-01T12:00:00Z)
  AND before=snapshot_scope([S])
WHEN calling dls_alert() and rendering its inclusion fragment twice
THEN context show_alert=False; fragment has no clockButton, overlay or alert popup
  AND no toggleAlert script, clock image or Hidden message renders
  AND assert_unchanged(before); read calls never reactivate S or add logs
```

<a id="misc-t07c"></a>

### MISC-T07c — test_explicit_reactivation_appears_on_next_read

Parent: `MISC-T07` | Operation: `MISC-O02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templatetags/dls_tags.py:8–36`

```text
GIVEN S={is_active:False,name:"Return"} and at_time(2026-01-01T12:00:00Z)
  AND initial dls_alert().show_alert=False
  AND ORM fixture save sets S.is_active=True; before=snapshot_scope([S])
WHEN calling dls_alert() and rendering its inclusion fragment
THEN show_alert=True; Return and clockButton render
  AND assert_unchanged(before); no read-side update or admin LogEntry is created
```

<a id="misc-t08a"></a>

### MISC-T08a — test_multi_setting_selection_needs_singleton_policy

Parent: `MISC-T08` | Operation: `MISC-O02` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q2 multiple-setting precedence
Source: `SPDWEBAPP/MISC/templatetags/dls_tags.py:8–36`

```text
GIVEN A={pk:10,is_active:False,name:"Zebra"}; B={pk:20,is_active:True,name:"Apple"}
  AND at_time(2026-01-01T12:00:00Z); before=snapshot_scope([A,B])
WHEN dls_alert() is called, B.name is explicitly changed to "Edited", and tag is called again
THEN current first-PK selection keeps A hidden with message Zebra on both reads
  AND Q2 must choose first-PK precedence or singleton enforcement for acceptance
  AND no read repairs multiplicity; only explicit B.name fixture write is allowed
  AND A, row count and admin logs remain unchanged
```

<a id="misc-t08b"></a>

### MISC-T08b — test_setting_delete_fallback_needs_visibility_policy

Parent: `MISC-T08` | Operation: `MISC-O02` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q2 last-setting/default visibility
Source: `SPDWEBAPP/MISC/templatetags/dls_tags.py:8–36`

```text
GIVEN A={pk:10,is_active:False,name:"First"}; B={pk:20,is_active:True,name:"Second"}
  AND at_time(2026-01-01T12:00:00Z)
WHEN ORM fixture deletes A, reads tag, deletes B, then reads tag again
THEN current code selects Second after A removal and computed visible default after B removal
  AND Q2 must choose preserve this fallback or retain disabled state with no setting
  AND only the two explicit deletes change records; reads add no rows or admin logs
```

<a id="misc-t10a"></a>

### MISC-T10a — test_override_content_cannot_create_executable_markup

Parent: `MISC-T10` | Operation: `MISC-O05` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D1 raw override HTML; Q3 presentation tracked separately
Source: `SPDWEBAPP/MISC/templates/MISC/dls_alert.html:13`

```text
GIVEN active S.name='<img src=x onerror=alert(1)><script>alert(2)</script>'
  AND before=snapshot_scope([S]); at_time(2026-01-01T12:00:00Z)
WHEN rendering the dls_alert inclusion fragment
THEN content must not create script or event-handler-bearing elements
  AND current message|safe violates this concrete safety invariant (D1)
  AND assert_unchanged(before); no files/session identity/admin logs change
  AND this case does not decide presentation of harmless rich text
```

<a id="misc-t10b"></a>

### MISC-T10b — test_override_harmless_markup_needs_presentation_policy

Parent: `MISC-T10` | Operation: `MISC-O05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q3 plain text versus sanitized rich text; D1
Source: `SPDWEBAPP/MISC/templates/MISC/dls_alert.html:13`

```text
GIVEN S={is_active:True,name:"<b>Meeting</b>\nRoom 4"}
  AND before=snapshot_scope([S]); at_time(2026-01-01T12:00:00Z)
WHEN rendering the dls_alert inclusion fragment
THEN Q3 must choose escaped literal text or allowlisted sanitized bold markup
  AND both candidate outcomes preserve inert content and intended line separation
  AND assert_unchanged(before); no executable markup is acceptable
```

<a id="misc-t11a"></a>

### MISC-T11a — test_fragment_controls_have_local_targets

Parent: `MISC-T11` | Operation: `MISC-O05` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templates/MISC/dls_alert.html:4–40`

```text
GIVEN active S={name:"Clock",is_active:True} and announcement A={title:"Notice",content:"Text"}
  AND before=snapshot_scope([S,A]); at_time(2026-01-01T12:00:00Z)
WHEN rendering each MISC fragment once
THEN DST fragment has exactly one clockButton, alert, overlay and toggleAlert definition
  AND open/close controls invoke toggleAlert and target those IDs
  AND announcement close onclick finds its containing table and sets display none
  AND neither control contains a mutation form or write endpoint
  AND assert_unchanged(before); no admin LogEntry or session identity change
```

<a id="misc-t11b"></a>

### MISC-T11b — test_browser_dismissal_has_no_persistent_effect

Parent: `MISC-T11` | Operation: `MISC-O05` | Priority: P2
Status: `INFRA_BLOCKED` | Blockers: shared browser with network/cookie capture
Source: `SPDWEBAPP/MISC/templates/MISC/dls_alert.html:19–40`

```text
GIVEN browser facility with network capture, logged-in make_user(username="browser",roles=())
  AND active S={name:"Clock"} and active A={title:"Notice",content:"Text"}
  AND at_time(2026-01-01T12:00:00Z); before=snapshot_scope([S,A])
WHEN browser loads /auth/dashboard/, opens/closes/reopens clock and dismisses announcement
THEN popup/overlay follow open/closed classes; announcement table becomes display none
  AND no mutation HTTP request or dismissal cookie/session value is produced
WHEN browser reloads /auth/dashboard/
THEN clock and announcement controls return; assert_unchanged(before)
```
