# Majors cases

[Case index](../case-index.md) · [Inventory](../regression-spec.md) ·
[Shared fixtures](../../../../docs/testing/fixture-contract.md) · [Decisions](../decisions.md)

[Fresh actor/file fixture legend](../fixture-notes.md) applies independently to every case.

A/B have distinct real profiles and independently named major links. Payloads
use names, matching the mounted endpoint, not guessed major-ID schemas.

Every case is a design only. Refresh named rows/relations and check file bytes
separately. Unlisted fields on named A/B rows stay unchanged, including hashes,
User first_name/last_name and staff/superuser flags; admin LogEntry is asserted
only for admin writes. Compare session identity, not whole CSRF/session blobs.

<a id="auth-a07-01a"></a>

### AUTH-A07-01a — test_replace_own_major_set

Parent: `AUTH-A07-01` | Operation: `AUTH-A07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A linked to Old; B linked to Other; catalog New exists
  AND A role variants: (), ACTIVE, EXEC, NEW_MEMBER, ALUMNI
WHEN A JSON POSTs /auth/update_majors/ with {majors:['New','New']}
THEN response is 200 JSON success=true, message='Majors updated successfully'
  AND A links exactly one New row; Old/New catalog rows remain
  AND B links, A/B Users/profiles/roles remain unchanged
```

<a id="auth-a07-01b"></a>

### AUTH-A07-01b — test_clear_own_major_set

Parent: `AUTH-A07-01` | Operation: `AUTH-A07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A linked to Old; B linked to Other
WHEN A JSON POSTs /auth/update_majors/ with {majors:[]}
THEN response is 200 JSON success=true with majors-updated message
  AND A has zero major links; catalog Old remains
  AND B links, Users/profiles/roles are unchanged
```

<a id="auth-a07-02a"></a>

### AUTH-A07-02a — test_major_selection_missing_key

