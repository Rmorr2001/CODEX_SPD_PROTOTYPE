# Chair edit forms, metadata and failures

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

### PH-C14a — test_edit_get_populates_form_without_audit_write

Parent: `PH-C14` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C has ACTIVE+PHIL_CHAIR and owns requested E ("Park",2,2026-07-01)
  AND E has old editor D/time T0; B owns approved F
  AND before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles))
WHEN C GETs /philanthropy/edit/E.id/
THEN response is 200 with editing:true and event E
  AND form values are "Park", 2 and "2026-07-01", with a real CSRF cookie/token
  AND E including editor/time, F, users, roles and event count are unchanged
```

### PH-C14b — test_chair_edit_field_whitelist_needs_reapproval_policy

Parent: `PH-C14` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q3 target scope and approval invalidation
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; A or B owns E in requested, approved or denied state
  AND E has submission T0, decision "Dana Chair"/T1, editor D/T1; B owns unrelated F
  AND before = snapshot_scope([A,B,C,D,E,F],
      relations=(A_profile.roles, B_profile.roles, C_profile.roles, D_profile.roles));
      at_time("2026-07-04T12:00:00Z")
  AND client = csrf_client(); login_actor(client,C)
  AND C acquired a real cookie/token from GET /philanthropy/edit/E.id/
WHEN C POSTs E edit {event_title:"Updated",hours:"3",event_date:"2026-06-30",
      user:A.id,status:"denied",philanthropy_approval_status:"denied",
      philanthropy_event_approver_name:"Forged",last_edited_by:D.id,
      philanthropy_event_submission_request_date:"2000-01-01T00:00:00Z",
      csrfmiddlewaretoken:form_token}
THEN Q3 chooses permitted statuses/owners and whether approval is invalidated
  AND permitted edits set exact title/3/date and editor C/time, then redirect to owner's history
  AND owner/submission metadata cannot be forged; decision fields follow Q3, never posted audit
  AND denied edits preserve E; F, actors, profiles and role relations remain unchanged
```

### PH-C14c — test_second_edit_needs_latest_editor_and_audit_policy

Parent: `PH-C14` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q3 edits and approval invalidation
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C and D have ACTIVE+PHIL_CHAIR; B owns E previously edited by C at T2
  AND B owns approved F; before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles))
WHEN D POSTs E edit at T3 with {event_title:"Second",hours:"4",event_date:"2026-07-03"}
THEN Q3 chooses whether E's current state can be edited and whether approval changes
  AND permitted update records D/T3 as latest editor, creates no extra event
  AND title/hours/date are exactly "Second"/4/2026-07-03
  AND E owner/submission metadata, F, actors and roles remain unchanged
  AND rejection preserves the complete prior E including C/T2
```

### PH-C15a — test_unknown_numeric_edit_target_is_404

Parent: `PH-C15` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; B owns E and unrelated F
  AND ID 999999 does not exist; before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
WHEN C GETs edit/999999/ and separately POSTs
      {event_title:"Updated",hours:"3",event_date:"2026-07-03"}
THEN both responses are 404
  AND no event is inserted or changed
  AND E/F editor and decision audit, C, B, profile roles and event count are unchanged
```

### PH-C15b — test_noninteger_edit_paths_do_not_resolve

Parent: `PH-C15` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; B owns E and unrelated F
  AND before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
WHEN C GETs or POSTs /philanthropy/edit/-1/ and /philanthropy/edit/not-an-id/
  AND POST body is {event_title:"Updated",hours:"3",event_date:"2026-07-03"}
THEN every response is 404 from routing
  AND E/F title/hours/date/editor/audit fields are unchanged
  AND C, B, profile roles and event count are unchanged
```

### PH-C15c — test_edit_missing_title_or_bad_date_is_controlled

Parent: `PH-C15` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D3 edit lacks validation/error handling; Q2 normalization; Q9 adapter
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C has ACTIVE+PHIL_CHAIR and owns requested E with old editor D/T0
  AND B owns approved F; before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles))
WHEN C POSTs {event_title:"Updated",hours:"3",event_date:"2026-07-03"}
  AND independently omits event_title/event_date or uses date "", "abc" or "2026-02-30"
THEN response must return a controlled field error without uncaught save/parse exception
  AND E title/hours/date, old editor/time, owner, status and decision audit are unchanged
  AND F, actors, profile roles and event count are unchanged
```

### PH-C16a — test_edit_prewrite_failure_preserves_entire_target

Parent: `PH-C16` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D3 uncaught edit save failure; Q9 adapter
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C has ACTIVE+PHIL_CHAIR and owns requested E with old editor D/T0
  AND B owns approved F; before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles))
  AND deliberate save failure raises RuntimeError("synthetic") before UPDATE
WHEN C POSTs E edit {event_title:"Updated",hours:"3",event_date:"2026-07-03"}
THEN response must be a controlled failure, not a server traceback or success redirect
  AND E title/hours/date, old editor/time and decision/submission metadata stay unchanged
  AND F, actors, profiles, role relations and event count remain unchanged
```

### PH-C16b — test_edit_postwrite_exception_needs_commit_policy

Parent: `PH-C16` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 rollback/committed outcome; Q3 scope; TransactionTestCase
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C has ACTIVE+PHIL_CHAIR; B owns E and unrelated approved F
  AND save wrapper UPDATEs E then raises RuntimeError("after write")
  AND before = snapshot_scope([B,C,E,F],
      relations=(B_profile.roles, C_profile.roles))
WHEN C POSTs E edit {event_title:"Updated",hours:"3",event_date:"2026-07-03"}
THEN Q8 chooses rollback with error or a reported committed result
  AND a failure must not conceal changed title/hours/date/editor fields
  AND Q3 controls decision audit preservation/invalidation
  AND E owner/submission metadata, F, users and profile role relations remain unchanged
```

### PH-C16c — test_stale_edit_and_approval_need_conflict_policy

Parent: `PH-C16` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 merge/conflict strategy; Q3 audit; PostgreSQL connections/barrier
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C and D have ACTIVE+PHIL_CHAIR on independent PostgreSQL connections
  AND B owns requested E and approved F; before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles))
WHEN C reads E for edit and pauses on a bounded barrier
  AND D approves E before C saves {event_title:"Updated",hours:"3",event_date:"2026-07-03"}
THEN Q3/Q8 choose merge, serialized update or explicit conflict
  AND a stale full-row save must not silently erase D's approval audit
  AND E decision/editor tuples stay internally consistent with the chosen outcome
  AND E owner/submission metadata, F, actors and profile roles remain unchanged
```

### PH-C16d — test_competing_edits_need_conflict_policy

Parent: `PH-C16` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 merge/conflict strategy; Q3 target scope; PostgreSQL connections/barrier
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C and D have ACTIVE+PHIL_CHAIR on independent PostgreSQL connections
  AND B owns E and approved F; before = snapshot_scope([B,C,D,E,F],
      relations=(B_profile.roles, C_profile.roles, D_profile.roles))
WHEN a bounded barrier makes C/D read E before either saves
  AND C posts {event_title:"First",hours:"3",event_date:"2026-07-03"}
  AND D posts {event_title:"Second",hours:"4",event_date:"2026-07-04"}
THEN Q8 chooses serial winner, merge or explicit conflict responses
  AND E title/hours/date/editor/time must match that choice without mixed audit
  AND E owner/submission/decision metadata follows Q3, never a silent stale overwrite
  AND F, users, profile role relations and event count remain unchanged
```
