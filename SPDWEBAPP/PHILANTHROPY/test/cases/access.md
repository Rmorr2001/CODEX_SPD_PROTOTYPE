# Access, CSRF and transport

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

### PH-C01a — test_anonymous_domain_requests_require_login

Parent: `PH-C01` | Operation: `PH-P01-G, PH-P01-S, PH-P02-G, PH-P02-A, PH-P02-D, PH-P03-G, PH-P03-E, PH-P04-D, PH-P05-H, PH-P06-X` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:14–16,59–61,83–85,98–100,137–139,243–245`

```text
GIVEN A and B are synthetic ACTIVE users; B owns requested event E with hours 2
  AND client is anonymous; before = snapshot_scope([A,B,E],
      relations=(A_profile.roles, B_profile.roles))
WHEN client GETs dashboard, request, approve, E edit, A history and export routes
  AND separately POSTs request {hours:"2",event_title:"Park",event_date:"2026-07-01"}
  AND POSTs approve {event_id:E.id,action:"approve"}, then {event_id:E.id,action:"deny"}
  AND POSTs E edit {hours:"3",event_title:"Edited",event_date:"2026-07-02"}
THEN each response is 302 to named login, with next for login_required outer wrappers
  AND approve redirects to named login without next because requires_role is outermost
  AND E, A, B, profile role relations and event count are unchanged
```

### PH-C01b — test_non_active_actors_cannot_submit_or_read_member_pages

Parent: `PH-C01` | Operation: `PH-P01-G, PH-P01-S, PH-P04-D, PH-P05-H` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:14–16,59–61,98–100`

```text
GIVEN actor A has exactly one role set: (), ALUMNI, NEW_MEMBER, EXEC or PHIL_CHAIR
  AND ACTIVE B owns requested E; before = snapshot_scope([A,B,E],
      relations=(A_profile.roles, B_profile.roles))
WHEN login_actor authenticates A with no referrer
  AND A GETs dashboard, request form and A's history
  AND A POSTs request {hours:"2",event_title:"Park",event_date:"2026-07-01"}
THEN every request redirects 302 to reverse("poll") and reports missing ACTIVE
  AND no event is created; E, A, B and their roles remain unchanged
  AND the session still authenticates A
```

### PH-C01c — test_approval_requires_both_narrow_roles

