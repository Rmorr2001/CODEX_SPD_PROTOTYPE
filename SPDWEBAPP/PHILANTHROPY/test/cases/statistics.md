# Academic years, dashboard totals and helpers

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

### PH-C17a — test_academic_year_dates_are_july_through_june

Parent: `PH-C17` | Operation: `PH-P04-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–61`

```text
GIVEN no ORM rows or network services are needed
WHEN get_academic_year_dates(2025) is called
THEN result is (date(2025,7,1),date(2026,6,30))
  AND get_academic_year_dates(2023) includes leap day within its range
  AND range start/end are calendar dates, not time-dependent datetimes
  AND no DB or filesystem operation occurs
  AND the pure helper is a SimpleTestCase candidate
  AND this is a SimpleTestCase design; no database fixture is required
```

### PH-C17b — test_available_years_before_and_after_july

Parent: `PH-C17` | Operation: `PH-P04-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–61`

```text
GIVEN at_time patches the clock consumed by get_available_academic_years
WHEN clock is 2026-06-30T23:59:59Z and helper is called with no arguments
THEN result is exactly [2025,2024,2023]
  AND at 2026-07-01T00:00:00Z the result is [2026,2025,2024]
  AND ordering is descending with three year starts, not three arbitrary dates
  AND no DB or filesystem state changes
  AND no browser-local timezone assumption is made
  AND this is a SimpleTestCase design; no database fixture is required
```

### PH-C17c — test_available_year_count_can_be_zero_or_one

Parent: `PH-C17` | Operation: `PH-P04-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–61`

```text
GIVEN at_time("2026-07-02T12:00:00Z") patches the helper clock
WHEN get_available_academic_years(past=1) is called
THEN result is exactly [2026]
  AND calling with past=0 returns []
  AND default past remains three rather than mutating across calls
  AND no user, event or file is accessed or changed
  AND this is a SimpleTestCase design; no database fixture is required
  AND no authentication session, event row or persistent file is created
```

### PH-C17d — test_dashboard_default_year_before_july

Parent: `PH-C17` | Operation: `PH-P04-D` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:14–57`

```text
GIVEN ACTIVE A owns approved E dated 2026-06-30 with hours 2
  AND B owns unrelated approved F; before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
  AND at_time("2026-06-30T23:59:59Z")
WHEN A GETs /philanthropy/ without year
THEN response is 200 with selected_year=2025 and label "2025–2026 Academic Year"
  AND A's year events contain E and approved personal total is 2
  AND E, F, A, B, profile roles and event count remain unchanged
```

### PH-C17e — test_dashboard_default_year_from_july

Parent: `PH-C17` | Operation: `PH-P04-D` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:14–57`

```text
GIVEN ACTIVE A owns approved E dated 2026-07-01 with hours 2
  AND B owns unrelated approved F; before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
  AND at_time("2026-07-01T00:00:00Z")
WHEN A GETs /philanthropy/ without year
THEN response is 200 with selected_year=2026 and label "2026–2027 Academic Year"
  AND A's year events contain E and approved personal total is 2
  AND E, F, A, B, profile roles and event count remain unchanged
```

### PH-C17f — test_explicit_dashboard_year_overrides_clock

Parent: `PH-C17` | Operation: `PH-P04-D` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:22–57`

```text
GIVEN ACTIVE A owns approved E dated 2024-07-01 with hours 2
  AND B owns unrelated approved F; before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
  AND at_time("2026-07-02T12:00:00Z")
WHEN A GETs /philanthropy/?year=2024
THEN response is 200 with selected_year=2024 and label "2024–2025 Academic Year"
  AND A's total is 2; available years are still [2026,2025,2024]
  AND E, F, A, B, profile roles and event count remain unchanged
```

### PH-C17g — test_date_helper_invalid_arguments_need_contract

Parent: `PH-C17` | Operation: `PH-P04-H` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q2 pure-helper supported arguments
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–61`

```text
GIVEN get_academic_year_dates and get_available_academic_years are internal helpers
WHEN year is separately 0, 9999, "2025" or None
  AND separately past is -1, "3" or None
THEN Q2 chooses typed internal preconditions or explicit argument validation
  AND conditional outcomes name a controlled rejection or documented empty result
  AND no incidental TypeError, year overflow or arbitrary coercion is frozen as policy
  AND no DB, user, event or filesystem state changes
  AND this is a SimpleTestCase design; no database fixture is required
```