Parent: `AUTH-A07-02` | Operation: `AUTH-A07` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-MAJORS](../decisions.md#q-majors)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A linked to Old; B linked to Other
WHEN A JSON POSTs {} to /auth/update_majors/
THEN Q-MAJORS chooses omitted-key validation error versus intentional clear
  AND if rejected, A Old links remain; if clear accepted, only A links are removed
  AND B links and catalog rows remain unchanged
```

<a id="auth-a07-02b"></a>

### AUTH-A07-02b — test_major_selection_json_shape

Parent: `AUTH-A07-02` | Operation: `AUTH-A07` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-PARSE](../decisions.md#f-parse); [Q-PARSE](../decisions.md#q-parse); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A linked to Old; B linked to Other
  AND bodies: '{', '[]', 'null', '{"majors":null}', '{"majors":"Physics"}', '{"majors":{}}'
WHEN A POSTs each body as application/json to /auth/update_majors/
THEN Q-PARSE/Q-ERROR define typed controlled rejection
  AND no bad request may silently clear A links or create character-name majors
  AND A/B links, catalog and identity/roles remain unchanged
```

<a id="auth-a07-02c"></a>

### AUTH-A07-02c — test_major_selection_name_validation

Parent: `AUTH-A07-02` | Operation: `AUTH-A07` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-MAJORS](../decisions.md#q-majors); [Q-VALID](../decisions.md#q-valid); [Q-FILTER](../decisions.md#q-filter)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A linked to Old; B to Other
  AND majors variants: [7], [''], ['x' repeated 256], ['fuck'], ['physics','Physics']
WHEN A JSON POSTs each majors variant to /auth/update_majors/
THEN Q-MAJORS/Q-VALID/Q-FILTER choose name validation and case-normalization rules
  AND rejected payload leaves A/B links and catalog unchanged
  AND accepted payload obeys exact selected rule without partial writes
```

<a id="auth-a07-02d"></a>

### AUTH-A07-02d — test_major_selection_count_boundary

Parent: `AUTH-A07-02` | Operation: `AUTH-A07` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-MAJORS](../decisions.md#q-majors)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A has Old; catalog Physics/Chemistry/Biology exists; B separate
  AND selected sets have 0, 1, 2 and 3 distinct names
WHEN A JSON POSTs each selected set to /auth/update_majors/
THEN Q-MAJORS chooses server maximum; UI-only 'up to 2' does not settle it
  AND accepted set replaces only A links; rejected set retains Old
  AND catalog, B links and identity/roles stay unchanged
```

<a id="auth-a07-03a"></a>

### AUTH-A07-03a — test_major_creation_mid_replace_failure

Parent: `AUTH-A07-03` | Operation: `AUTH-A07` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-PARTIAL](../decisions.md#f-partial); [Q-ATOMIC](../decisions.md#q-atomic); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A linked to Old; B linked to Other
  AND inject second get_or_create failure after first new major/link was written
WHEN A JSON POSTs {majors:['Physics','Chemistry']} to /auth/update_majors/
THEN Q-ATOMIC chooses rollback or explicit recoverable partial-result contract
  AND Q-ERROR selects response; no silent success/loss of Old links
  AND record catalog/link state after failure; B and identity/roles unchanged
```

<a id="auth-a07-03b"></a>

### AUTH-A07-03b — test_major_add_mid_replace_failure

Parent: `AUTH-A07-03` | Operation: `AUTH-A07` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-PARTIAL](../decisions.md#f-partial); [Q-ATOMIC](../decisions.md#q-atomic); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A linked to Old; Physics/Chemistry catalog rows exist; B separate
  AND inject second majors.add failure after first succeeds
WHEN A JSON POSTs {majors:['Physics','Chemistry']} to /auth/update_majors/
THEN Q-ATOMIC defines old-link restoration versus explicit partial recovery
  AND Q-ERROR selects non-success response; inspect fresh A links before test rollback
  AND catalog, B links and User/profile/role fields remain unchanged
```

<a id="auth-a07-04a"></a>

### AUTH-A07-04a — test_major_selection_get_noop

Parent: `AUTH-A07-04` | Operation: `AUTH-A07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A linked to Old; B linked to Other
WHEN A GETs /auth/update_majors/
THEN response is 200 JSON success=false, message='Invalid request method'
  AND A/B links and catalog rows remain unchanged
  AND Users/profiles/roles remain unchanged
```

<a id="auth-a07-04b"></a>

### AUTH-A07-04b — test_major_selection_no_profile

Parent: `AUTH-A07-04` | Operation: `AUTH-A07` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-PROFILE](../decisions.md#q-profile); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN make_user(username='no-profile', with_profile=False); B linked to Other
WHEN no-profile user JSON POSTs {majors:['Physics']} to /auth/update_majors/
THEN Q-PROFILE/Q-ERROR choose controlled rejection/onboarding response
  AND no new Major/profile/link or User change is created incidentally
  AND B links/catalog/roles remain unchanged
```

<a id="auth-a07-04c"></a>

### AUTH-A07-04c — test_major_selection_preexisting_duplicates

Parent: `AUTH-A07-04` | Operation: `AUTH-A07` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-UNIQUE](../decisions.md#q-unique); [F-PARTIAL](../decisions.md#f-partial); [Q-ATOMIC](../decisions.md#q-atomic); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN two catalog rows intentionally have name='Physics'; A has Old; B separate
WHEN A JSON POSTs {majors:['Physics']} to /auth/update_majors/
THEN Q-UNIQUE chooses remediation or controlled ambiguous-name error
  AND A Old links cannot be silently erased by MultipleObjectsReturned
  AND B links, identity/roles and unrelated catalog rows remain unchanged
```

<a id="auth-a07-04d"></a>

### AUTH-A07-04d — test_repeat_major_replacement

Parent: `AUTH-A07-04` | Operation: `AUTH-A07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A already linked to one New row; B has Other; no duplicate names
WHEN A POSTs {majors:['New']} twice to /auth/update_majors/
THEN both responses are 200 JSON success=true
  AND A still has exactly one link to existing New; no new catalog rows
  AND B links and A/B User/profile/role fields are unchanged
```

<a id="auth-a07-04e"></a>

### AUTH-A07-04e — test_concurrent_major_replacement_policy

Parent: `AUTH-A07-04` | Operation: `AUTH-A07` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-MAJORS](../decisions.md#q-majors); PostgreSQL independent connections/barrier required
Source: `SPDWEBAPP/AUTHENTICATE/views.py:256–276; SPDWEBAPP/AUTHENTICATE/models.py:82–96`

```text
GIVEN A has Old; B Other; two A clients synchronize concurrent replacements
  AND first set ['Physics'], second ['Chemistry']; all catalog rows exist
WHEN send concurrent JSON POSTs to /auth/update_majors/ using separate DB connections
THEN Q-MAJORS chooses last-writer-wins, conflict rejection or serialized replacement
  AND final A set cannot be an undocumented interleaving; responses match chosen rule
  AND B links/catalog/identities unchanged; use bounded waits, not SQLite evidence
```

<a id="auth-a08-01a"></a>

### AUTH-A08-01a — test_custom_major_normalization

Parent: `AUTH-A08-01` | Operation: `AUTH-A08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:279–305; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:229–256`

```text
GIVEN A/B linked to existing unrelated majors; no Mechanical Engineering catalog row
  AND A role variants: (), ACTIVE, EXEC, NEW_MEMBER, ALUMNI
WHEN A JSON POSTs {major_name:'  mechanical   ENGINEERING  '} to /auth/add-custom-major/
THEN response is 200 JSON success=true with major_name='Mechanical Engineering'
  AND major_id identifies exactly one created catalog row
  AND A/B links, Users/profiles and roles remain unchanged
```

<a id="auth-a08-01b"></a>

### AUTH-A08-01b — test_custom_major_sequential_idempotency

Parent: `AUTH-A08-01` | Operation: `AUTH-A08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:279–305; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:229–256`

```text
GIVEN Mechanical Engineering exists once; A/B separate
WHEN A POSTs {major_name:'mechanical engineering'} twice to /auth/add-custom-major/
THEN both responses are 200 JSON success=true with the existing major_id
  AND no new catalog row or profile-major link is created
  AND A/B User/profile/role state remains unchanged
```

<a id="auth-a08-01c"></a>

### AUTH-A08-01c — test_custom_major_acronym_unicode_policy

Parent: `AUTH-A08-01` | Operation: `AUTH-A08` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-NORMALIZE](../decisions.md#q-normalize)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:279–305; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:229–256`

```text
GIVEN A/B linked to existing majors
  AND names: 'NASA studies'; 'éLECTRICAL engineering'; 'iOS Engineering'
WHEN A JSON POSTs each major_name to /auth/add-custom-major/
THEN Q-NORMALIZE selects word.capitalize behavior or acronym/Unicode-aware alternative
  AND returned name and saved catalog key obey that rule
  AND A/B profile links and identity/roles remain unchanged
```

<a id="auth-a08-02a"></a>

### AUTH-A08-02a — test_custom_major_blacklist_rejection

Parent: `AUTH-A08-02` | Operation: `AUTH-A08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:279–305; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:229–256`

```text
GIVEN A/B profiles and catalog are unchanged snapshots
WHEN A JSON POSTs {major_name:'fuck'} to /auth/add-custom-major/
THEN response is 200 JSON success=false
  AND message is 'Major name contains inappropriate language'
  AND no catalog/link/User/profile/role writes occur
```

<a id="auth-a08-02b"></a>

### AUTH-A08-02b — test_custom_major_get_noop

Parent: `AUTH-A08-02` | Operation: `AUTH-A08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:279–305; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:229–256`

```text
GIVEN A authenticated; catalog and A/B links captured
WHEN A GETs /auth/add-custom-major/
THEN response is 200 JSON success=false, message='Invalid request method'
  AND catalog and A/B major links remain unchanged
  AND A/B Users/profiles/roles remain unchanged
```

<a id="auth-a08-03a"></a>

### AUTH-A08-03a — test_custom_major_empty_or_typed_payload

Parent: `AUTH-A08-03` | Operation: `AUTH-A08` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-VALID](../decisions.md#f-valid); [F-PARSE](../decisions.md#f-parse); [Q-VALID](../decisions.md#q-valid); [Q-PARSE](../decisions.md#q-parse); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:279–305; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:229–256`

```text
GIVEN A/B separate; catalog captured
  AND variants: {}; major_name='', '   ', null, 7, []; bodies '{', '[]', 'null'
  AND and major_name='x' repeated 256
WHEN A POSTs one listed JSON payload to /auth/add-custom-major/
THEN Q-VALID/Q-PARSE/Q-ERROR define controlled field/body errors
  AND no empty/invalid catalog row or partial write may result
  AND A/B links, User/profile/role fields remain unchanged
```

<a id="auth-a08-03b"></a>

### AUTH-A08-03b — test_custom_major_no_profile_catalog_policy

Parent: `AUTH-A08-03` | Operation: `AUTH-A08` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-MAJORS](../decisions.md#q-majors); [Q-PROFILE](../decisions.md#q-profile)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:279–305; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:229–256`

```text
GIVEN make_user(username='no-profile', with_profile=False); B linked to Physics
WHEN no-profile user JSON POSTs {major_name:'Astronomy'} to /auth/add-custom-major/
THEN Q-MAJORS chooses authenticated catalog creation versus profile requirement
  AND accepted case creates only catalog row; denied case creates none
  AND no incidental profile/role/User/link changes; B unchanged
```

<a id="auth-a08-03c"></a>

### AUTH-A08-03c — test_custom_major_browser_markup_safety

Parent: `AUTH-A08-03` | Operation: `AUTH-A08` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-VALID](../decisions.md#q-valid); browser execution required; template innerHTML sink
Source: `SPDWEBAPP/AUTHENTICATE/views.py:279–305; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:229–256`

```text
GIVEN A has rendered profile; browser uses real custom-major fetch
  AND names: '<img src=x onerror="window.bad=1">'; 'Quotes " and apostrophe'
WHEN A submits listed custom major through profile UI
THEN Q-VALID chooses rejection or literal text rendering with safe escaping
  AND window.bad must remain unset; no script executes from returned major_name
  AND only accepted catalog entry may change; A/B links/roles/identities unchanged
```

<a id="auth-a08-04a"></a>

### AUTH-A08-04a — test_custom_major_existing_duplicate_resolution

Parent: `AUTH-A08-04` | Operation: `AUTH-A08` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-UNIQUE](../decisions.md#q-unique); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:279–305; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:229–256`

```text
GIVEN two Major rows intentionally share name='Physics'; A/B links captured
WHEN A JSON POSTs {major_name:'physics'} to /auth/add-custom-major/
THEN Q-UNIQUE selects remediation/canonical row or controlled ambiguous-name response
  AND Q-ERROR forbids internal MultipleObjectsReturned details in response
  AND no unintended profile links or other catalog writes occur
```

<a id="auth-a08-04b"></a>

### AUTH-A08-04b — test_custom_major_postgresql_race

Parent: `AUTH-A08-04` | Operation: `AUTH-A08` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-UNIQUE](../decisions.md#q-unique); PostgreSQL separate connections/barrier required
Source: `SPDWEBAPP/AUTHENTICATE/views.py:279–305; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:229–256`

```text
GIVEN no Physics catalog row; A/B clients on independent PostgreSQL connections
  AND barrier pauses both immediately before creation; waits have bounded timeout
WHEN both JSON POST {major_name:'physics'} to /auth/add-custom-major/
THEN Q-UNIQUE chooses unique normalized key/idempotency or explicit conflict behavior
  AND responses and row count must obey selected uniqueness rule
  AND A/B profile links/roles/identity remain unchanged; SQLite is insufficient
```
