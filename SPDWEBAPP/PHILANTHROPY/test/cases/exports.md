# Workbook values, scope and text safety

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

### PH-C25a — test_xlsx_content_totals_and_typed_hours

Parent: `PH-C25` | Operation: `PH-P06-X` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:163–239`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; ACTIVE A/B names are "Alex One"/"Blair Two"
  AND A approved events E2/E3 are dated 2025-07-01/2025-07-02; B approved F10 is later
  AND E2 approver is null; E3/F10 approver is "Casey Chair"; requested R and denied D exist
  AND before = snapshot_scope([A,B,C,E2,E3,F10,R,D],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles))
WHEN C GETs export and openpyxl loads BytesIO(body) with data_only=False
THEN response is 200, XLSX MIME, attachment filename approved_philanthropy_hours.xlsx
  AND sheet is "Philanthropy Hours"; name blocks start columns A/F with merged rows1/2
  AND row3 headers are Date/Event/Hours/Approved By; totals are "Total: 5"/"Total: 10"
  AND rows contain exact ISO dates/titles, numeric2/3/10 and em dash for missing approver
  AND A dates ascend; each approved event appears once; R/D are absent
  AND E2/E3/F10/R/D, actors, roles and event count are unchanged; no file is persisted
```

### PH-C25b — test_xlsx_total_fill_thresholds_and_event_wrapping

Parent: `PH-C25` | Operation: `PH-P06-X` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:176–228`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; ACTIVE A/B/D have distinct names
  AND their approved totals are exactly 4/5/10 from E/F/G on distinct dates
  AND before = snapshot_scope([A,B,C,D,E,F,G],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles, D_profile.roles))
WHEN C GETs export and openpyxl loads BytesIO(body) with data_only=False
THEN response is 200 and block totals are "Total: 4","Total: 5","Total: 10"
  AND fills are FFC7CE/FFEB9C/C6EFCE respectively, comparing normalized RGB suffix
  AND Event column data cells wrap text; four data columns have a spacer between blocks
  AND E/F/G, actors, profile roles and event count remain unchanged
  AND archive bytes and incidental auto-width values are not compared
```

### PH-C26a — test_export_actor_permissions_require_policy

Parent: `PH-C26` | Operation: `PH-P06-X` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q6 authorized export roles and profile requirement
Source: `SPDWEBAPP/PHILANTHROPY/views.py:137–239`

```text
GIVEN A_active/A_alumni/A_none/A_chair/A_both have respectively
      ACTIVE/ALUMNI/()/PHIL_CHAIR/(ACTIVE+PHIL_CHAIR); A_profileless has no profile
  AND B owns approved E and denied F
  AND before = snapshot_scope([A_active,A_alumni,A_none,A_chair,A_both,A_profileless,B,E,F],
      relations=(A_active_profile.roles, A_alumni_profile.roles, A_none_profile.roles,
      A_chair_profile.roles, A_both_profile.roles, B_profile.roles))
WHEN each of those six authenticated actors GETs export-philanthropy-hours/
THEN Q6 chooses which actors may receive chapter XLSX bytes
  AND denied actors receive no E title/name/hours or XLSX attachment/body
  AND allowed actors receive only the agreed Q6 export scope
  AND E/F and the six actors/B, their profiles/role relations and event count are unchanged
  AND login-only source acceptance is evidence, not the selected authorization policy
```

### PH-C26b — test_export_year_owner_and_active_scope_require_policy

Parent: `PH-C26` | Operation: `PH-P06-X` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q6 year/owner/ACTIVE scope and fallback naming
Source: `SPDWEBAPP/PHILANTHROPY/views.py:137–239`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; ACTIVE A, ALUMNI D and profileless E own approved rows
  AND approved rows E_A25/E_D26/E_E25 fall in AY2025/AY2026/AY2025
  AND requested R and denied F also exist
  AND before = snapshot_scope([C,A,D,E,E_A25,E_D26,E_E25,R,F],
      relations=(C_profile.roles, A_profile.roles, D_profile.roles))
WHEN C GETs export?year=2025&user_id=A.id
THEN Q6 chooses all-time versus selected-year and chapter versus owner scope
  AND Q6 chooses ACTIVE-only inclusion versus inactive/profileless inclusion
  AND included owners have agreed display name or username fallback; excluded rows are absent
  AND requested/denied rows never contribute; no event/user/profile/role is changed
  AND no persistent file is created; source ignores both query parameters
```

### PH-C27a — test_same_name_active_owners_keep_separate_export_totals

Parent: `PH-C27` | Operation: `PH-P06-X` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D9 display-name grouping merges identities; Q6 presentation only
Source: `SPDWEBAPP/PHILANTHROPY/views.py:137–239`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; ACTIVE A and B are both named "Alex Example"
  AND A owns approved E hours2; B owns approved F hours7; names are deliberately identical
  AND before = snapshot_scope([A,B,C,E,F],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles))
WHEN C GETs export and openpyxl loads BytesIO(body) with data_only=False
THEN E and F must belong to distinct owner blocks with totals2 and7
  AND one merged "Total: 9" block must not represent both people
  AND Q6 may choose label disambiguation without changing the identity invariant
  AND E, F, actors, profile role relations and event count are unchanged
```