### PH-C18a — test_chapter_and_personal_approved_totals_are_scoped

Parent: `PH-C18` | Operation: `PH-P04-D, PH-P04-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–61`

```text
GIVEN A/B/C have ACTIVE; D has ALUMNI; profiles are created in A,B,C order
  AND A is Alex Able, B is Blair Baker and C is Casey Cole
  AND approved 2025-07-01 events A5/B10/D99 have hours5/10/99
  AND A has requested R40 hours40, denied N50 hours50 and approved O70 dated 2025-06-30
  AND before = snapshot_scope([A,B,C,D,A5,B10,D99,R40,N50,O70],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles, D_profile.roles))
WHEN A GETs /philanthropy/?year=2025 and H2 helpers query (2025-07-01,2026-06-30)
THEN response is 200; chapter total15, ACTIVE count3, average5 and goal count1
  AND sorted dashboard progress is [(B,"Blair Baker",10),(A,"Alex Able",5),(C,"Casey Cole",0)]
  AND all three full names are rendered as member labels
  AND the collection helper retains its explicitly supplied A,B,C order and full names
  AND own events are A5/R40/N50, own total5; B10/D99/O70 do not enter own in-range list
  AND A5/B10/D99/R40/N50/O70, users A/B/C/D and their profile roles are unchanged
```

### PH-C18b — test_goal_threshold_is_ten_approved_hours

Parent: `PH-C18` | Operation: `PH-P04-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–61`

```text
GIVEN ACTIVE A is the only supplied profile; B owns unrelated event F
  AND A's approved AY total is separately 0,4,5,9,10 or 11 with no pending hours
  AND A_events=[] for total0, otherwise [approved E with hours equal to that total]
  AND before = snapshot_scope([A,B,F,A_events],
      relations=(A_profile.roles, B_profile.roles))
WHEN collect_philanthropy_statistics queries (2025-07-01,2026-06-30)
THEN total equals the concrete approved total and progress has exactly A
  AND members_meeting_goal is respectively 0,0,0,0,1,1
  AND neither 5 nor 9 approved hours counts as meeting the goal
  AND A's events, F, A/B profiles and their role relations remain unchanged
```

### PH-C18c — test_multiple_nonactive_roles_do_not_duplicate_statistics

Parent: `PH-C18` | Operation: `PH-P04-D, PH-P04-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–61`

```text
GIVEN A has ACTIVE+EXEC+PHIL_CHAIR and one approved AY event E hours 2
  AND B has ACTIVE+ALUMNI and one approved AY event F hours 3
  AND before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs /philanthropy/?year=2025
THEN response is 200 with exactly two progress rows
  AND chapter total is 5, ACTIVE count is 2 and average is 2.5
  AND E, F, A, B and every named role relation are unchanged
```

### PH-C19a — test_year_range_includes_july_first_and_june_thirtieth

Parent: `PH-C19` | Operation: `PH-P04-D, PH-P04-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–61`

```text
GIVEN ACTIVE A owns approved events E1/E2/E3/E4 with hours 1/2/3/4
  AND dates are 2025-06-30,2025-07-01,2026-06-30,2026-07-01 respectively
  AND B owns unrelated F; before = snapshot_scope([A,B,E1,E2,E3,E4,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs /philanthropy/?year=2025 and H2 helpers query that AY
THEN response is 200; own events are [E3,E2] and own total is 5
  AND A's chapter progress total is 5; neither outside boundary contributes
  AND E1/E2/E3/E4/F, users, profile roles and event count remain unchanged
```

### PH-C19b — test_empty_selected_year_retains_zero_active_members

Parent: `PH-C19` | Operation: `PH-P04-D, PH-P04-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–61`

```text
GIVEN ACTIVE A and B have no event in the 2025 AY
  AND A owns approved E dated 2024-07-01; B owns approved F dated 2026-07-01
  AND before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs /philanthropy/?year=2025
THEN response is 200 with own empty-events text, personal total0 and chapter total0
  AND progress includes A0 and B0; average0, ACTIVE count2 and goal count0
  AND no order is required between the equal zero totals
  AND E, F, users, profile roles and event count remain unchanged
```

### PH-C19c — test_statistics_empty_profile_input_returns_zeroes

Parent: `PH-C19` | Operation: `PH-P04-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–61`

