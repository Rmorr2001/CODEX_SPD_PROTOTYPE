# Pending review, decisions and audit

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

### PH-C09a — test_pending_list_contains_only_requested_rows_by_date

Parent: `PH-C09` | Operation: `PH-P02-G` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:83–95`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; ACTIVE A owns requested E dated 2026-07-01
  AND ACTIVE B owns requested F dated 2026-07-02, approved G and denied H
  AND before = snapshot_scope([A,B,C,E,F,G,H],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles))
WHEN C GETs /philanthropy/approve/
THEN response is 200 with pending_requests exactly [F,E]
  AND G and H do not appear; displayed names/titles/hours belong to F and E
  AND E, F, G, H, user/profile rows and role relations remain unchanged
```

### PH-C09b — test_initial_approval_updates_only_decision_fields

Parent: `PH-C09` | Operation: `PH-P02-A` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C has ACTIVE+PHIL_CHAIR with profile name "Casey Chair"; B owns requested E
  AND E is ("Park",2,2026-07-01), has submission time T0 and null decision/editor fields
  AND B owns unrelated F; before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
  AND at_time("2026-07-02T12:00:00Z"); client = csrf_client(); login_actor(client,C)
  AND C acquired a real cookie/token from GET /philanthropy/approve/
WHEN C POSTs approve/ with {event_id:E.id,action:"approve",csrfmiddlewaretoken:form_token}
THEN response is 200 with approval success; pending_requests excludes E
  AND E becomes approved with approver "Casey Chair" and decision time 2026-07-02T12:00:00Z
  AND E owner/title/hours/event date/submission time/editor fields are unchanged
  AND F, B, C and profile roles stay unchanged; event and admin LogEntry counts do not grow
```

### PH-C10a — test_initial_denial_updates_only_decision_fields

Parent: `PH-C10` | Operation: `PH-P02-D` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C has ACTIVE+PHIL_CHAIR with profile name "Casey Chair"; B owns requested E
  AND E is ("Park",2,2026-07-01), has submission time T0 and null decision/editor fields
  AND B owns unrelated F; before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
  AND at_time("2026-07-02T12:00:00Z"); client = csrf_client(); login_actor(client,C)
  AND C acquired a real cookie/token from GET /philanthropy/approve/
WHEN C POSTs approve/ with {event_id:E.id,action:"deny",csrfmiddlewaretoken:form_token}
THEN response is 200 with denial success; pending_requests excludes E
  AND E becomes denied with approver "Casey Chair" and decision time 2026-07-02T12:00:00Z
  AND E owner/title/hours/event date/submission time/editor fields are unchanged
  AND F, B, C and profile roles stay unchanged; no event or admin LogEntry is added
```

### PH-C10b — test_denied_event_remains_personal_but_not_approved_history

Parent: `PH-C10` | Operation: `PH-P04-D, PH-P04-H, PH-P05-H` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:14–57,98–120; SPDWEBAPP/PHILANTHROPY/views_functions.py:22–61,96–123`

```text
GIVEN ACTIVE B owns denied E hours 2 dated 2026-07-01 and approved F hours 3 same AY
  AND ACTIVE A owns approved G hours 7; before = snapshot_scope([A,B,E,F,G],
      relations=(A_profile.roles, B_profile.roles))
WHEN B GETs dashboard?year=2026 and B's own history
  AND get_user_events_and_total_hours uses B and (2026-07-01,2027-06-30)
THEN both responses are 200; own dashboard includes denied E and approved F
  AND personal approved total is 3; own history contains only F and lifetime is 3
  AND chapter approved total is 10, excluding E
  AND E, F, G, users, profile roles and session user B remain unchanged
```

### PH-C11a — test_bad_decision_event_ids_report_error_without_write

Parent: `PH-C11` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; ACTIVE B owns requested E and approved F
  AND numeric ID 999999 does not exist; before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
WHEN C POSTs approve/ with action:"approve" or action:"deny" independently
  AND event_id is omitted, "", "abc" or "999999" in separate requests
THEN response is 200 with an error, not a decision success
  AND pending list retains E; nonexistent numeric ID reports "Event not found"
  AND E/F audit and event count, users, profile roles and session user C are unchanged
```

