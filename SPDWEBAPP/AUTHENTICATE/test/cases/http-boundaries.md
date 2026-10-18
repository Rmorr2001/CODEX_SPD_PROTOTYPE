# Http Boundaries cases

[Case index](../case-index.md) · [Inventory](../regression-spec.md) ·
[Shared fixtures](../../../../docs/testing/fixture-contract.md) · [Decisions](../decisions.md)

[Fresh actor/file fixture legend](../fixture-notes.md) applies independently to every case.

Shared denial/CSRF checks live here; workflows own accepted business effects.
P is form payload username="updated-a", email="updated@example.invalid",
firstName="Alex", lastName="Example", hometown="Columbia", pclass="Alpha".
A/B are distinct users. Password JSON names are current_password, new_password1,
new_password2, with TEST_PASSWORD and matching Replacement-22!word values.

Every case is a design only. Refresh named rows/relations and check file bytes
separately. Unlisted fields on named A/B rows stay unchanged, including hashes,
User first_name/last_name and staff/superuser flags; admin LogEntry is asserted
only for admin writes. Compare session identity, not whole CSRF/session blobs.

<a id="auth-s01a"></a>

### AUTH-S01a — test_anonymous_protected_routes

Parent: `AUTH-S01` | Operation: `AUTH-S01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/urls.py:4–17; SPDWEBAPP/AUTHENTICATE/views.py:26–305`

```text
GIVEN anonymous client; A/B rows/roles/majors and temporary files captured
  AND paths: dashboard, roster, alumni_roster, profile, change-password, update_profile
  AND also update_photo, reset-photo, update_majors, add-custom-major (all under /auth/)
WHEN GET each path with trailing slash
THEN response redirects LOGIN_URL with the requested path encoded as next
  AND client stays anonymous; no business body exposes A/B profile data
  AND A/B Users/profiles/relations/catalog/files remain unchanged
```

<a id="auth-s01b"></a>

### AUTH-S01b — test_anonymous_protected_post_routes

Parent: `AUTH-S01` | Operation: `AUTH-S01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/urls.py:4–17; SPDWEBAPP/AUTHENTICATE/views.py:26–305`

```text
GIVEN anonymous client; real token from login page
  AND payloads: change-password JSON current_password=TEST_PASSWORD
  AND new_password1=new_password2='Replacement-22!word'; update_profile form P
  AND update_photo multipart 40x40 PNG; reset-photo form {}; update_majors JSON {majors:[]}
  AND add-custom-major JSON {major_name:'Astronomy'}
WHEN POST each named /auth/ route with its stated payload and CSRF token
THEN response redirects to login with next; no business mutation occurs
  AND no password/profile/catalog/M2M/file writes; no uploaded orphan bytes
  AND anonymous identity and A/B state remain unchanged
```

<a id="auth-s01c"></a>

### AUTH-S01c — test_own_mutations_ignore_foreign_target_fields

Parent: `AUTH-S01` | Operation: `AUTH-S01` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/urls.py:4–17; SPDWEBAPP/AUTHENTICATE/views.py:26–305`

```text
GIVEN A has ACTIVE profile, B separate; A linked Old, B Other; both have distinct images
  AND variants: update_majors {majors:['Physics'],user_id:B.id}; reset-photo {user_id:B.id}
  AND also update_photo multipart profile_photo=40x40 PNG,user_id=B.id
WHEN A POSTs one listed request, starting each variant from original snapshot
THEN response matches operation: majors/reset 200 true; non-AJAX photo redirect profile
  AND only A selected major links/image change; no role or privilege field changes
  AND B User/profile/role/major links and image bytes/reference remain unchanged
```

<a id="auth-s02a"></a>

### AUTH-S02a — test_csrf_rejects_profile_mutation_tokens

Parent: `AUTH-S02` | Operation: `AUTH-S02` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/SPDWEBAPP_CORE/settings.py:93–100; SPDWEBAPP/AUTHENTICATE/views.py:72–305`

```text
GIVEN csrf_client identity A; real HTTPS cookie/token acquired from /auth/profile/
  AND routes/payloads: change-password JSON current_password=TEST_PASSWORD
  AND new_password1=new_password2='Replacement-22!word'; update_profile form P
  AND update_photo multipart 40x40 PNG; reset-photo form {}; update_majors {majors:[]}
  AND add-custom-major {major_name:'Astronomy'}; variants absent token or token='invalid'
WHEN POST each /auth/ route using its stated content type and token variant
THEN response is 403 before any business writes
  AND A identity/hash/profile/major links/image reference and bytes unchanged
  AND B state and Major catalog unchanged; CSRF metadata/messages need not be identical
```

<a id="auth-s02b"></a>

### AUTH-S02b — test_csrf_accepts_real_profile_tokens

Parent: `AUTH-S02` | Operation: `AUTH-S02` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/SPDWEBAPP_CORE/settings.py:93–100; SPDWEBAPP/AUTHENTICATE/views.py:72–305`

```text
GIVEN csrf_client identity A; original snapshot reset for each variant
  AND real HTTPS cookie/token from /auth/profile/; routes and payloads listed below
  AND change-password JSON
    current_password=TEST_PASSWORD,new_password1=new_password2='Replacement-22!word'
  AND update_profile form P; update_photo multipart 40x40 PNG; reset-photo form {}
  AND update_majors JSON {majors:[]}; add-custom-major JSON {major_name:'Astronomy'}
WHEN POST one request; JSON token in X-CSRFToken, form/multipart csrfmiddlewaretoken
THEN JSON responses are 200 success=true; ordinary photo redirects profile
  AND only the named password/P fields/image/A major links/catalog operation changes
  AND session remains A; B state, A role/privilege fields unchanged
```

<a id="auth-s02c"></a>

### AUTH-S02c — test_login_csrf_token_boundary

Parent: `AUTH-S02` | Operation: `AUTH-S02` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/SPDWEBAPP_CORE/settings.py:93–100; SPDWEBAPP/AUTHENTICATE/views.py:72–305`

```text
GIVEN anonymous csrf_client GETs /auth/login/ for real cookie/form token
  AND A username='actor-a', TEST_PASSWORD; token variants absent, 'invalid', matching
WHEN form POST A credentials to /auth/login/ with listed token
THEN absent/bad token gives 403 with anonymous identity
  AND matching token redirects home and authenticates A
  AND A/B User/profile/hash/role/major/file state unchanged
```

<a id="auth-s02d"></a>

### AUTH-S02d — test_other_mutation_methods_policy

Parent: `AUTH-S02` | Operation: `AUTH-S02` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-MUTATION-METHOD](../decisions.md#q-mutation-method)
Source: `SPDWEBAPP/SPDWEBAPP_CORE/settings.py:93–100; SPDWEBAPP/AUTHENTICATE/views.py:72–305`

```text
GIVEN A authenticated with profile/image; routes update_profile/update_photo/reset-photo
  AND also update_majors/add-custom-major; methods PUT/PATCH/DELETE
  AND use matching CSRF header and operation payload from this file
WHEN send each method to each named /auth/ route
THEN Q-MUTATION-METHOD chooses legacy JSON-false/photo-redirect versus HTTP 405
  AND no listed method changes A/B User/profile/hash/role/major/image/catalog state
  AND session identity remains A
```