```text
GIVEN A/B profiles and their E/F events exist outside the supplied empty profile list
  AND before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN collect_philanthropy_statistics([],date(2025,7,1),date(2026,6,30)) is called
THEN result is exactly ([],0,0)
  AND no division or null total escapes the helper
  AND E, F, A, B and role relations remain unchanged
  AND no mock replaces ORM aggregate behavior
```

### PH-C19d — test_unwrapped_dashboard_zero_denominator_is_safe

Parent: `PH-C19` | Operation: `PH-P04-D` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:28–57`

```text
GIVEN A has a profile with no roles; B has ALUMNI and owns approved F
  AND RequestFactory request has A/session/messages; no ACTIVE profile exists
  AND before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN the twice-unwrapped philanthropy_dashboard callable renders the request
THEN response is 200 with total_active_members=0 and avg_hours_per_brother=0
  AND chapter total0, goal count0 and progress[] are rendered without division error
  AND F, users and role relations stay unchanged; no active query is mocked
  AND this branch test is not evidence of authorization for unwrapped callers
```

### PH-C20a — test_invalid_dashboard_year_is_a_controlled_error

Parent: `PH-C20` | Operation: `PH-P04-D` | Priority: P1
Status: `NEEDS_FIX` | Blockers: D7 uncaught int/date errors; Q2 supported range; Q9 adapter
Source: `SPDWEBAPP/PHILANTHROPY/views.py:22–25`

```text
GIVEN ACTIVE A and B exist; B owns approved F; before = snapshot_scope([A,B,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs dashboard with year="", "abc", "2025.5", "0", "9999"
  AND separately year="999999999999999999999999999999"
THEN response must return controlled year validation without a server traceback
  AND it cannot return another member's data as a fallback for malformed input
  AND F, A, B, profile roles, event count and session user A remain unchanged
  AND Q2 defines the final supported range without blessing current crashes
```

### PH-C20b — test_historical_year_outside_dropdown_needs_range_policy

Parent: `PH-C20` | Operation: `PH-P04-D` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q2 supported selected-year range
Source: `SPDWEBAPP/PHILANTHROPY/views.py:22–54`

```text
GIVEN ACTIVE A owns approved E dated 2000-07-01; B owns unrelated F
  AND at_time("2026-07-02T12:00:00Z"); before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs /philanthropy/?year=2000
THEN Q2 chooses historical-year support or a controlled out-of-range response
  AND allowed support uses AY 2000–2001, never the current-year event set
  AND rejected input must not change a record
  AND E, F, actors, profile roles and session identity are unchanged
```

### PH-C20c — test_declared_chair_dashboard_flag_needs_canonical_role_policy

Parent: `PH-C20` | Operation: `PH-P04-D, PH-P05-H` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q7 canonical flag or flag removal
Source: `SPDWEBAPP/PHILANTHROPY/views.py:38,104; SPDWEBAPP/AUTHENTICATE/models.py:58–77`

```text
GIVEN C has ACTIVE+PHIL_CHAIR and owns approved E; B owns unrelated F
  AND before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
WHEN C GETs dashboard and C's own history
THEN source dashboard chair flag is false while history chair flag is true
  AND Q7 chooses PHIL_CHAIR consistently or removes the unused dashboard flag
  AND flag assertions must not infer permissions from visible buttons
  AND E, F, C, B and role relations remain unchanged
```

### PH-C20d — test_undeclared_chair_role_cannot_gain_decision_permissions

Parent: `PH-C20` | Operation: `PH-P04-D, PH-P02-A, PH-P03-E` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q7 invalid-role flag handling; D8 role-name inconsistency
Source: `SPDWEBAPP/PHILANTHROPY/views.py:38,83–85,243–245`

```text
GIVEN A has ACTIVE; explicit local ORM inserts corrupt_role named PHILANTHROPY_CHAIR
  AND A is linked to that role deliberately bypassing factory role validation
  AND B owns requested E and approved F; before = snapshot_scope([A,B,E,F,corrupt_role],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs dashboard, POSTs approve {event_id:E.id,action:"approve"}
  AND POSTs E edit {event_title:"Edited",hours:"3",event_date:"2026-07-02"}
THEN Q7 chooses canonical flag/removal; source currently marks dashboard chair=true
  AND decision/edit responses remain role-denied302 without PHIL_CHAIR
  AND E, F, users and explicit role relations stay unchanged
  AND the corrupt role must not be added to shared fixtures or production seeding
```
