# Chicago calendar, utility boundaries and failures

Use [at_time](../../../../docs/testing/fixture-contract.md) at the consumed
`MISC.utils.datetime.now(tz)` boundary; preserve real datetime construction.
The frozen now(tz) must return that instant converted to requested Chicago tz.
UTC instants distinguish repeated local hours. Pure utility cases use SimpleTestCase.
Fall candidate 2026-11-01 02:00 CST is 08:00Z; physical rollback is 07:00Z.

<a id="misc-t12a"></a>

### MISC-T12a — test_spring_boundary_returns_strictly_future_calendar_date

Parent: `MISC-T12` | Operation: `MISC-O03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN independent at_time values 2026-03-08T07:59:59Z,
  AND 2026-03-08T08:00:00Z and 2026-03-08T08:00:01Z
WHEN get_next_dst_change() runs for each instant
THEN Chicago dates are 2026-03-08, 2026-11-01 and 2026-11-01 respectively
  AND each result is aware and strictly later than its input instant
  AND the pre-boundary spring result represents 2026-03-08T08:00:00Z
  AND no database, session, file or admin audit operation occurs
```

<a id="misc-t12b"></a>

### MISC-T12b — test_spring_returned_wall_label_needs_normalization_policy

Parent: `MISC-T12` | Operation: `MISC-O03` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q4 spring local-time label
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN at_time(2026-03-08T07:59:59Z)
WHEN get_next_dst_change() returns the spring candidate
THEN current candidate is nonexistent local 02:00 -06:00 but represents 08:00Z
  AND Q4 must choose normalized 03:00 -05:00 or documented transition-label value
  AND either choice must represent the physical 08:00Z instant
  AND this pure operation must never mutate database/session/files
```

<a id="misc-t13a"></a>

### MISC-T13a — test_fall_returned_transition_matches_physical_rollback

Parent: `MISC-T13` | Operation: `MISC-O03` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D2 physical fall UTC instant
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN at_time(2026-11-01T06:59:59Z)
WHEN get_next_dst_change() computes the next physical DST transition
THEN the returned aware instant must be 2026-11-01T07:00:00Z
  AND current candidate 02:00 CST represents 08:00Z and violates this invariant (D2)
  AND date-only message tests must not hide the one-hour error
  AND no database/session/file/audit operations occur
```

<a id="misc-t13b"></a>

### MISC-T13b — test_fall_exact_and_after_boundary_need_strictness_decision

Parent: `MISC-T13` | Operation: `MISC-O03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q4 exact-at semantics; D2 fall candidate
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN separate at_time values 2026-11-01T07:00:00Z and 2026-11-01T07:00:01Z
WHEN get_next_dst_change() runs
THEN Q4 must choose strictly-future or inclusive-current transition at exact 07:00:00Z
  AND under strict future both results represent next spring 2027-03-14T08:00:00Z
  AND under inclusive-current only the exact input may return 2026-11-01T07:00:00Z
  AND after 07:00:00Z no outcome may call 08:00Z the physical fall transition
  AND database/session/files/audit remain untouched
```

<a id="misc-t14a"></a>

### MISC-T14a — test_fall_candidate_boundary_must_not_become_physical_contract

Parent: `MISC-T14` | Operation: `MISC-O03` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q4 candidate compatibility; D2 physical fall instant
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN at_time separately 2026-11-01T07:59:59Z, 08:00:00Z and 08:00:01Z
WHEN get_next_dst_change() runs against current calendar candidates
THEN inspected current dates are 2026-11-01, 2027-03-14 and 2027-03-14
  AND Q4 chooses whether compatibility uses candidate labels or physical transition instants
  AND physical-transition acceptance requires next spring for all three inputs
  AND current 08:00Z fall label must not be silently approved as a real rollback
  AND no persistence/session/file effects occur
```

<a id="misc-t15a"></a>

### MISC-T15a — test_year_rollover_keeps_next_spring_date

Parent: `MISC-T15` | Operation: `MISC-O03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN at_time separately 2027-01-01T05:59:59Z and 2027-01-01T06:00:00Z
  AND these are Chicago Dec 31 23:59:59 and Jan 1 00:00:00
WHEN get_next_dst_change() runs for each
THEN both aware outputs have Chicago date 2027-03-14 and instant 08:00Z on that date
  AND both are strictly in the future and neither is None
  AND no database/session/file/admin audit operation occurs
```

<a id="misc-t15b"></a>

### MISC-T15b — test_second_and_first_sunday_dates_across_years

Parent: `MISC-T15` | Operation: `MISC-O03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN (UTC clock, expected Chicago date) separately
  AND (2027-01-01T12:00:00Z,2027-03-14), (2027-04-01T12:00:00Z,2027-11-07)
  AND (2028-01-01T12:00:00Z,2028-03-12), (2028-04-01T12:00:00Z,2028-11-05)
