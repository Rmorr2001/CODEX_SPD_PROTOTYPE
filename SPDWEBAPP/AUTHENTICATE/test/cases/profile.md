# Profile cases

[Case index](../case-index.md) · [Inventory](../regression-spec.md) ·
[Shared fixtures](../../../../docs/testing/fixture-contract.md) · [Decisions](../decisions.md)

[Fresh actor/file fixture legend](../fixture-notes.md) applies independently to every case.

Payload P is form data: username="updated-a", email="updated@example.invalid",
firstName="Alex", lastName="Example", hometown="Demo Town", pclass="Alpha".
A/B are distinct synthetic users. No target identity is inferred from posted IDs.

Every case is a design only. Refresh named rows/relations and check file bytes
separately. Unlisted fields on named A/B rows stay unchanged, including hashes,
User first_name/last_name and staff/superuser flags; admin LogEntry is asserted
only for admin writes. Compare session identity, not whole CSRF/session blobs.

<a id="auth-a04-01a"></a>

### AUTH-A04-01a — test_edit_own_profile

Parent: `AUTH-A04-01` | Operation: `AUTH-A04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A/B have distinct profiles, no A image; A has major Physics
  AND A starts in class Beta independently for every role variant; P submits Alpha
  AND A role variants: (), ACTIVE, EXEC, PHIL_CHAIR, NM_BOARD, NME
  AND also EXEC+ACTIVE, PHIL_CHAIR+ACTIVE, NEW_MEMBER, NEW_MEMBER+ACTIVE
  AND also NEW_MEMBER+EXEC+ACTIVE, ALUMNI, ALUMNI+ACTIVE
  AND profile payload P is defined at this file's top
WHEN form POST /auth/update_profile/ with P
THEN response is 200 JSON {success:true}
  AND A username/email and profile firstName/lastName/hometown/pclass equal P
  AND A hash, User first_name/last_name, flags, roles/majors and B rows are unchanged
```

<a id="auth-a04-01b"></a>

### AUTH-A04-01b — test_profile_ignores_target_and_privilege_fields

Parent: `AUTH-A04-01` | Operation: `AUTH-A04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A/B profiles are distinct; A has ACTIVE, not EXEC; no images
  AND P is extended with user=B.id, user_id=B.id, profile_id=B.profile.id
  AND and roles=EXEC, is_staff=true, is_superuser=true
WHEN A form POSTs /auth/update_profile/ with extended P
THEN response is 200 JSON {success:true}; only A's P fields change
  AND A remains nonstaff/nonsuperuser with only ACTIVE
  AND B User/profile/major/role rows and A hash remain unchanged
```

<a id="auth-a04-01c"></a>

### AUTH-A04-01c — test_repeat_profile_update

Parent: `AUTH-A04-01` | Operation: `AUTH-A04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A already has exact P fields, no image; B distinct
WHEN POST P twice to /auth/update_profile/
THEN each response is 200 JSON {success:true}
  AND no User/profile/catalog rows are added
  AND A/B values and role/major links remain unchanged
```

<a id="auth-a04-02a"></a>

### AUTH-A04-02a — test_profile_rejects_blacklist_field

Parent: `AUTH-A04-02` | Operation: `AUTH-A04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A has no image; start with P
  AND variants replace exactly one field with 'fuck': username, firstName, lastName, hometown,
    pclass
WHEN form POST one variant to /auth/update_profile/
THEN response is 200 JSON success=false
  AND message is 'Input contains inappropriate language.'
  AND A/B Users/profiles/roles/majors remain unchanged
```

<a id="auth-a04-02b"></a>

### AUTH-A04-02b — test_profile_get_rejection

Parent: `AUTH-A04-02` | Operation: `AUTH-A04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A authenticated with profile and no image
WHEN GET /auth/update_profile/
THEN response is 200 JSON success=false, message='Invalid request'
  AND A/B User/profile fields and relations remain unchanged
  AND no file or catalog row is created
```

<a id="auth-a04-02c"></a>

### AUTH-A04-02c — test_profile_accepts_exact_whitelist

