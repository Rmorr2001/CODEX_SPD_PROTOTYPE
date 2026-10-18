# Individual history and remaining-hours tag

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

### PH-C21a — test_history_helper_buckets_approved_events_and_lifetime

Parent: `PH-C21` | Operation: `PH-P05-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:98–120; SPDWEBAPP/PHILANTHROPY/views_functions.py:89–123`

```text
GIVEN B owns approved events E1/E2/E3/E4 hours 2/3/4/5
  AND dates are 2025-06-30,2025-07-01,2026-06-30,2026-07-01 respectively
  AND B owns requested R99 and denied D99; A owns approved F70
  AND before = snapshot_scope([A,B,E1,E2,E3,E4,R99,D99,F70],
      relations=(A_profile.roles, B_profile.roles))
WHEN retrieve_individual_brother_history(B.brother_profile,B.id) is called
THEN bucket starts are [2026,2025,2024], totals [5,7,2] and lifetime14
  AND bucket events are [E4],[E3,E2],[E1]; neither R99/D99 nor F70 contributes
  AND E1/E2/E3/E4/R99/D99/F70, A, B and profile role relations are unchanged
  AND fixture passes matching profile and user_id despite unused brother argument
```

### PH-C21b — test_own_history_view_renders_approved_only

Parent: `PH-C21` | Operation: `PH-P05-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:98–120; SPDWEBAPP/PHILANTHROPY/views_functions.py:89–123`

```text
GIVEN ACTIVE A owns approved E hours 3 dated 2025-07-01 and requested R40/denied D50
  AND B owns approved F70; before = snapshot_scope([A,B,E,R40,D50,F70],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs /philanthropy/brother/A.id/
THEN response is 200 using philanthropy_brother_history.html
  AND academic year total and lifetime are 3, and only E is included in events
  AND R40/D50/F70 titles are absent from A's history
  AND named events, users, profile roles and session identity stay unchanged
```

### PH-C21c — test_empty_approved_history_renders_zero_and_empty_text

Parent: `PH-C21` | Operation: `PH-P05-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:98–120; SPDWEBAPP/PHILANTHROPY/views_functions.py:89–123`

```text
GIVEN ACTIVE A owns only requested E and denied F
  AND B owns approved G; before = snapshot_scope([A,B,E,F,G],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs own history and H4 helper receives A's profile/A.id
THEN response is 200 with "No philanthropy hours recorded yet."
  AND helper returns [] and 0; view lifetime_total is 0
  AND E/F/G, users, profile role relations and event count are unchanged
  AND requests retain authenticated user identity and create no persistent files
```

### PH-C21d — test_history_marks_edited_event

Parent: `PH-C21` | Operation: `PH-P05-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:98–120; SPDWEBAPP/PHILANTHROPY/views_functions.py:89–123`

```text
GIVEN ACTIVE A owns approved E with last_edited_at=2026-07-02T12:00:00Z
  AND A owns approved F with last_edited_at=null; B owns unrelated G
  AND before = snapshot_scope([A,B,E,F,G],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs own history
THEN response is 200; E's row contains [EDITED] and F's row does not
  AND displayed event titles are escaped and hours come from E/F
  AND E/F/G owner/status/hours/date/audit/editor fields are unchanged
  AND A, B and profile roles remain unchanged
```

### PH-C21e — test_history_edit_link_tracks_declared_chair_role

Parent: `PH-C21` | Operation: `PH-P05-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:98–120; SPDWEBAPP/PHILANTHROPY/views_functions.py:89–123`

```text
GIVEN A owns approved E; A has ACTIVE or ACTIVE+PHIL_CHAIR in separate fixtures
  AND B owns unrelated F; before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs own history
THEN response is 200 and is_philanthropy_chair is false or true respectively
  AND E edit link is absent for ACTIVE-only and present for the combined chair
  AND link visibility does not authorize the edit endpoint
  AND E, F, actors, role relations and event count remain unchanged
```

### PH-C22a — test_other_and_inactive_history_visibility_needs_policy

Parent: `PH-C22` | Operation: `PH-P05-H` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q5 object visibility
Source: `SPDWEBAPP/PHILANTHROPY/views.py:98–120; SPDWEBAPP/PHILANTHROPY/views_functions.py:89–123`

