# Submission values, validation and save boundaries

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

### PH-C04a — test_submission_form_exposes_three_fields

Parent: `PH-C04` | Operation: `PH-P01-G` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN make_user(username="a",roles=("ACTIVE",)) creates A; B owns event F
  AND client = csrf_client(); login_actor(client,A); before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs /philanthropy/request/
THEN response is 200 using philanthropy_request.html
  AND form includes event_title, hours and event_date with a real CSRF cookie/token
  AND hours input has min="0.5" and step="0.5"
  AND F, A, B, their profile roles and event count are unchanged
```

### PH-C04b — test_integer_submission_persists_exact_values

Parent: `PH-C04` | Operation: `PH-P01-S` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F with hours 7
  AND at_time("2026-07-02T12:00:00Z") freezes view and model clocks
  AND client = csrf_client(); login_actor(client,A)
  AND A acquired a real cookie/token from GET /philanthropy/request/
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs request/ with {hours:"2",event_title:"Park cleanup",
      event_date:"2026-07-01",csrfmiddlewaretoken:form_token}
THEN response is 302 to philanthropy_dashboard with the submission success message
  AND exactly one new event has owner A, title "Park cleanup", hours 2, date 2026-07-01
  AND its status is requested and submission time is 2026-07-02T12:00:00Z
  AND decision name/date and editor/time are null; F, A/B roles and session user A are unchanged
```

### PH-C04c — test_submitted_owner_status_and_audit_are_ignored

Parent: `PH-C04` | Operation: `PH-P01-S` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F with hours 7
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs request/ with {hours:"2",event_title:"Park",event_date:"2026-07-01",
      user:B.id,user_id:B.id,status:"approved",philanthropy_approval_status:"approved",
      philanthropy_event_approver_name:"Forged",last_edited_by:B.id,
      philanthropy_event_submission_request_date:"2000-01-01T00:00:00Z",
      philanthropy_event_submission_approval_date:"2000-01-01T00:00:00Z"}
THEN response is 302 to philanthropy_dashboard
  AND one new event belongs to A, has requested status and null decision/editor fields
  AND request time is current, not 2000; F, A, B and profile roles are unchanged
```

### PH-C05a — test_submission_rejects_below_minimum_hours

Parent: `PH-C05` | Operation: `PH-P01-S` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F with hours 7
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs request/ with {event_title:"Park",event_date:"2026-07-01"}
  AND hours is separately "0", "-1" or "0.49"
THEN response is 200 request form with "Must request at least 0.5 hours."
  AND event count is unchanged; no A event is inserted
  AND F, A, B, profile roles and session identity remain unchanged
```

### PH-C05b — test_integral_float_string_preserves_integer_hours

Parent: `PH-C05` | Operation: `PH-P01-S` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F with hours 7
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs request/ with {hours:"2.0",event_title:"Park",event_date:"2026-07-01"}
THEN response is 302 to philanthropy_dashboard
  AND one new requested A event has fresh-DB hours exactly 2
  AND title/date are "Park"/2026-07-01; decision and editor fields are null
  AND F, A, B, profile roles and session identity remain unchanged
```

### PH-C05c — test_fractional_submission_requires_precision_policy

Parent: `PH-C05` | Operation: `PH-P01-S` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q1 precision/step; D2 float to IntegerField truncation
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F with hours 7
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs request/ with {event_title:"Park",event_date:"2026-07-01"}
  AND hours is separately "0.5", "1.5" or "2.25"
THEN Q1 chooses exact supported fractional storage or controlled rejection
  AND no accepted input may silently become 0, 1 or 2 respectively
  AND rejected input inserts no event; accepted input creates only A's requested event
  AND F, A, B, profile roles and session identity are unchanged
```

### PH-C05d — test_edit_minimum_and_fractional_hours_require_policy

Parent: `PH-C05` | Operation: `PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q1 minimum/precision; Q3 edit scope; D2 integer truncation
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–263`

```text
GIVEN C has ACTIVE+PHIL_CHAIR and owns requested E with hours 2
  AND B owns approved F; before = snapshot_scope([C,B,E,F],
      relations=(C_profile.roles, B_profile.roles))
WHEN C POSTs edit/E.id/ with {event_title:"Edited",event_date:"2026-07-02"}
  AND hours is separately "0", "-1", "0.49", "0.5", "1.5", "2.25" or "2.0"
THEN Q1 chooses shared minimum, allowed steps and exact stored precision
  AND Q3 chooses whether this target can be edited
  AND rejection preserves every E field including editor/time; acceptance cannot truncate
  AND E owner/submission time, F, C, B and role relations are unchanged
```

