# Demo cases

[Case index](../case-index.md) · [Inventory](../regression-spec.md) ·
[Shared fixtures](../../../../docs/testing/fixture-contract.md) · [Decisions](../decisions.md)

[Fresh actor/file fixture legend](../fixture-notes.md) applies independently to every case.

Use demo settings and HTTPS for secure cookie requests. Persona fixtures are
thin local ORM/group setup, not the executive seed command. Groups are railway-demo:demo-executive, railway-demo:demo-active,
railway-demo:demo-newmember and railway-demo:demo-alumni.

Every case is a design only. Refresh named rows/relations and check file bytes
separately. Unlisted fields on named A/B rows stay unchanged, including hashes,
User first_name/last_name and staff/superuser flags; admin LogEntry is asserted
only for admin writes. Compare session identity, not whole CSRF/session blobs.

<a id="auth-d01-01a"></a>

### AUTH-D01-01a — test_demo_persona_entry_identity

Parent: `AUTH-D01-01` | Operation: `AUTH-D01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN demo settings; four local users have unusable passwords, active/nonstaff/nonsuperuser
  AND groups: railway-demo:demo-executive/active/newmember/alumni respectively
  AND profiles explicitly have EXEC+ACTIVE, ACTIVE, NEW_MEMBER, ALUMNI
  AND persona variants: executive, active, newmember, alumni
WHEN HTTPS form POST /demo/enter/ with one persona and real CSRF token
THEN response redirects alumni to reverse('alumni_roster'), others reverse('dashboard')
  AND session identity is the sole corresponding group member
  AND User hashes/flags/groups/profiles/roles and B state remain unchanged
```

<a id="auth-d01-01b"></a>

### AUTH-D01-01b — test_demo_default_persona

Parent: `AUTH-D01-01` | Operation: `AUTH-D01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN demo mode; only seeded-style executive group member E exists
  AND E active, password=None, nonstaff/nonsuperuser; profile EXEC+ACTIVE
WHEN HTTPS form POST /demo/enter/ without persona, with real CSRF token
THEN response redirects dashboard; session identity is E
  AND no User/group/profile row is created
  AND E flags/unusable hash/roles and B rows remain unchanged
```

<a id="auth-d01-01c"></a>

### AUTH-D01-01c — test_demo_entry_after_username_change

Parent: `AUTH-D01-01` | Operation: `AUTH-D01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN eligible active persona member originally username='demo-active'
  AND change only username to 'renamed-active'; original railway-demo:demo-active group retained
WHEN HTTPS form POST /demo/enter/ with persona='active'
THEN response redirects dashboard; identity is the same group member PK
  AND no username-based replacement account is selected or created
  AND groups, flags, hashes, profile roles and B rows remain unchanged
```

<a id="auth-d01-01d"></a>

### AUTH-D01-01d — test_demo_newmember_dashboard_redirect

Parent: `AUTH-D01-01` | Operation: `AUTH-D01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN eligible demo-newmember group member has only NEW_MEMBER role
  AND client entered with persona='newmember'
WHEN HTTPS GET /auth/dashboard/ without following redirect
THEN response redirects /newmember/
  AND session identity stays newmember user
  AND User/profile/group/role/major rows and files remain unchanged
```

<a id="auth-d01-02a"></a>

### AUTH-D01-02a — test_demo_entry_post_only

Parent: `AUTH-D01-02` | Operation: `AUTH-D01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN demo mode; client anonymous or already A; mode variants True and False
WHEN HTTPS GET /demo/enter/
THEN response is 405 with POST in Allow header, before mode branch
  AND session identity stays anonymous/A respectively
  AND no User/group/profile/role/file changes
```

<a id="auth-d01-02b"></a>

### AUTH-D01-02b — test_demo_unknown_persona

Parent: `AUTH-D01-02` | Operation: `AUTH-D01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN demo mode; eligible executive exists; A identity or anonymous
  AND persona variants: 'unknown', ''
WHEN HTTPS form POST /demo/enter/ with one listed persona and real token
THEN response is 400 body 'Unknown demo persona.'
  AND no fallback executive login; prior identity remains
  AND User/groups/profiles/roles/files unchanged
```

<a id="auth-d01-02c"></a>

### AUTH-D01-02c — test_demo_entry_disabled

Parent: `AUTH-D01-02` | Operation: `AUTH-D01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN DEMO_MODE=False; eligible group member exists; client identity A
WHEN HTTPS form POST /demo/enter/ with persona='active' and real CSRF token
THEN response is 404
  AND identity remains A
  AND all Users/groups/profiles/roles/majors/files unchanged
```

<a id="auth-d01-02d"></a>

### AUTH-D01-02d — test_demo_json_content_type_policy