```text
GIVEN A has ACTIVE, B has ACTIVE, D has ALUMNI
  AND B owns approved E2, requested R_B and denied N_B
  AND D owns approved F3, requested R_D and denied N_D
  AND before = snapshot_scope([A,B,D,E2,F3,R_B,N_B,R_D,N_D],
      relations=(A_profile.roles, B_profile.roles, D_profile.roles))
WHEN A GETs B's and D's history in separate requests
THEN Q5 chooses member-wide approved history or restricted self/chair visibility
  AND denied responses must expose no target name/title/hours or event context
  AND allowed responses contain only that target's approved history, never controls
  AND E2, F3, controls, A/B/D profiles and their role relations remain unchanged
```

### PH-C22b — test_missing_target_profile_redirects_without_record_changes

Parent: `PH-C22` | Operation: `PH-P05-H` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:98–120; SPDWEBAPP/PHILANTHROPY/views_functions.py:89–123`

```text
GIVEN ACTIVE A and B exist; E is a profileless User; ID 999999 does not exist
  AND B owns unrelated F; before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs brother/E.id/ and brother/999999/ separately
THEN each response is 302 to philanthropy_dashboard with "Brother not found."
  AND neither response creates a target profile or reveals F
  AND A, B, E, F, profile roles and session user A remain unchanged
  AND requests retain authenticated user identity and create no persistent files
```

### PH-C23a — test_hours_remaining_clamps_numeric_difference

Parent: `PH-C23` | Operation: `PH-P07-T` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/templatetags/philanthropy_extras.py:5–7`

```text
GIVEN no ORM rows, sessions or files are required
WHEN hours_remaining receives pairs (10,0),(10,5),(10,10),(10,12),("10","0.5")
THEN results are exactly 10.0,5.0,0,0,9.5 respectively
  AND finite numeric strings are converted for arithmetic
  AND totals above goal do not produce negative remaining hours
  AND no DB or filesystem operation occurs
  AND fractional arithmetic does not decide event storage precision
  AND this is a SimpleTestCase design; no database fixture is required
```

### PH-C23b — test_dashboard_and_history_remaining_text_uses_tag

Parent: `PH-C23` | Operation: `PH-P07-T, PH-P04-D, PH-P05-H` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/templates/philanthropy_dashboard.html:149–154; SPDWEBAPP/PHILANTHROPY/templates/philanthropy_brother_history.html:21–26`

```text
GIVEN ACTIVE A owns approved E hours 5 in AY2025; ACTIVE B owns approved F hours10
  AND before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs dashboard?year=2025 and A's own history
THEN both responses are 200 and show A's remaining 5 hours
  AND dashboard shows B Complete without negative remaining text
  AND E, F, actors and profile role relations are unchanged
  AND no full-page HTML snapshot or mocked arithmetic is required
```

### PH-C24a — test_tag_invalid_and_nonfinite_inputs_need_contract

Parent: `PH-C24` | Operation: `PH-P07-T` | Priority: P2
Status: `POLICY_BLOCKED` | Blockers: Q10 caller preconditions versus fallback
Source: `SPDWEBAPP/PHILANTHROPY/templatetags/philanthropy_extras.py:5–7`

```text
GIVEN no DB records or filesystem resources are needed
WHEN hours_remaining(10,current) receives None,"",object(),"NaN","Infinity","-Infinity",1e309
THEN Q10 chooses controlled validation or a documented finite fallback
  AND a successful rendered result must not advertise NaN or infinite required hours
  AND source float conversion exceptions/clamping are not approved policy
  AND no DB, session or filesystem state changes
  AND this is a SimpleTestCase design; no database fixture is required
  AND no authentication session, event row or persistent file is created
```

### PH-C24b — test_negative_or_huge_tag_operands_need_contract

Parent: `PH-C24` | Operation: `PH-P07-T` | Priority: P2
Status: `POLICY_BLOCKED` | Blockers: Q10 finite operand domain
Source: `SPDWEBAPP/PHILANTHROPY/templatetags/philanthropy_extras.py:5–7`

```text
GIVEN no DB records or filesystem resources are needed
WHEN hours_remaining receives pairs (-10,0),(10,-2),(1e308,-1e308)
THEN Q10 chooses supported operands, controlled rejection or finite fallback
  AND overflow must not become an infinite member-facing hours requirement
  AND negative goal/current semantics are documented before assertions choose a value
  AND no DB, session or filesystem state changes
  AND this is a SimpleTestCase design; no database fixture is required
  AND no authentication session, event row or persistent file is created
```