### PH-C11b — test_unknown_decision_action_cannot_report_success

Parent: `PH-C11` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D5 unknown action falsely saves/reports denial
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; B owns requested E and unrelated approved F
  AND before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
WHEN C POSTs approve/ with event_id:E.id
  AND action is omitted, "", "bogus", "pending" or "requested"
THEN response must report invalid action without approval or denial success
  AND E remains requested with original audit/editor/title/hours/date/owner fields
  AND no save signal is emitted for E and no admin LogEntry is created
  AND F, actors, roles and event count stay unchanged; source currently falsely says denied
```

### PH-C11c — test_decision_helper_nonpost_is_noop

Parent: `PH-C11` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; B owns requested E and approved F
  AND before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
WHEN philanthropy_approval_POST receives a GET RequestFactory request for C
  AND request.GET is {event_id:E.id,action:"approve"}
THEN helper returns None without adding success/error messages
  AND E stays requested with original audit/editor fields
  AND F, C, B, role relations and event count are unchanged
```

### PH-C11d — test_direct_decision_callable_needs_authorization_boundary

Parent: `PH-C11` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D6 callable trusts request without role check; domain boundary repair
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN A has ACTIVE only; B owns requested E and approved F
  AND before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN the future protected decision callable receives A and {event_id:E.id,action:"approve"}
THEN it must reject the actor lacking PHIL_CHAIR without changing E
  AND no approval audit or success is created; F, actors and roles are unchanged
  AND current philanthropy_approval_POST can perform that write when called directly
  AND the request wrapper's C01c denial must remain independent evidence
```

### PH-C12a — test_approved_to_approve_requires_transition_policy

Parent: `PH-C12` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q4 repeated/reverse transition and audit semantics
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C and D each have ACTIVE+PHIL_CHAIR; B owns approved E
  AND E decision audit is "Dana Chair"/2026-07-02T12:00:00Z; unrelated F belongs to B
  AND before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles));
      at_time("2026-07-03T12:00:00Z")
WHEN C POSTs approve/ with {event_id:E.id,action:"approve"}
THEN Q4 chooses forbidden, idempotent or allowed transition and matching response
  AND forbidden/no-op leaves E decision status/name/time exactly unchanged
  AND allowed transition changes only agreed status/audit fields with matching actor/time
  AND E owner/title/hours/date/submission/editor fields, F, actors and roles are unchanged
```

### PH-C12b — test_denied_to_deny_requires_transition_policy

Parent: `PH-C12` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q4 repeated/reverse transition and audit semantics
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C and D each have ACTIVE+PHIL_CHAIR; B owns denied E
  AND E decision audit is "Dana Chair"/2026-07-02T12:00:00Z; unrelated F belongs to B
  AND before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles));
      at_time("2026-07-03T12:00:00Z")
WHEN C POSTs approve/ with {event_id:E.id,action:"deny"}
THEN Q4 chooses forbidden, idempotent or allowed transition and matching response
  AND forbidden/no-op leaves E decision status/name/time exactly unchanged
  AND allowed transition changes only agreed status/audit fields with matching actor/time
  AND E owner/title/hours/date/submission/editor fields, F, actors and roles are unchanged
```

### PH-C12c — test_approved_to_deny_requires_transition_policy

Parent: `PH-C12` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q4 repeated/reverse transition and audit semantics
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C and D each have ACTIVE+PHIL_CHAIR; B owns approved E
  AND E decision audit is "Dana Chair"/2026-07-02T12:00:00Z; unrelated F belongs to B
  AND before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles));
      at_time("2026-07-03T12:00:00Z")
WHEN C POSTs approve/ with {event_id:E.id,action:"deny"}
THEN Q4 chooses forbidden, idempotent or allowed transition and matching response
  AND forbidden/no-op leaves E decision status/name/time exactly unchanged
  AND allowed transition changes only agreed status/audit fields with matching actor/time
  AND E owner/title/hours/date/submission/editor fields, F, actors and roles are unchanged
```