### PH-C06a — test_submission_parse_errors_leave_no_event

Parent: `PH-C06` | Operation: `PH-P01-S` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F with hours 7
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs request/ with {event_title:"Park",event_date:"2026-07-01"}
  AND hours is omitted, "", "   " or "abc" in separate requests
THEN response is 200 request form with an error message, not submission success
  AND no new A event exists and event count is unchanged
  AND F, A, B, profile roles and session identity are unchanged
  AND raw exception wording is not asserted as a preservation contract
```

### PH-C06b — test_submission_nonfinite_hours_create_no_record

Parent: `PH-C06` | Operation: `PH-P01-S` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F with hours 7
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs request/ with {event_title:"Park",event_date:"2026-07-01"}
  AND hours is separately "NaN", "nan", "Infinity", "-Infinity" or "1e309"
THEN response is 200 request form with an error and no success message
  AND no new event exists, including a zero-hours converted event
  AND F, A, B, profile roles and session identity are unchanged
  AND this does not settle finite upper bounds or exception disclosure policy
```

### PH-C06c — test_edit_invalid_hours_returns_controlled_error

Parent: `PH-C06` | Operation: `PH-P03-E` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D3 uncaught edit conversion/save errors; Q9 error adapter
Source: `SPDWEBAPP/PHILANTHROPY/views.py:253–260`

```text
GIVEN C has ACTIVE+PHIL_CHAIR and owns requested E with hours 2 and old editor D
  AND B owns approved F; before = snapshot_scope([C,B,D,E,F],
      relations=(C_profile.roles, B_profile.roles, D_profile.roles))
WHEN C POSTs edit/E.id/ with {event_title:"Edited",event_date:"2026-07-02"}
  AND hours is omitted, "", "   ", "abc", "NaN", "nan", "Infinity", "-Infinity" or "1e309"
THEN response must report a controlled input error without a server traceback
  AND source's uncaught TypeError/ValueError/OverflowError is a defect, not expected output
  AND E including old editor/time, F, actors, profile roles and event count are unchanged
```

### PH-C06d — test_huge_finite_hours_need_upper_bound

Parent: `PH-C06` | Operation: `PH-P01-S, PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q1 upper bound; Q3 edit scope; backend integer range
Source: `SPDWEBAPP/PHILANTHROPY/views.py:64–79,253–260`

```text
GIVEN ACTIVE A and C with ACTIVE+PHIL_CHAIR exist; C owns requested E with hours 2
  AND B owns approved F; before = snapshot_scope([A,B,C,E,F],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles))
WHEN A POSTs request/ with {hours:"1e100",event_title:"Park",event_date:"2026-07-01"}
  AND separately C POSTs E edit with the identical three fields
THEN Q1 chooses maximum finite hours and requires rejection outside that bound
  AND an accepted value must be stored exactly, not overflow or truncate
  AND rejected submission inserts no row; rejected edit preserves E including editor/time
  AND F, users and profile roles stay unchanged on SQLite and PostgreSQL
```

### PH-C07a — test_missing_submission_keys_and_bad_dates_do_not_write

Parent: `PH-C07` | Operation: `PH-P01-S` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F
  AND base payload is {hours:"2",event_title:"Park",event_date:"2026-07-01"}
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs request/ independently omitting event_title or event_date
  AND separately sets event_date to "", "not-a-date" or "2026-02-30"
THEN each response is 200 request form with error and no submission success
  AND no event is inserted
  AND F, A, B, their profile role relations and session user A are unchanged
```

### PH-C07b — test_empty_and_overlong_titles_require_validation_policy

Parent: `PH-C07` | Operation: `PH-P01-S, PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q2 required/trimmed title and max handling; Q3 edit scope
Source: `SPDWEBAPP/PHILANTHROPY/views.py:68–79,253–260; SPDWEBAPP/PHILANTHROPY/models.py:14`

```text
GIVEN ACTIVE A and C with ACTIVE+PHIL_CHAIR exist; C owns requested E with title "Old"
  AND B owns approved F; before = snapshot_scope([A,B,C,E,F],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles))
WHEN A submits and C separately edits E with {hours:"2",event_date:"2026-07-01"}
  AND event_title is separately "", "   " or 101 literal "x" characters
THEN Q2 chooses field errors or explicit normalization within the model's 100-character limit
  AND rejected submission creates no row; rejected edit preserves all E fields
  AND accepted text is not silently truncated; F, actors and role relations are unchanged
