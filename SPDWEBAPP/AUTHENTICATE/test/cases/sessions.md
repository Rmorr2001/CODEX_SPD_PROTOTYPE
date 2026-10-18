# Sessions cases

[Case index](../case-index.md) · [Inventory](../regression-spec.md) ·
[Shared fixtures](../../../../docs/testing/fixture-contract.md) · [Decisions](../decisions.md)

[Fresh actor/file fixture legend](../fixture-notes.md) applies independently to every case.

Password login submits credentials; login_actor is not login evidence.
Use distinct A/B users and client sessions. TEST_PASSWORD is the shared synthetic constant.

Every case is a design only. Refresh named rows/relations and check file bytes
separately. Unlisted fields on named A/B rows stay unchanged, including hashes,
User first_name/last_name and staff/superuser flags; admin LogEntry is asserted
only for admin writes. Compare session identity, not whole CSRF/session blobs.

<a id="auth-a01-01a"></a>

### AUTH-A01-01a — test_login_form

Parent: `AUTH-A01-01` | Operation: `AUTH-A01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN anonymous client has no authenticated identity
WHEN GET /auth/login/
THEN response is 200 using AUTHENTICATE/login.html
  AND form names are username/password and includes a CSRF token
  AND no User or profile is created; session has no user identity
```

<a id="auth-a01-01b"></a>

### AUTH-A01-01b — test_password_login_home

Parent: `AUTH-A01-01` | Operation: `AUTH-A01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN make_user(username='actor-a') has password TEST_PASSWORD
  AND anonymous session contains marker='before'; B is distinct
WHEN form POST /auth/login/ with username='actor-a', password=TEST_PASSWORD
THEN response redirects to reverse('home')
  AND session identity is A and session key differs from the anonymous key
  AND A/B User hashes, profiles and role/major relations are unchanged
```

<a id="auth-a01-01c"></a>

### AUTH-A01-01c — test_password_login_local_next

Parent: `AUTH-A01-01` | Operation: `AUTH-A01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN A has username='actor-a' and password TEST_PASSWORD
WHEN form POST /auth/login/?next=/auth/roster/%3Fx%3D1 with A credentials
THEN response redirects to /auth/roster/?x=1
  AND session identity is A
  AND A/B Users and profiles are unchanged
```

<a id="auth-a01-01d"></a>

### AUTH-A01-01d — test_password_login_without_profile

Parent: `AUTH-A01-01` | Operation: `AUTH-A01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN make_user(username='no-profile', with_profile=False) has TEST_PASSWORD
WHEN form POST /auth/login/ with username='no-profile', password=TEST_PASSWORD
THEN response redirects to reverse('home')
  AND session identity is the no-profile user
  AND no profile or role relation is created
```

<a id="auth-a01-02a"></a>

### AUTH-A01-02a — test_reject_bad_login_credentials

Parent: `AUTH-A01-02` | Operation: `AUTH-A01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN A has username='actor-a', TEST_PASSWORD; client is anonymous
  AND variants: wrong password='wrong'; empty/missing username; empty/missing password
  AND each variant starts with a fresh client and unchanged A
WHEN form POST /auth/login/ using one listed credential variant
THEN response redirects to reverse('login')
  AND message is 'Invalid username or password.' without submitted credentials
  AND session remains anonymous; A/B hashes and profiles are unchanged
```

<a id="auth-a01-02b"></a>

### AUTH-A01-02b — test_reject_inactive_login

Parent: `AUTH-A01-02` | Operation: `AUTH-A01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN make_user(username='inactive-a', is_active=False) has TEST_PASSWORD
WHEN form POST /auth/login/ with username='inactive-a', password=TEST_PASSWORD
THEN response redirects to reverse('login') with invalid-credentials message
  AND client remains anonymous
  AND inactive flag, hash and profiles are unchanged
```

<a id="auth-a01-02c"></a>

### AUTH-A01-02c — test_authenticated_login_get