Parent: `AUTH-A04-02` | Operation: `AUTH-A04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A has no image; P hometown is 'biological engineering'
WHEN form POST /auth/update_profile/ with that P
THEN response is 200 JSON {success:true}
  AND A hometown becomes exactly 'biological engineering'; remaining P fields persist
  AND A roles/majors/hash and B rows remain unchanged
```

<a id="auth-a04-03a"></a>

### AUTH-A04-03a — test_profile_duplicate_username

Parent: `AUTH-A04-03` | Operation: `AUTH-A04` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [F-VALID](../decisions.md#f-valid); [Q-VALID](../decisions.md#q-valid); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN B owns username='actor-b'; A snapshot includes User and profile
WHEN form POST P with username='actor-b' to /auth/update_profile/
THEN Q-VALID/Q-ERROR choose a controlled duplicate-username field error
  AND A cannot take B username or partially change any P field
  AND A/B profiles, identities and role/major relations stay unchanged
```

<a id="auth-a04-03b"></a>

### AUTH-A04-03b — test_profile_missing_fields

Parent: `AUTH-A04-03` | Operation: `AUTH-A04` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-PARSE](../decisions.md#f-parse); [Q-VALID](../decisions.md#q-valid)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN P is the complete payload; A/B snapshots include User and profile
  AND variants omit one: username, email, firstName, lastName, hometown, pclass
WHEN form POST one variant to /auth/update_profile/
THEN Q-VALID chooses required-field errors or explicit optional-field defaults
  AND omission must not incidentally erase other fields or crash on None.lower
  AND rejected request leaves A/B rows and relations unchanged
```

<a id="auth-a04-03c"></a>

### AUTH-A04-03c — test_profile_field_validation_boundaries

Parent: `AUTH-A04-03` | Operation: `AUTH-A04` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-VALID](../decisions.md#q-valid); database length behavior
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A/B snapshots include User and profile; P is otherwise complete
  AND variants: empty username/email; email='not-email'; pclass='NotAClass'; hometown='null'
  AND lengths: username 150/151, email 254/255, profile names/hometown 200/201, pclass 50/51
  AND text variants: 'Zoë', '<tag>', a control-character-containing name
WHEN form POST each isolated field variant to /auth/update_profile/
THEN Q-VALID defines accepted fields, lengths, choices, optional blanks and text handling
  AND accepted field persists exactly under that rule; rejection writes no P fields
  AND B, hashes, flags and role/major links remain unchanged
```

<a id="auth-a04-04a"></a>

### AUTH-A04-04a — test_profile_database_second_write_failure

Parent: `AUTH-A04-04` | Operation: `AUTH-A04` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-PARTIAL](../decisions.md#f-partial); [Q-ATOMIC](../decisions.md#q-atomic); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A/B profile and User snapshots captured; A no image
  AND inject profile database save failure after User.save completes
WHEN form POST P to /auth/update_profile/
THEN Q-ERROR defines controlled failure response
  AND Q-ATOMIC chooses rollback versus explicit recoverable partial-state contract
  AND no silent success or unreported username/email-only change; B and roles stay unchanged
```

<a id="auth-a04-04b"></a>

### AUTH-A04-04b — test_profile_image_storage_failure_after_user_write

Parent: `AUTH-A04-04` | Operation: `AUTH-A04` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-PARTIAL](../decisions.md#f-partial); [Q-ATOMIC](../decisions.md#q-atomic); [Q-IMAGE](../decisions.md#q-image); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A has synthetic old.png with stored bytes; B has separate image
  AND inject storage.save failure in the model hook after A User.save
WHEN form POST P to /auth/update_profile/
THEN Q-ERROR selects controlled response; Q-ATOMIC defines DB/file compensation
  AND A old bytes cannot be silently lost; record User fields and old/new references separately
  AND B rows/image and A role/major links remain unchanged
```

<a id="auth-a04-05a"></a>

### AUTH-A04-05a — test_profile_missing_profile_response

Parent: `AUTH-A04-05` | Operation: `AUTH-A04` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-PROFILE](../decisions.md#q-profile); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN make_user(username='no-profile', with_profile=False); B has a profile
WHEN no-profile user form POSTs P to /auth/update_profile/
THEN Q-PROFILE chooses onboarding, controlled rejection or explicit creation
  AND Q-ERROR chooses response; no User-only update or accidental profile creation
  AND B rows/relations remain unchanged
```

<a id="auth-a04-05b"></a>

### AUTH-A04-05b — test_profile_text_edit_image_retention

Parent: `AUTH-A04-05` | Operation: `AUTH-A04` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-IMAGE](../decisions.md#q-image); [F-IMAGE-REWRITE](../decisions.md#f-image-rewrite)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:126–164; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old.png and B other.png exist in temporary_media; P changes text only
WHEN A form POSTs P to /auth/update_profile/
THEN Q-IMAGE decides whether unrelated text edits may re-encode/rename images
  AND response 200 success only if all requested text changes persist consistently
  AND record file references/bytes/orphans; B file and all role/major links unchanged
```

<a id="auth-a10-01a"></a>

### AUTH-A10-01a — test_profile_read_own_context

Parent: `AUTH-A10-01` | Operation: `AUTH-A10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:167–185`

```text
GIVEN A/B have distinct profiles with no images; A major Physics, B major Chemistry
WHEN A GETs /auth/profile/?user_id=B.id
THEN response is 200 AUTHENTICATE/profile.html; brother_profile is A's
  AND page includes A fields, not B private profile form values
  AND fresh A/B User/profile/role/major rows remain unchanged
```

<a id="auth-a10-01b"></a>

### AUTH-A10-01b — test_profile_sorted_majors_and_form_payloads

Parent: `AUTH-A10-01` | Operation: `AUTH-A10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:167–185`

```text
GIVEN A has no image; catalog names are Zoology, Chemistry; B distinct
WHEN A GETs /auth/profile/
THEN response is 200; available_majors are Chemistry then Zoology
  AND form names include username, firstName, lastName, hometown, email, pclass
  AND photo field is profile_photo with multipart form and CSRF token
  AND A/B rows and files remain unchanged
```

<a id="auth-a10-02a"></a>

### AUTH-A10-02a — test_profile_url_failure_cannot_delete_reference

Parent: `AUTH-A10-02` | Operation: `AUTH-A10` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [F-DESTRUCTIVE-READ](../decisions.md#f-destructive-read); [Q-STORAGE](../decisions.md#q-storage); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:167–185`

```text
GIVEN A old.png bytes and DB reference exist; B other.png distinct
  AND inject storage.url transient exception, without deleting A bytes
WHEN A GETs /auth/profile/
THEN Q-ERROR chooses fallback rendering versus controlled unavailable response
  AND GET must not clear A image reference or write profile fields
  AND A/B stored bytes, rows and relations remain unchanged
```

<a id="auth-a10-02b"></a>

### AUTH-A10-02b — test_profile_missing_physical_file_policy

Parent: `AUTH-A10-02` | Operation: `AUTH-A10` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-STORAGE](../decisions.md#q-storage)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:167–185`

```text
GIVEN A DB reference old.png exists but bytes are deliberately absent
  AND storage.url still generates /media/profile_images/old.png; B intact
WHEN A GETs /auth/profile/
THEN Q-STORAGE chooses placeholder, repair workflow or unavailable response
  AND URL generation alone must not be treated as proof that bytes exist
  AND no incidental B or A role/major/User writes; any reference repair must be explicit
```

<a id="auth-a10-03a"></a>

### AUTH-A10-03a — test_profile_read_without_profile

Parent: `AUTH-A10-03` | Operation: `AUTH-A10` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-PROFILE](../decisions.md#q-profile); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:167–185`

```text
GIVEN make_user(username='no-profile', with_profile=False); B intact
WHEN no-profile user GETs /auth/profile/
THEN Q-PROFILE selects onboarding/rejection/explicit creation and response
  AND no incidental new profile or changes to B are permitted
  AND no username, hash, role or file changes occur
```

<a id="auth-a10-03b"></a>

### AUTH-A10-03b — test_profile_read_does_not_rewrite_image

Parent: `AUTH-A10-03` | Operation: `AUTH-A10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:167–185`

```text
GIVEN A old.png is readable; storage.url works; B other.png separate
  AND snapshot_scope records A/B profiles and both files
WHEN A GETs /auth/profile/ twice
THEN both responses are 200 and context is A's own profile
  AND no storage.save/delete occurs; A reference and bytes remain identical
  AND A/B User/profile fields and role/major relations remain unchanged
```
