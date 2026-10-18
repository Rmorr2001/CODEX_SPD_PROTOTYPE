# Cross-operation approved projections

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

### PH-C33a — test_submit_then_approve_updates_all_approved_projections_once

Parent: `PH-C33` | Operation: `PH-P01-S, PH-P02-A, PH-P04-D, PH-P04-H, PH-P05-H, PH-P06-X` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:14–120,137–239`

```text
GIVEN ACTIVE A/B exist; C has ACTIVE+PHIL_CHAIR; B owns approved F hours7 in AY2026
  AND before = snapshot_scope([A,B,C,F],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles))
WHEN A submits {hours:"2",event_title:"Park",event_date:"2026-07-01"}
THEN response302 creates requested E; own dashboard includes E but approved own/history totals are0
  AND C's parsed export contains F but not E
WHEN C POSTs approve {event_id:E.id,action:"approve"} at T1
THEN response200; A dashboard/history totals are2 and chapter approved total9
  AND C's parsed export contains E exactly once with numeric2 and total2 for A
  AND E owner/title/hours/date/submission/editor fields, F, actors and roles stay unchanged
```

### PH-C33b — test_cross_year_edit_projection_requires_approval_policy

Parent: `PH-C33` | Operation: `PH-P03-E, PH-P04-D, PH-P05-H, PH-P06-X` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q3 approval invalidation and edit scope; Q6 export scope
Source: `SPDWEBAPP/PHILANTHROPY/views.py:14–120,137–269`

```text
GIVEN ACTIVE A owns approved E hours2 dated 2026-07-01; B owns approved F7
  AND C has ACTIVE+PHIL_CHAIR; E has original submission T0 and decision audit T1
  AND before = snapshot_scope([A,B,C,E,F],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles))
WHEN C edits E {hours:"3",event_title:"Moved",event_date:"2026-06-30"} at T2
THEN Q3 chooses retained approval or reset-to-requested and matching response
  AND if still approved, AY2025 gains3, AY2026 loses2 and A lifetime/export reflect3
  AND if reset, approved projections exclude E; Q6 controls which export year is requested
  AND E owner/submission time, F, users and profile role relations stay unchanged
```

### PH-C33c — test_reversed_decision_projections_need_transition_policy

Parent: `PH-C33` | Operation: `PH-P02-D, PH-P04-D, PH-P05-H, PH-P06-X` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q4 reverse decision; Q6 export scope
Source: `SPDWEBAPP/PHILANTHROPY/views.py:14–120,137–239`

```text
GIVEN ACTIVE A owns approved E hours2 in AY2026; B owns approved F7
  AND C has ACTIVE+PHIL_CHAIR; E audit identifies previous approver D at T1
  AND before = snapshot_scope([A,B,C,E,F],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles))
WHEN C POSTs approve {event_id:E.id,action:"deny"} at T2
THEN Q4 chooses allowed reversal or rejection and matching audit response
  AND allowed denial removes E from approved dashboard/history/export but retains own event row
  AND rejected reversal preserves E audit and every approved projection
  AND E owner/title/hours/date/submission/editor fields, F, actors and roles are unchanged
```
