# Announcement records and rendering

Use business settings and the [shared fixtures](../../../../docs/testing/fixture-contract.md).
Rows are real ORM fixtures; no demo seed or real content.

<a id="misc-t01a"></a>

### MISC-T01a — test_dashboard_selects_only_active_announcements

Parent: `MISC-T01` | Operation: `MISC-O01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–35`

```text
GIVEN make_user(username="reader", roles=("ACTIVE",)) and login_actor(client, reader)
  AND A={title:"Spring notice", content:"Bring paper", is_active:True}
  AND B={title:"Hidden notice", content:"Hidden content", is_active:False}
  AND C={title:"Meeting notice", content:"Room 4", is_active:True}
  AND before=snapshot_scope([A,B,C], relations=[reader.brother_profile.roles])
WHEN client GETs /auth/dashboard/
THEN response is 200 and announcements context has exactly PKs A and C
  AND Spring notice and Meeting notice each render once; Hidden notice is absent
  AND assert_unchanged(before); reader session identity is unchanged
```

<a id="misc-t01b"></a>

### MISC-T01b — test_next_dashboard_read_reflects_activation_change

Parent: `MISC-T01` | Operation: `MISC-O01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:33–35`

```text
GIVEN make_user(username="reader", roles=()) is logged in
  AND A={title:"Old notice", content:"Old", is_active:True}
  AND B={title:"New notice", content:"New", is_active:False}
  AND an initial GET /auth/dashboard/ includes A but excludes B
  AND ORM saves A.is_active=False and B.is_active=True
  AND before=snapshot_scope([A,B]) after those explicit fixture saves
WHEN client GETs /auth/dashboard/ again
THEN response is 200 and context PK set is exactly {B.pk}
  AND assert_unchanged(before); no read changes updated_at
```

<a id="misc-t01c"></a>

### MISC-T01c — test_announcement_order_requires_product_rule

Parent: `MISC-T01` | Operation: `MISC-O01` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q1 ordering
Source: `SPDWEBAPP/AUTHENTICATE/views.py:33–35`

```text
GIVEN active A title="Zebra" created_at=2026-01-01T12:00:00Z
  AND active B title="Apple" created_at=2026-02-01T12:00:00Z
  AND A.pk < B.pk and logged-in reader has roles=()
WHEN reader GETs /auth/dashboard/
THEN both A and B appear and neither row changes
  AND Q1 must choose newest-first, oldest-first or unspecified order
  AND only a chosen ordering rule may become an ordering assertion
```

<a id="misc-t02a"></a>

### MISC-T02a — test_dashboard_empty_or_inactive_only_has_no_table

Parent: `MISC-T02` | Operation: `MISC-O01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templates/MISC/announcement_alert.html:7–38`

```text
GIVEN make_user(username="reader", roles=()) is logged in
  AND separately fixtures are [] or [A={title:"Hidden", content:"No", is_active:False}]
  AND before=snapshot_scope(existing A rows)
WHEN client GETs /auth/dashboard/ twice
THEN both responses are 200 with empty announcements context
  AND neither response contains announcement-table or its close-button
  AND assert_unchanged(before); no AnnouncementAlert is created
```

<a id="misc-t03a"></a>

### MISC-T03a — test_announcement_create_defaults_and_string

Parent: `MISC-T03` | Operation: `MISC-O07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/models.py:16–24`

```text
GIVEN at_time(2026-01-02T12:00:00Z) controls Django model clocks
  AND B={title:"Other", content:"Keep", is_active:False} already exists
  AND before=snapshot_scope([B])
WHEN ORM creates A with title="Spring notice" and content="Bring paper"
THEN A.is_active is True and str(A) is "Spring notice"
  AND A.created_at and A.updated_at are aware 2026-01-02T12:00:00Z
  AND AnnouncementAlert count increases by exactly one
  AND assert_unchanged(before); no admin LogEntry is added
```

<a id="misc-t03b"></a>

### MISC-T03b — test_announcement_update_changes_only_update_timestamp

Parent: `MISC-T03` | Operation: `MISC-O07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/models.py:16–24`

```text
GIVEN A={title:"Notice", content:"Room 4"} created at 2026-01-02T12:00:00Z
  AND B={title:"Other", content:"Keep", is_active:False}
  AND before=snapshot_scope([A,B])
WHEN at_time(2026-01-03T12:00:00Z) saves A.title="Revised" and content="Room 5"
THEN fresh A has Revised and Room 5; str(A) is "Revised"
  AND A.updated_at is 2026-01-03T12:00:00Z; created_at is unchanged
  AND assert_unchanged(before, except_fields={A:{title,content,updated_at}})
  AND no admin LogEntry is added
```

<a id="misc-t03c"></a>

### MISC-T03c — test_unchanged_announcement_save_advances_updated_at

Parent: `MISC-T03` | Operation: `MISC-O07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/models.py:16–24`