### PH-C27b — test_username_and_full_name_collision_requires_export_scope

Parent: `PH-C27` | Operation: `PH-P06-X` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q6 inactive/profileless inclusion; D9 grouping identity
Source: `SPDWEBAPP/PHILANTHROPY/views.py:137–239`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; ACTIVE A is named "Alex Example" and owns E2
  AND profileless User B has username "Alex Example" and owns approved F7
  AND before = snapshot_scope([A,B,C,E2,F7],
      relations=(A_profile.roles, C_profile.roles))
WHEN C GETs export and openpyxl loads BytesIO(body) with data_only=False
THEN Q6 chooses whether B is included
  AND if included, A/B retain distinct identities and separate totals2/7, never combined9
  AND if excluded, F7 contributes neither rows nor hours
  AND E2/F7, actors, profile roles and event count remain unchanged
```

### PH-C28a — test_equals_prefixed_user_content_is_never_formula_typed

Parent: `PH-C28` | Operation: `PH-P06-X` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D10 openpyxl treats raw equals text as formula; Q6 actor scope only
Source: `SPDWEBAPP/PHILANTHROPY/views.py:137–239`

```text
GIVEN C has ACTIVE+PHIL_CHAIR and ACTIVE A owns approved E hours2
  AND separately A's display-name first character, E title or E approver is "=1+1"
  AND before = snapshot_scope([A,C,E],
      relations=(A_profile.roles, C_profile.roles))
WHEN C GETs export and openpyxl loads BytesIO(body) with data_only=False
THEN every user-supplied cell must have data_type other than "f"
  AND display text is retained as literal text; numeric hours remain numeric2
  AND no spreadsheet program, formula evaluator or network link is executed
  AND E, actors, profile roles and event count remain unchanged
  AND the formula assertion is independent of a particular escaping presentation
```

### PH-C28b — test_other_formula_like_prefixes_need_client_protection_policy

Parent: `PH-C28` | Operation: `PH-P06-X` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q12 spreadsheet-client targets and escaping; Q6 profileless scope
Source: `SPDWEBAPP/PHILANTHROPY/views.py:137–239`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; A owns approved E hours2
  AND separately name/title/approver uses "+SUM(A1:A2)","-1+2","@SUM(A1:A2)"
  AND profileless B has a formula-like username; prefix variants add tab/newline before "=1+1"
  AND before = snapshot_scope([A,B,C,E],
      relations=(A_profile.roles, C_profile.roles))
WHEN C GETs export and openpyxl loads BytesIO(body) with data_only=False
THEN Q12 chooses required spreadsheet clients and a reversible text-escaping rule
  AND included user text must not become an executable formula in a supported client
  AND Q6 decides whether the profileless username fixture belongs in output
  AND E, actors, profile roles and event count remain unchanged
```

### PH-C28c — test_unicode_and_plain_multiline_export_text_round_trips

Parent: `PH-C28` | Operation: `PH-P06-X` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:137–239`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; ACTIVE A named "Δ Member" owns approved E hours2
  AND E title is "Park\ncleanup\tteam" and approver is "Zoë Chair"
  AND before = snapshot_scope([A,C,E],
      relations=(A_profile.roles, C_profile.roles))
WHEN C GETs export and openpyxl loads BytesIO(body) with data_only=False
THEN response is 200; name/title/approver equal the original Unicode and plain multiline text
  AND these cells are strings, not formulas, and hours cell is numeric2
  AND E, actors, profile roles and event count remain unchanged
  AND no external spreadsheet client or network service is invoked
```

### PH-C29a — test_export_with_no_approved_events_is_readable_empty_workbook

Parent: `PH-C29` | Operation: `PH-P06-X` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:145–169,230–239`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; A owns requested E and denied F, no approved event exists
  AND before = snapshot_scope([A,C,E,F],
      relations=(A_profile.roles, C_profile.roles))
WHEN C GETs export and openpyxl loads BytesIO(body) with data_only=False
THEN response is 200 with XLSX MIME and attachment filename
  AND workbook contains "Philanthropy Hours" but no member name, title or total block
  AND E/F, actors, role relations and event count remain unchanged
  AND no disk file is created
```

### PH-C29b — test_workbook_serialization_failure_is_controlled

Parent: `PH-C29` | Operation: `PH-P06-X` | Priority: P1
Status: `NEEDS_FIX` | Blockers: D11 uncaught Workbook.save failure; Q9 error adapter
Source: `SPDWEBAPP/PHILANTHROPY/views.py:230–239`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; A owns approved E and unrelated requested F
  AND Workbook.save deliberately raises RuntimeError("synthetic serialization failure")
  AND before = snapshot_scope([A,C,E,F],
      relations=(A_profile.roles, C_profile.roles))
WHEN C GETs export
THEN response must be a controlled error, not an unhandled traceback
  AND it returns no partial XLSX attachment or private cell contents
  AND E/F, actors, profile roles and event count remain unchanged
  AND no persistent file exists; only serializer failure is mocked
```