Parent: `PH-C01` | Operation: `PH-P02-G, PH-P02-A, PH-P02-D` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:83–95; SPDWEBAPP/PARLEYPRO/pp_decorators.py:30–44`

```text
GIVEN A has exactly (), ACTIVE, PHIL_CHAIR, EXEC or ACTIVE+EXEC in separate fixtures
  AND B owns requested E with null decision audit; before = snapshot_scope([A,B,E],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs /philanthropy/approve/ with no referrer
  AND A separately POSTs {event_id:E.id,action:"approve"} and {event_id:E.id,action:"deny"}
THEN each response is 302 to reverse("poll") with the specific missing-role message
  AND neither ACTIVE alone nor PHIL_CHAIR alone may decide E
  AND E status, owner, title, hours, dates, approver and editor fields are unchanged
  AND event count, A/B profiles and their roles are unchanged
```

### PH-C01d — test_non_chairs_cannot_read_or_post_edit

Parent: `PH-C01` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–251`

```text
GIVEN A has exactly (), ACTIVE, ALUMNI, NEW_MEMBER, EXEC or ACTIVE+EXEC
  AND B owns requested E with hours 2; before = snapshot_scope([A,B,E],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs /philanthropy/edit/E.id/ with no referrer
  AND separately POSTs {hours:"3",event_title:"Edited",event_date:"2026-07-02"}
THEN both responses are 302 to reverse("poll") with missing PHIL_CHAIR
  AND no event is added; E including editor/time is unchanged
  AND A, B, their profile roles and session identity are unchanged
```

### PH-C01e — test_missing_profiles_are_denied_by_role_decorators

Parent: `PH-C01` | Operation: `PH-P01-G, PH-P01-S, PH-P02-G, PH-P02-A, PH-P02-D, PH-P03-G, PH-P03-E, PH-P04-D, PH-P05-H` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:14–16,59–61,83–85,98–100,243–245; SPDWEBAPP/PARLEYPRO/pp_decorators.py:46–48`

```text
GIVEN make_user(username="a",with_profile=False) creates authenticated A
  AND ACTIVE B owns requested E; before = snapshot_scope([A,B,E],
      relations=(B_profile.roles))
WHEN A GETs dashboard, request, approve, E edit and B history with no referrer
  AND POSTs request {hours:"2",event_title:"Park",event_date:"2026-07-01"}
  AND POSTs approve {event_id:E.id,action:"approve"} then action:"deny"
  AND POSTs E edit {hours:"3",event_title:"Edited",event_date:"2026-07-02"}
THEN each response is 302 to reverse("poll") with "User profile not found."
  AND no profile/event is created; A, B, E and B's role relations are unchanged
```

### PH-C01f — test_chair_without_active_edit_authority_needs_policy

Parent: `PH-C01` | Operation: `PH-P03-G, PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q3 edit roles/status/ownership
Source: `SPDWEBAPP/PHILANTHROPY/views.py:243–269`

```text
GIVEN C has only PHIL_CHAIR; B owns approved E with hours 2 and approver "Dana Chair"
  AND B owns unrelated approved F; before = snapshot_scope([C,B,E,F],
      relations=(C_profile.roles, B_profile.roles))
WHEN C GETs E edit and POSTs {hours:"3",event_title:"Edited",event_date:"2026-07-02"}
THEN Q3 chooses whether chair-only access is permitted or requires ACTIVE too
  AND if denied, response must not expose E and every E field must remain unchanged
  AND if allowed, response/changed fields follow the Q3 edit and reapproval policy
  AND B, C, profile roles and unrelated event F remain unchanged
```

### PH-C02a — test_submit_csrf_rejects_absent_or_bad_token

Parent: `PH-C02` | Operation: `PH-P01-S` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–95,243–269; SPDWEBAPP/PHILANTHROPY/templates/philanthropy_request.html:9–10`

```text
GIVEN actor A has ACTIVE; B owns requested E and unrelated approved F
  AND client = csrf_client(); login_actor(client,A); before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs /philanthropy/request/ with {hours:"2",event_title:"Park",event_date:"2026-07-01"}
  AND token is absent or csrfmiddlewaretoken:"bad-token", in separate requests
THEN each response is 403 from real CSRF middleware
  AND E and F retain owner, status, hours, title, dates, approver and editor fields
  AND event count, profiles, role relations and session user A are unchanged
  AND a real form cookie/token success request is specified in the workflow cases
```

### PH-C02b — test_approve_csrf_rejects_absent_or_bad_token

Parent: `PH-C02` | Operation: `PH-P02-A` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–95,243–269; SPDWEBAPP/PHILANTHROPY/templates/philanthropy_request.html:9–10`

```text
GIVEN actor A has ACTIVE+PHIL_CHAIR; B owns requested E and unrelated approved F
  AND client = csrf_client(); login_actor(client,A); before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs /philanthropy/approve/ with {event_id:E.id,action:"approve"}
  AND token is absent or csrfmiddlewaretoken:"bad-token", in separate requests
THEN each response is 403 from real CSRF middleware
  AND E and F retain owner, status, hours, title, dates, approver and editor fields
  AND event count, profiles, role relations and session user A are unchanged
  AND a real form cookie/token success request is specified in the workflow cases
```

### PH-C02c — test_deny_csrf_rejects_absent_or_bad_token

Parent: `PH-C02` | Operation: `PH-P02-D` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–95,243–269; SPDWEBAPP/PHILANTHROPY/templates/philanthropy_request.html:9–10`

```text
GIVEN actor A has ACTIVE+PHIL_CHAIR; B owns requested E and unrelated approved F
  AND client = csrf_client(); login_actor(client,A); before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs /philanthropy/approve/ with {event_id:E.id,action:"deny"}
  AND token is absent or csrfmiddlewaretoken:"bad-token", in separate requests
THEN each response is 403 from real CSRF middleware
  AND E and F retain owner, status, hours, title, dates, approver and editor fields
  AND event count, profiles, role relations and session user A are unchanged
  AND a real form cookie/token success request is specified in the workflow cases
```

### PH-C02d — test_edit_csrf_rejects_absent_or_bad_token

Parent: `PH-C02` | Operation: `PH-P03-E` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PHILANTHROPY/views.py:59–95,243–269; SPDWEBAPP/PHILANTHROPY/templates/philanthropy_request.html:9–10`

```text
GIVEN actor A has ACTIVE+PHIL_CHAIR; B owns requested E and unrelated approved F
  AND client = csrf_client(); login_actor(client,A); before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs /philanthropy/edit/E.id/ with {hours:"3",event_title:"Edited",event_date:"2026-07-02"}
  AND token is absent or csrfmiddlewaretoken:"bad-token", in separate requests
THEN each response is 403 from real CSRF middleware
  AND E and F retain owner, status, hours, title, dates, approver and editor fields
  AND event count, profiles, role relations and session user A are unchanged
  AND a real form cookie/token success request is specified in the workflow cases
```

### PH-C03a — test_mutation_route_other_methods_need_policy

Parent: `PH-C03` | Operation: `PH-P01-S, PH-P02-A, PH-P02-D, PH-P03-E` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q9 method allow-list
Source: `SPDWEBAPP/PHILANTHROPY/views.py:62,88,253`

```text
GIVEN A has ACTIVE+PHIL_CHAIR; B owns requested E and approved F
  AND before = snapshot_scope([A,B,E,F],
      relations=(A_profile.roles, B_profile.roles))
WHEN A uses PUT, PATCH and DELETE on request/, approve/ and edit/E.id/
  AND payload is {hours:"3",event_title:"Edited",event_date:"2026-07-02",
      event_id:E.id,action:"approve"}
THEN Q9 chooses render/no-op compatibility versus explicit 405
  AND no method may insert, change or delete E, F or another event
  AND A, B, profile roles and session identity are unchanged
```

### PH-C03b — test_read_route_post_methods_need_policy

Parent: `PH-C03` | Operation: `PH-P04-D, PH-P05-H, PH-P06-X` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q9 method allow-list; Q6 export access
Source: `SPDWEBAPP/PHILANTHROPY/views.py:16–57,100–120,139–239`

```text
GIVEN A has ACTIVE+PHIL_CHAIR; B owns approved E with hours 2
  AND before = snapshot_scope([A,B,E],
      relations=(A_profile.roles, B_profile.roles))
WHEN A POSTs dashboard, A history and export with {event_id:E.id,action:"deny"}
THEN Q9 chooses read/download compatibility versus explicit 405
  AND any returned data remains subject to Q5 history and Q6 export scope
  AND E, A, B, profile roles and event count are unchanged
  AND no file is persisted and session identity remains A
```

### PH-C03c — test_role_denial_uses_poll_without_referrer

Parent: `PH-C03` | Operation: `PH-P02-G` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:25–48`

```text
GIVEN ACTIVE A lacks PHIL_CHAIR; B owns requested E
  AND before = snapshot_scope([A,B,E],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs /philanthropy/approve/ without HTTP_REFERER
THEN response is 302 to reverse("poll")
  AND message names missing PHIL_CHAIR
  AND E, A, B, role relations and event count are unchanged
  AND the session remains authenticated as A
```

### PH-C03d — test_role_denial_uses_safe_referrer

Parent: `PH-C03` | Operation: `PH-P02-G` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:25–48`

```text
GIVEN ACTIVE A lacks PHIL_CHAIR; B owns requested E
  AND before = snapshot_scope([A,B,E],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs approve/ with HTTP_REFERER:"http://testserver/philanthropy/"
THEN response is 302 to "http://testserver/philanthropy/"
  AND message names missing PHIL_CHAIR
  AND E, A, B, role relations and event count are unchanged
  AND the session remains authenticated as A
```

### PH-C03e — test_role_denial_rejects_external_referrer

Parent: `PH-C03` | Operation: `PH-P02-G` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D1 unsafe referrer redirect; shared decorator owner AUTHENTICATE
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:38–48`

```text
GIVEN ACTIVE A lacks PHIL_CHAIR; B owns requested E
  AND before = snapshot_scope([A,B,E],
      relations=(A_profile.roles, B_profile.roles))
WHEN A GETs approve/ with HTTP_REFERER:"https://outside.invalid/landing"
THEN the denied response must not redirect to outside.invalid
  AND it must use a safe local denial destination without exposing E
  AND E, A, B, role relations and event count are unchanged
  AND session identity remains A; source currently redirects externally
```