### PH-C12d — test_denied_to_approve_requires_transition_policy

Parent: `PH-C12` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q4 repeated/reverse transition and audit semantics
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C and D each have ACTIVE+PHIL_CHAIR; B owns denied E
  AND E decision audit is "Dana Chair"/2026-07-02T12:00:00Z; unrelated F belongs to B
  AND before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles));
      at_time("2026-07-03T12:00:00Z")
WHEN C POSTs approve/ with {event_id:E.id,action:"approve"}
THEN Q4 chooses forbidden, idempotent or allowed transition and matching response
  AND forbidden/no-op leaves E decision status/name/time exactly unchanged
  AND allowed transition changes only agreed status/audit fields with matching actor/time
  AND E owner/title/hours/date/submission/editor fields, F, actors and roles are unchanged
```

### PH-C12e — test_self_approve_requires_review_policy

Parent: `PH-C12` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q4 self-review and audit
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C has ACTIVE+PHIL_CHAIR and owns requested E with no decision audit
  AND B owns approved F; before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
WHEN C POSTs approve/ with {event_id:E.id,action:"approve"}
THEN Q4 chooses whether self-approve is permitted or rejected
  AND rejected action leaves E requested with null decision fields
  AND permitted action records only status and C's matching display-name/time audit
  AND E owner/title/hours/date/submission/editor fields, F, C and B remain unchanged
```

### PH-C12f — test_self_deny_requires_review_policy

Parent: `PH-C12` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q4 self-review and audit
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C has ACTIVE+PHIL_CHAIR and owns requested E with no decision audit
  AND B owns approved F; before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
WHEN C POSTs approve/ with {event_id:E.id,action:"deny"}
THEN Q4 chooses whether self-deny is permitted or rejected
  AND rejected action leaves E requested with null decision fields
  AND permitted action records only status and C's matching display-name/time audit
  AND E owner/title/hours/date/submission/editor fields, F, C and B remain unchanged
```

### PH-C13a — test_decision_prewrite_save_failure_preserves_request

Parent: `PH-C13` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; B owns requested E and approved F
  AND before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
  AND a deliberate save failure raises RuntimeError("synthetic") before UPDATE
WHEN C POSTs {event_id:E.id,action:"approve"} or separately action:"deny"
THEN response is 200 with an error and no decision success
  AND E remains in pending_requests with every persisted field unchanged
  AND F, actors, profile roles and event count are unchanged
```

### PH-C13b — test_decision_postwrite_exception_needs_commit_policy

Parent: `PH-C13` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 error-after-write outcome; TransactionTestCase
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; B owns requested E and approved F
  AND save wrapper UPDATEs E then raises RuntimeError("after write")
  AND before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
WHEN C POSTs {event_id:E.id,action:"approve"} or separately action:"deny"
THEN Q8 chooses rollback/error or committed success with recoverable result
  AND an error must not conceal an unreported persisted decision
  AND final E decision status/name/time must agree with the chosen result
  AND E owner/title/hours/date/submission/editor fields, F, actors and roles are unchanged
```

### PH-C13c — test_competing_approve_and_deny_need_conflict_policy

Parent: `PH-C13` | Operation: `PH-P02-A, PH-P02-D` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q4 winner/transition rule; Q8 locking/version rule; PostgreSQL connections/barrier
Source: `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`

```text
GIVEN PostgreSQL independent connections for C and D, both ACTIVE+PHIL_CHAIR
  AND B owns requested E and approved F; before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles))
WHEN a bounded barrier pauses both after reading E
  AND C submits action:"approve" while D submits action:"deny" for event_id:E.id
THEN Q4/Q8 choose serial winner or explicit conflict, with matching response outcomes
  AND final E status, approver and decision timestamp describe one consistent decision
  AND no mixed audit or silently lost decision is accepted under the chosen policy
  AND E nondecision fields, F, actors and profile roles remain unchanged
```