WHEN get_next_dst_change() runs under at_time for each concrete clock
THEN each aware output has its explicitly enumerated expected date
  AND no test copies the weekday formula or asserts the defective fall UTC instant
  AND ordinary current/next-year inputs never return None; no state is written
```

<a id="misc-t15c"></a>

### MISC-T15c — test_chicago_calendar_is_independent_of_django_timezone

Parent: `MISC-T15` | Operation: `MISC-O03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN at_time(2026-01-01T05:30:00Z) patches MISC.utils.datetime.now(tz)
  AND Django active timezone separately UTC, Asia/Tokyo and America/Los_Angeles
WHEN get_next_dst_change() runs for each timezone override
THEN each aware result represents 2026-03-08T08:00:00Z and Chicago date 2026-03-08
  AND output is not naive and does not inherit the display timezone
  AND no database/session/file/admin audit operation occurs
```

<a id="misc-t16a"></a>

### MISC-T16a — test_tag_none_result_uses_unavailable_message

Parent: `MISC-T16` | Operation: `MISC-O02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templatetags/dls_tags.py:11–35`

```text
GIVEN no setting rows; injected tag-imported get_next_dst_change returns None
WHEN dls_alert() runs
THEN show_alert=True and next_change=None
  AND message="Daylight Saving Time information unavailable."
  AND inclusion fragment has clockButton and that plain fallback text
  AND no setting, announcement, session or LogEntry changes
  AND injected None is a boundary case, not a normal calendar expectation
```

<a id="misc-t16b"></a>

### MISC-T16b — test_tag_none_result_still_allows_setting_override

Parent: `MISC-T16` | Operation: `MISC-O02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templatetags/dls_tags.py:11–35`

```text
GIVEN S={is_active:False,name:"Maintenance"}; before=snapshot_scope([S])
  AND injected tag-imported get_next_dst_change returns None
WHEN dls_alert() runs
THEN show_alert=False, next_change=None and message="Maintenance"
  AND inclusion fragment has no clockButton or Maintenance popup
  AND assert_unchanged(before); no defaults, session changes or LogEntry writes
```

<a id="misc-t16c"></a>

### MISC-T16c — test_clock_or_timezone_failure_needs_error_policy

Parent: `MISC-T16` | Operation: `MISC-O03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q6 utility exception response/logging
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN S={is_active:False,name:"Disabled"}; before=snapshot_scope([S])
  AND separately inject UnknownTimeZoneError at pytz.timezone,
  AND RuntimeError("clock unavailable") at MISC.utils.datetime.now
WHEN invoking utility through tag/dashboard boundary
THEN Q6 must choose unavailable fragment with 200 or explicit safe error response
  AND current source propagates the injected exception before disabled-setting selection
  AND no outcome may persist defaults, alter S or leak exception details
  AND assert_unchanged(before); session identity remains unchanged
```

<a id="misc-t16d"></a>

### MISC-T16d — test_tag_dependency_exception_needs_fallback_policy

Parent: `MISC-T16` | Operation: `MISC-O02` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q6 failure isolation and logging
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN active S={name:"Keep"}; before=snapshot_scope([S])
  AND tag-imported utility raises RuntimeError("synthetic outage")
WHEN a logged-in reader GETs /auth/dashboard/
THEN Q6 must choose unavailable fragment with 200 or explicit safe error response
  AND current source does not catch this exception
  AND no exception details may be exposed to the reader
  AND assert_unchanged(before); announcement/user rows and session identity stay unchanged
  AND recovery must not require clearing a persisted fallback row
```

<a id="misc-t16e"></a>

### MISC-T16e — test_setting_lookup_failure_needs_database_error_policy

Parent: `MISC-T16` | Operation: `MISC-O02` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q6 database failure response
Source: `SPDWEBAPP/MISC/utils.py:4–28`

```text
GIVEN active S={name:"Keep"}; before=snapshot_scope([S])
  AND at_time(2026-01-01T12:00:00Z); inject OperationalError at setting lookup boundary
WHEN dls_alert() is consumed by a dashboard GET
THEN Q6 must choose unavailable fragment with 200 or explicit safe error response
  AND current DoesNotExist handler does not catch OperationalError
  AND assert_unchanged(before); no row/default/log may be written
  AND reader session identity must not change
```

<a id="misc-t16f"></a>

### MISC-T16f — test_injected_does_not_exist_keeps_tag_default

Parent: `MISC-T16` | Operation: `MISC-O02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/templatetags/dls_tags.py:23–30`

```text
GIVEN at_time(2026-01-01T12:00:00Z) and no setting rows
  AND deliberate failure injection makes objects.first raise DayLightSavingsAlert.DoesNotExist
WHEN dls_alert() runs
THEN show_alert=True and computed message contains March 08, 2026
  AND next_change is aware and no default setting is created
  AND no announcement, session or LogEntry changes
  AND this is exception-handler coverage; normal first() returns None instead
```