Parent: `AUTH-A01-02` | Operation: `AUTH-A01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN login_actor gives client identity A; B is distinct
WHEN GET /auth/login/?next=/auth/roster/
THEN response is 200 using the login template, without redirect
  AND identity remains A
  AND A/B User and profile rows are unchanged
```

<a id="auth-a01-03a"></a>

### AUTH-A01-03a — test_reject_external_login_next

Parent: `AUTH-A01-03` | Operation: `AUTH-A01` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-REDIR](../decisions.md#f-redir); [Q-REDIR](../decisions.md#q-redir)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN A can authenticate with TEST_PASSWORD
  AND next variants: https://other.invalid/x; //other.invalid/x; %2F%2Fother.invalid/x
WHEN form POST /auth/login/ with A credentials and one next variant
THEN Location must not direct the browser to other.invalid
  AND Q-REDIR chooses local fallback versus rejection and response status
  AND A/B rows remain unchanged; decision states whether login identity is retained
```

<a id="auth-a01-04a"></a>

### AUTH-A01-04a — test_login_identity_switch

Parent: `AUTH-A01-04` | Operation: `AUTH-A01` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-LOGIN-SWITCH](../decisions.md#q-login-switch)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN client identity is A; B has username='actor-b' and TEST_PASSWORD
WHEN form POST /auth/login/ with B credentials
THEN Q-LOGIN-SWITCH chooses accepted switch with B identity or rejection retaining A
  AND response redirect/status follows that decision
  AND A/B rows and roles are unchanged
```

<a id="auth-a01-04b"></a>

### AUTH-A01-04b — test_failed_login_keeps_existing_identity

Parent: `AUTH-A01-04` | Operation: `AUTH-A01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN client identity is A; submitted username='actor-b' has password TEST_PASSWORD
WHEN form POST /auth/login/ with username='actor-b', password='wrong'
THEN response redirects to login with invalid-credentials message
  AND session identity remains A
  AND A/B hashes, profiles and roles remain unchanged
```

<a id="auth-a01-04c"></a>

### AUTH-A01-04c — test_login_other_methods

Parent: `AUTH-A01-04` | Operation: `AUTH-A01` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-LOGIN-METHOD](../decisions.md#q-login-method)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:72–91`

```text
GIVEN anonymous client has no identity
  AND methods: PUT, PATCH, DELETE
WHEN send one method to /auth/login/?next=/auth/roster/ with A credentials
THEN Q-LOGIN-METHOD chooses rendered form versus method rejection
  AND no submitted credentials authenticate and next is not followed
  AND A/B rows are unchanged
```

<a id="auth-a02-01a"></a>

### AUTH-A02-01a — test_logout_clears_current_session

Parent: `AUTH-A02-01` | Operation: `AUTH-A02` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-LOGOUT-METHOD](../decisions.md#q-logout-method)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:94–96; SPDWEBAPP/HOME/templates/HOME/navbar.html:74`

```text
GIVEN client identity is A with marker='before'; B client remains authenticated
WHEN POST /auth/logout/ with a real form CSRF token
THEN if POST retained, response is 200 HOME/home.html and A identity/marker are removed
  AND if method policy changes, assert its rejection response and retained A identity
  AND B session, A/B hashes, profiles and relations are unchanged
```

<a id="auth-a02-01b"></a>

### AUTH-A02-01b — test_repeat_logout

Parent: `AUTH-A02-01` | Operation: `AUTH-A02` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-LOGOUT-METHOD](../decisions.md#q-logout-method)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:94–96; SPDWEBAPP/HOME/templates/HOME/navbar.html:74`

```text
GIVEN client has completed logout through the method selected by Q-LOGOUT-METHOD
WHEN repeat logout with that method
THEN accepted repeat remains anonymous without creating a new authenticated identity
  AND Q-LOGOUT-METHOD selects response rendering/redirect
  AND A/B User/profile rows remain unchanged
```

<a id="auth-a02-02a"></a>

### AUTH-A02-02a — test_logout_rejects_bad_csrf

Parent: `AUTH-A02-02` | Operation: `AUTH-A02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:94–96; SPDWEBAPP/HOME/templates/HOME/navbar.html:74`

```text
GIVEN csrf_client has identity A; variants: absent token, token='invalid'
WHEN POST /auth/logout/ with one listed token variant
THEN response is 403
  AND identity and application session marker remain A/'before' when marker was set
  AND A/B hashes and profiles remain unchanged
```

<a id="auth-a02-02b"></a>

### AUTH-A02-02b — test_cross_site_get_logout

Parent: `AUTH-A02-02` | Operation: `AUTH-A02` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-LOGOUT-METHOD](../decisions.md#q-logout-method)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:94–96; SPDWEBAPP/HOME/templates/HOME/navbar.html:74`

```text
GIVEN A is authenticated; navigation originates at https://other.invalid/
WHEN GET /auth/logout/ with external Referer
THEN Q-LOGOUT-METHOD chooses removal of GET mutation or explicit retained behavior
  AND if GET rejected, A session must remain authenticated
  AND A/B User hashes, profiles and B session remain unchanged
```

<a id="auth-a03-01a"></a>

### AUTH-A03-01a — test_password_change_keeps_current_session

Parent: `AUTH-A03-01` | Operation: `AUTH-A03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN A has TEST_PASSWORD; C1 authenticated through credentials; B has another session
  AND A role variants: (), ACTIVE, EXEC, EXEC+ACTIVE, PHIL_CHAIR+ACTIVE, NEW_MEMBER, ALUMNI
WHEN C1 JSON POST /auth/change-password/ with current_password=TEST_PASSWORD
  AND and new_password1=new_password2='Replacement-22!word'
THEN response is 200 JSON {success:true}
  AND fresh A hash accepts replacement and rejects TEST_PASSWORD
  AND C1 GET /auth/profile/ is 200 with A identity; B session/rows unchanged
```

<a id="auth-a03-01b"></a>

### AUTH-A03-01b — test_password_change_invalidates_other_session

Parent: `AUTH-A03-01` | Operation: `AUTH-A03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN A authenticated through credentials in C1 and C2; B is separate
WHEN C1 changes password from TEST_PASSWORD to 'Replacement-22!word'
  AND C2 then GETs /auth/profile/
THEN change response is 200 JSON {success:true}; C2 redirects to login
  AND C1 identity remains A; C2 loses authenticated identity
  AND A/B profiles, roles and majors are unchanged
```

<a id="auth-a03-02a"></a>

### AUTH-A03-02a — test_wrong_current_password

Parent: `AUTH-A03-02` | Operation: `AUTH-A03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN A has TEST_PASSWORD and current authenticated session
WHEN JSON POST /auth/change-password/ with current_password='wrong'
  AND and new_password1=new_password2='Replacement-22!word'
THEN response is 200 JSON success=false, error='Current password is incorrect.'
  AND A hash still accepts TEST_PASSWORD; session identity remains A
  AND A/B profiles and all B fields remain unchanged
```

<a id="auth-a03-02b"></a>

### AUTH-A03-02b — test_password_confirmation_mismatch

Parent: `AUTH-A03-02` | Operation: `AUTH-A03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN A has TEST_PASSWORD and current session
WHEN JSON POST /auth/change-password/ with current_password=TEST_PASSWORD
  AND and new_password1='Replacement-22!word', new_password2='different'
THEN response is 200 JSON success=false, error='New passwords do not match.'
  AND A hash and current identity are unchanged
  AND A/B profiles, roles and majors are unchanged
```

<a id="auth-a03-02c"></a>

### AUTH-A03-02c — test_password_nonpost_policy

Parent: `AUTH-A03-02` | Operation: `AUTH-A03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-PASSWORD-METHOD](../decisions.md#q-password-method)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN A is authenticated; methods: GET, PUT, PATCH, DELETE
WHEN send listed method to /auth/change-password/
THEN Q-PASSWORD-METHOD chooses legacy 200 false/'Invalid request method.' or 405
  AND password hash and session identity remain unchanged
  AND A/B profile and role/major relations remain unchanged
```

<a id="auth-a03-03a"></a>

### AUTH-A03-03a — test_password_malformed_json

Parent: `AUTH-A03-03` | Operation: `AUTH-A03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-PARSE](../decisions.md#f-parse); [Q-PARSE](../decisions.md#q-parse); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN A is authenticated with TEST_PASSWORD
  AND bodies: '{', '[]', 'null'; Content-Type application/json
WHEN POST each body independently to /auth/change-password/
THEN controlled non-success has schema/status chosen by Q-PARSE/Q-ERROR
  AND hash remains usable and accepts TEST_PASSWORD; identity remains A
  AND A/B profile rows remain unchanged
```

<a id="auth-a03-03b"></a>

### AUTH-A03-03b — test_password_missing_or_wrong_type_fields

Parent: `AUTH-A03-03` | Operation: `AUTH-A03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-PARSE](../decisions.md#f-parse); [Q-PARSE](../decisions.md#q-parse); [Q-PASSWORD](../decisions.md#q-password)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN A is authenticated with TEST_PASSWORD
  AND variants: missing current_password; missing both new fields; new values null, 7, []
  AND other fields use current_password=TEST_PASSWORD and matching replacement strings
WHEN JSON POST one variant to /auth/change-password/
THEN malformed input cannot set an unusable hash or partially change the password
  AND Q-PARSE chooses field errors/status; matching-null case exposes current defect
  AND A retains old hash/session; B and profiles remain unchanged
```

<a id="auth-a03-03c"></a>

### AUTH-A03-03c — test_password_empty_or_oversized_boundary

Parent: `AUTH-A03-03` | Operation: `AUTH-A03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-PASSWORD](../decisions.md#q-password); [Q-PARSE](../decisions.md#q-parse)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN A is authenticated with TEST_PASSWORD
  AND new values: ''; '   '; string at chosen request limit; string one above that limit
WHEN JSON POST current_password=TEST_PASSWORD and matching listed new values
THEN Q-PASSWORD/Q-PARSE must first define empty/whitespace/request-length outcomes
  AND rejected input leaves hash and session unchanged; accepted input hashes exact chosen value
  AND B/profile/role rows remain unchanged
```

<a id="auth-a03-04a"></a>

### AUTH-A03-04a — test_password_reuse_strength_whitespace

Parent: `AUTH-A03-04` | Operation: `AUTH-A03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-PASSWORD](../decisions.md#q-password)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN A has TEST_PASSWORD; each subcase starts from the original hash
  AND new values: TEST_PASSWORD; 'password'; ' Replacement-22!word '
WHEN JSON POST correct current_password and matching listed new values
THEN Q-PASSWORD decides reuse, configured validator enforcement and whitespace semantics
  AND accepted value authenticates exactly as that rule defines; rejected input keeps old hash
  AND A identity and B/profile/roles remain unchanged
```

<a id="auth-a03-04b"></a>

### AUTH-A03-04b — test_password_user_save_failure

Parent: `AUTH-A03-04` | Operation: `AUTH-A03` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN A is authenticated with TEST_PASSWORD
  AND inject User.save failure before its database write
WHEN JSON POST correct current_password and matching 'Replacement-22!word' values
THEN Q-ERROR chooses controlled failure status/schema
  AND fresh A hash still accepts TEST_PASSWORD and current session remains usable
  AND B Users/profiles and A profile/roles/majors remain unchanged
```

<a id="auth-a03-01c"></a>

### AUTH-A03-01c — test_password_change_without_profile

Parent: `AUTH-A03-01` | Operation: `AUTH-A03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:99–123`

```text
GIVEN make_user(username='no-profile', with_profile=False) has TEST_PASSWORD
  AND client authenticated by password credentials; B has a profile
WHEN JSON POST /auth/change-password/ with current_password=TEST_PASSWORD
  AND and new_password1=new_password2='Replacement-22!word'
THEN response is 200 JSON success=true
  AND fresh hash validates replacement; session identity remains no-profile user
  AND no profile created; B and all roles/major relations unchanged
```