Parent: `AUTH-D01-02` | Operation: `AUTH-D01` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-DEMO](../decisions.md#q-demo)
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN demo mode; eligible executive/active group members exist; client identity A
WHEN HTTPS JSON POST /demo/enter/ with {persona:'active'} and real token
THEN Q-DEMO chooses form-only rejection versus explicit JSON support
  AND JSON must not surprise-login executive because request.POST is empty
  AND response and identity follow selected rule; no ORM/file writes
```

<a id="auth-d01-03a"></a>

### AUTH-D01-03a — test_demo_ineligible_account_rejected

Parent: `AUTH-D01-03` | Operation: `AUTH-D01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN demo mode; only one active persona group member at most
  AND variants: no member; inactive; is_staff=True; is_superuser=True; usable TEST_PASSWORD
  AND each variant isolated; client identity A
WHEN HTTPS form POST persona='active' with real token
THEN response is 503 body 'The demo account is not ready.'
  AND session identity remains A; no privileged/unseeded account login
  AND all group/flag/hash/profile/role rows remain unchanged
```

<a id="auth-d01-03b"></a>

### AUTH-D01-03b — test_demo_group_membership_trust_policy

Parent: `AUTH-D01-03` | Operation: `AUTH-D01` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-DEMO](../decisions.md#q-demo)
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN two otherwise eligible unusable-password users belong to active persona group
  AND one has unrelated username/roles; also test missing-profile member independently
WHEN HTTPS form POST persona='active' with real token
THEN Q-DEMO defines trusted membership, multiplicity and profile/role consistency
  AND do not accept arbitrary .first identity without that rule
  AND no automatic role/profile creation or privileged login; B rows unchanged
```

<a id="auth-d01-04a"></a>

### AUTH-D01-04a — test_demo_csrf_rejects_absent_and_bad_tokens

Parent: `AUTH-D01-04` | Operation: `AUTH-D01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN csrf_client uses HTTPS, identity anonymous or A
  AND eligible active persona exists; variants absent token and 'invalid' token
WHEN HTTPS form POST /demo/enter/ with persona='active' and listed token
THEN response is 403; no persona login
  AND prior session identity remains anonymous/A respectively
  AND User/group/profile/role/major/file state unchanged
```

<a id="auth-d01-04b"></a>

### AUTH-D01-04b — test_demo_csrf_accepts_token_and_rotates_identity

Parent: `AUTH-D01-04` | Operation: `AUTH-D01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/views.py:8–23; SPDWEBAPP/railway_demo/settings.py:16–37`

```text
GIVEN csrf_client identity A; capture session key
  AND HTTPS GET /auth/login/ yields actual cookie/form token
  AND eligible active group member E is distinct from A
WHEN HTTPS form POST /demo/enter/ with persona='active' and matching cookie/form token
THEN response redirects dashboard; identity is E; session key differs
  AND E remains nonstaff/nonsuperuser with unusable password
  AND A/B/E User/profile/group/role/major state unchanged
```

<a id="auth-d03-01a"></a>

### AUTH-D03-01a — test_demo_admin_http_boundary

Parent: `AUTH-D03-01` | Operation: `AUTH-D03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/middleware.py:4–12; SPDWEBAPP/SPDWEBAPP_CORE/urls.py:25`

```text
GIVEN demo mode; actors anonymous, nonstaff, staff, superuser
  AND paths /admin/ and /admin/auth/user/; methods GET and CSRF-token POST
WHEN send each actor/path/method request after obtaining token where needed
THEN response is 403 JSON error='Admin is unavailable on the public demo.'
  AND no admin template or redirect; no LogEntry or ORM write
  AND session identity and all named User/profile/role/file state unchanged
```

<a id="auth-d03-01b"></a>

### AUTH-D03-01b — test_demo_admin_middleware_short_circuit

Parent: `AUTH-D03-01` | Operation: `AUTH-D03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/middleware.py:4–12; SPDWEBAPP/SPDWEBAPP_CORE/urls.py:25`

```text
GIVEN DemoBoundaryMiddleware wraps a sentinel that records calls
  AND request path /admin/ or /admin/auth/user/; no outer CSRF middleware
WHEN invoke middleware with request method GET/POST/PUT/DELETE
THEN response is 403 JSON public-demo error
  AND sentinel is never called even for unsafe methods
  AND no ORM, file or identity mutation
```

<a id="auth-d03-02a"></a>

### AUTH-D03-02a — test_demo_custom_admin_prefix

Parent: `AUTH-D03-02` | Operation: `AUTH-D03` | Priority: P0
Status: `NEEDS_FIX` | Blockers: [F-ADMIN-PREFIX](../decisions.md#f-admin-prefix)
Source: `SPDWEBAPP/railway_demo/middleware.py:4–12; SPDWEBAPP/SPDWEBAPP_CORE/urls.py:25`

```text
GIVEN demo settings mount actual admin at /control/ instead of /admin/
  AND A superuser has no app roles; B is admin-visible target
WHEN A HTTPS GETs /control/ and /control/auth/user/
THEN response is 403 JSON public-demo error, with no admin HTML/data
  AND boundary must apply to mounted admin prefix, not only hardcoded /admin/
  AND no admin read exposure, ORM/LogEntry/file or identity change
```

<a id="auth-d03-02b"></a>

### AUTH-D03-02b — test_demo_prefix_edge_paths

Parent: `AUTH-D03-02` | Operation: `AUTH-D03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-ADMIN](../decisions.md#q-admin)
Source: `SPDWEBAPP/railway_demo/middleware.py:4–12; SPDWEBAPP/SPDWEBAPP_CORE/urls.py:25`

```text
GIVEN demo admin configured at /admin/; paths /admin and /administrator/
  AND caller identity A; unrelated resolver behavior remains real
WHEN HTTPS GET each edge path
THEN Q-ADMIN defines slashless admin handling and non-admin prefix exclusion
  AND actual admin cannot be exposed; unrelated /administrator/ must follow resolver
  AND no User/profile/LogEntry/file/identity mutation
```