```text
GIVEN A={title:"Notice", content:"Room 4"} saved at 2026-01-02T12:00:00Z
  AND before=snapshot_scope([A])
WHEN at_time(2026-01-03T12:00:00Z) saves A without assigning new fields
THEN fresh A.updated_at is 2026-01-03T12:00:00Z
  AND title, content, is_active, created_at and PK are unchanged
  AND assert_unchanged(before, except_fields={A:{updated_at}})
  AND row count remains one and no admin LogEntry is added
```

<a id="misc-t04a"></a>

### MISC-T04a — test_announcement_full_clean_rejects_missing_or_long_title

Parent: `MISC-T04` | Operation: `MISC-O07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/models.py:16–24`

```text
GIVEN unsaved AnnouncementAlert instances with (title,content) separately
  AND values are ("","Text"), ("Notice",""), ("x" repeated 256,"Text")
  AND existing B={title:"Other", content:"Keep"}; before=snapshot_scope([B])
WHEN each instance receives full_clean()
THEN ValidationError identifies title, content, title respectively
  AND none of the unsaved instances is persisted
  AND assert_unchanged(before); row count remains one; no logs are added
```

<a id="misc-t04b"></a>

### MISC-T04b — test_announcement_full_clean_accepts_maximum_title

Parent: `MISC-T04` | Operation: `MISC-O07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/models.py:16–24`

```text
GIVEN unsaved A with title="x" repeated 255 and content="Text"
  AND B={title:"Other", content:"Keep"}; before=snapshot_scope([B])
WHEN A.full_clean() succeeds and A.save() runs at_time(2026-01-02T12:00:00Z)
THEN fresh A.title has exactly 255 characters and content is "Text"
  AND A.is_active=True; both timestamps are aware and equal the frozen time
  AND exactly A is inserted; assert_unchanged(before)
  AND no admin LogEntry is added
```

<a id="misc-t04c"></a>

### MISC-T04c — test_future_announcement_write_validation_needs_boundary

Parent: `MISC-T04` | Operation: `MISC-O07` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q5 future write validation
Source: `SPDWEBAPP/MISC/models.py:16–24`

```text
GIVEN an unsaved announcement with title="" and content=""
  AND current model save has no full_clean hook
WHEN specifying a future service or API write operation
THEN Q5 must choose service/form validation or another explicit boundary
  AND candidate outcomes are field errors without writes or explicitly allowed blanks
  AND no backend-independent max-length DB rejection may be assumed
  AND existing unrelated announcement fields and session identity must stay unchanged
```

<a id="misc-t09a"></a>

### MISC-T09a — test_announcement_template_escapes_untrusted_text

Parent: `MISC-T09` | Operation: `MISC-O04` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templates/MISC/announcement_alert.html:18–31`

```text
GIVEN A.title='<script>alert(1)</script>'
  AND A.content='<img src=x onerror=alert(2)> & "quoted"'
  AND before=snapshot_scope([A])
WHEN rendering MISC/announcement_alert.html with announcements=[A]
THEN title/content appear as escaped text, including ampersand and quotes
  AND there is no script element or content-derived img element/event handler
  AND exactly one announcement-row appears
  AND assert_unchanged(before); no files, sessions or admin logs are written
```

<a id="misc-t09b"></a>

### MISC-T09b — test_announcement_template_prefers_updated_date

Parent: `MISC-T09` | Operation: `MISC-O04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templates/MISC/announcement_alert.html:23–28`

```text
GIVEN UTC template timezone and A.created_at=2026-01-02T12:00:00Z
  AND A.updated_at=2026-01-03T13:15:00Z; before=snapshot_scope([A])
WHEN rendering MISC/announcement_alert.html with announcements=[A]
THEN the date reads "Updated on: Jan 03, 2026, 13:15"
  AND no Created on label appears
  AND title/content remain present exactly once
  AND assert_unchanged(before); no LogEntry is created
```

<a id="misc-t09c"></a>

### MISC-T09c — test_announcement_template_created_date_fallback

Parent: `MISC-T09` | Operation: `MISC-O04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templates/MISC/announcement_alert.html:23–28`

```text
GIVEN UTC template timezone and unsaved A with title="Notice", content="Text"
  AND A.created_at=2026-01-02T12:00:00Z; A.updated_at=None
WHEN rendering MISC/announcement_alert.html with announcements=[A]
THEN date text reads "Created on: Jan 02, 2026, 12:00"
  AND no Updated on label appears
  AND A remains unsaved; AnnouncementAlert and LogEntry counts do not change
```

<a id="misc-t09d"></a>

### MISC-T09d — test_announcement_fragment_without_context_is_empty

Parent: `MISC-T09` | Operation: `MISC-O04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templates/MISC/announcement_alert.html:1–38`

```text
GIVEN existing A={title:"Not supplied", content:"Do not leak"}
  AND before=snapshot_scope([A])
WHEN rendering MISC/announcement_alert.html with context {} and then {announcements:[]}
THEN neither result has announcement-container, table, close-button or A.title
  AND the static stylesheet link may remain
  AND assert_unchanged(before); no default announcement or LogEntry is created
```