```

### PH-C07c — test_hundred_character_title_round_trips

Parent: `PH-C07` | Operation: `PH-P01-S` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F
  AND title is exactly 100 literal "x" characters
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs request/ with {hours:"2",event_title:title,event_date:"2026-07-01"}
THEN response is 302 to philanthropy_dashboard
  AND exactly one requested A event has the entire 100-character title and hours 2
  AND no old row is updated; F, A, B and profile roles are unchanged
  AND no DB-backend truncation is accepted
```

### PH-C07d — test_unicode_and_html_title_render_as_text

Parent: `PH-C07` | Operation: `PH-P01-S, PH-P04-D` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F
  AND title is 'Δ cleanup <script>alert("demo")</script>'
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A submits {hours:"2",event_title:title,event_date:"2026-07-01"}
  AND GETs /philanthropy/?year=2026
THEN submission redirects 302 and dashboard returns 200
  AND A's new requested event stores title exactly and has hours 2
  AND response contains escaped script tags, never a literal executable script element
  AND F, A, B, profile roles and the new event's values stay unchanged during GET
```

### PH-C07e — test_past_and_future_event_dates_need_policy

Parent: `PH-C07` | Operation: `PH-P01-S, PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q2 date range; Q3 edit scope
Source: `SPDWEBAPP/PHILANTHROPY/views.py:68–79,253–260`

```text
GIVEN at_time("2026-07-02T12:00:00Z"); ACTIVE A and C with ACTIVE+PHIL_CHAIR exist
  AND C owns requested E; B owns approved F; before = snapshot_scope([A,B,C,E,F],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles))
WHEN A submits and C separately edits E with {hours:"2",event_title:"Park"}
  AND event_date is separately "1900-01-01" or "2099-12-31"
THEN Q2 chooses unrestricted calendar dates or a named allowed date range
  AND rejection returns a controlled error without creating/changing an event
  AND permitted edits may change only Q3's fields, not owner/submission metadata
  AND F, actors, profile roles and session identities are unchanged
```

### PH-C08a — test_submit_prewrite_save_failure_is_reported_without_row

Parent: `PH-C08` | Operation: `PH-P01-S` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F
  AND inject RuntimeError("synthetic failure") immediately before event INSERT
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A submits {hours:"2",event_title:"Park",event_date:"2026-07-01"}
THEN response is 200 request form with an error and no success
  AND no new event is persisted; F, A, B and role relations are unchanged
  AND no persistent file exists; mock only the deliberate save failure boundary
```

### PH-C08b — test_identical_submit_retry_requires_idempotency_policy

Parent: `PH-C08` | Operation: `PH-P01-S` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 retries and duplicate identity
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F; before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs twice {hours:"2",event_title:"Park",event_date:"2026-07-01"}
THEN Q8 chooses two distinct submissions or one retried submission with stable identity
  AND response assertions must match that choice rather than assume deduplication
  AND every created row belongs to A, is requested and has exact hours/title/date
  AND decision/editor fields stay null; F, actors and profile roles remain unchanged
  AND requests retain authenticated user identity and create no persistent files
```

### PH-C08c — test_submit_postwrite_exception_needs_commit_policy

Parent: `PH-C08` | Operation: `PH-P01-S` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 rollback versus committed-success/retry identity; TransactionTestCase
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F
  AND a deliberate save wrapper INSERTs A's event then raises RuntimeError("after write")
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A submits {hours:"2",event_title:"Park",event_date:"2026-07-01"}
THEN Q8 chooses rollback with an error or committed success with retriable identity
  AND a failure response must not conceal a committed row from the caller
  AND a retry must follow the chosen duplicate policy
  AND F, A, B, profile roles and existing event rows remain unchanged
```

### PH-C08d — test_submission_does_not_disclose_save_exception_details

Parent: `PH-C08` | Operation: `PH-P01-S` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D4 raw exception disclosure; Q9 error adapter
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–81`

```text
GIVEN ACTIVE A and B exist; B owns approved F
  AND save raises RuntimeError("INTERNAL-SYNTHETIC-DETAIL") before INSERT
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A submits {hours:"2",event_title:"Park",event_date:"2026-07-01"}
THEN response must show a controlled error without "INTERNAL-SYNTHETIC-DETAIL"
  AND no traceback or internal exception representation is returned
  AND no event is inserted; F, A, B and profile roles remain unchanged
  AND source currently interpolates str(exception) into its visible message
```
