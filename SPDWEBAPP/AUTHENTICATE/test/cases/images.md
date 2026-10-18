# Images cases

[Case index](../case-index.md) · [Inventory](../regression-spec.md) ·
[Shared fixtures](../../../../docs/testing/fixture-contract.md) · [Decisions](../decisions.md)

[Fresh actor/file fixture legend](../fixture-notes.md) applies independently to every case.

Every image uses synthetic bytes under temporary_media(). A and B have distinct
file references. Inspect stored bytes and DB references independently; no real uploads.
Inject faults only at storage/DB boundaries, not by mocking view behavior.

Every case is a design only. Refresh named rows/relations and check file bytes
separately. Unlisted fields on named A/B rows stay unchanged, including hashes,
User first_name/last_name and staff/superuser flags; admin LogEntry is asserted
only for admin writes. Compare session identity, not whole CSRF/session blobs.

<a id="auth-a05-01a"></a>

### AUTH-A05-01a — test_photo_ajax_thumbnail_png

Parent: `AUTH-A05-01` | Operation: `AUTH-A05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A has no image; B other.png exists in temporary_media
  AND upload is synthetic 900x450 PNG named portrait.png; A has major Physics
  AND A role variants: (), ACTIVE, EXEC, NEW_MEMBER, ALUMNI
WHEN A multipart POSTs /auth/update_photo/ with profile_photo=portrait.png
  AND and X-Requested-With: XMLHttpRequest
THEN response is 200 JSON success=true with current image_url
  AND stored A bytes decode as PNG sized 300x150 at an existing temporary path
  AND A User/roles/majors and B rows/file remain unchanged
```

<a id="auth-a05-01b"></a>

### AUTH-A05-01b — test_photo_form_preserves_small_jpeg

Parent: `AUTH-A05-01` | Operation: `AUTH-A05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A has no image; B other.png exists
  AND upload is synthetic 80x40 JPEG named portrait.jpg
WHEN A multipart POSTs /auth/update_photo/ with profile_photo=portrait.jpg, no AJAX header
THEN response redirects to reverse('profile')
  AND stored A bytes decode as JPEG sized 80x40, without upscaling
  AND A User/profile text/roles/majors and B rows/file are unchanged
```

<a id="auth-a05-02a"></a>

### AUTH-A05-02a — test_photo_successful_replacement

Parent: `AUTH-A05-02` | Operation: `AUTH-A05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old.png and B other.png exist as distinct temporary files
  AND replacement is synthetic 40x40 PNG named new.png
WHEN A multipart POSTs profile_photo=new.png to /auth/update_photo/
THEN response redirects to profile
  AND A references readable new PNG bytes; old A path no longer exists
  AND B file/reference, A/B identity fields and role/major links remain unchanged
```

<a id="auth-a05-02b"></a>

### AUTH-A05-02b — test_photo_repeat_filename_retention

Parent: `AUTH-A05-02` | Operation: `AUTH-A05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-IMAGE](../decisions.md#q-image)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A image portrait.png exists and B file is separate
  AND new synthetic 40x40 PNG has the same supplied name portrait.png
WHEN A uploads the same named replacement twice
THEN Q-IMAGE selects old-file cleanup/retention and filename-collision rule
  AND response may report success only with a readable current image
  AND enumerate old/new paths and orphan bytes; B image and identity fields unchanged
```

<a id="auth-a05-02c"></a>

### AUTH-A05-02c — test_model_save_image_reencoding_policy

Parent: `AUTH-A05-02` | Operation: `AUTH-A05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [F-IMAGE-REWRITE](../decisions.md#f-image-rewrite); [Q-IMAGE](../decisions.md#q-image)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A has stored portrait.png and unchanged profile data; B separate
WHEN call A.brother_profile.save() twice directly
THEN Q-IMAGE chooses whether unchanged saves may re-encode/rename bytes
  AND any new file and old-file cleanup must follow that explicit rule
  AND A User/roles/majors and all B rows/file remain unchanged
```

<a id="auth-a05-03a"></a>

### AUTH-A05-03a — test_photo_corrupt_upload_retains_old_image

Parent: `AUTH-A05-03` | Operation: `AUTH-A05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [F-INVALID-IMAGE](../decisions.md#f-invalid-image); [Q-IMAGE](../decisions.md#q-image); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old.png is readable; B other.png separate
  AND upload variants: b'not-an-image' named fake.png; empty bytes; truncated PNG header
WHEN A multipart POSTs each profile_photo variant to /auth/update_photo/
THEN Q-ERROR defines controlled non-success without internal exception/path text
  AND invalid bytes must not replace the previous usable A image
  AND A/B User/profile text/role/major state and B image remain unchanged
```

<a id="auth-a05-03b"></a>

### AUTH-A05-03b — test_photo_format_contenttype_policy

Parent: `AUTH-A05-03` | Operation: `AUTH-A05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-IMAGE](../decisions.md#q-image)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old.png exists; B separate
  AND variants: PNG bytes named .jpg with image/jpeg; GIF bytes with text/plain
  AND and a Pillow-readable format not selected by the eventual supported-format rule
WHEN A multipart POSTs each profile_photo variant
THEN Q-IMAGE chooses decode-based acceptance versus mismatch/format rejection
  AND accepted output matches selected format rule; rejected upload retains old bytes/reference
  AND no unrelated A/B rows, roles, majors or B files change
```

<a id="auth-a05-03c"></a>

### AUTH-A05-03c — test_photo_size_dimension_boundaries

Parent: `AUTH-A05-03` | Operation: `AUTH-A05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-IMAGE](../decisions.md#q-image)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old.png exists; B separate
  AND construct byte sizes at/one above limit L and pixel dimensions at/one above limit D
  AND L and D are not yet defined; no limit is inferred from thumbnail size
WHEN A uploads each boundary image as profile_photo
THEN Q-IMAGE defines L/D and rejection/normalization responses before implementation
  AND rejected upload retains old A bytes/reference; accepted result is readable
  AND B files/rows and A identity/role/major state remain unchanged
```

<a id="auth-a05-04a"></a>

### AUTH-A05-04a — test_photo_old_delete_failure

Parent: `AUTH-A05-04` | Operation: `AUTH-A05` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-ATOMIC](../decisions.md#q-atomic); [Q-STORAGE](../decisions.md#q-storage); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old.png and B other.png exist
  AND inject old image delete failure before new storage.save
WHEN A uploads synthetic new.png to /auth/update_photo/
THEN Q-ATOMIC chooses abort versus continue-with-retained-old-file behavior
  AND response must match resulting DB/file state without exception leakage
  AND B bytes/rows and A identity/role/major fields remain unchanged
```

<a id="auth-a05-04b"></a>

### AUTH-A05-04b — test_photo_new_storage_save_failure

Parent: `AUTH-A05-04` | Operation: `AUTH-A05` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-FILE-LOSS](../decisions.md#f-file-loss); [Q-ATOMIC](../decisions.md#q-atomic); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old.png and B other.png exist
  AND inject replacement storage.save failure after the old delete phase
WHEN A uploads synthetic new.png to /auth/update_photo/
THEN Q-ERROR defines controlled non-success; no false success
  AND Q-ATOMIC defines compensation so the old usable image is not silently lost
  AND check fresh DB pointer and old/new bytes separately; B unchanged
```

<a id="auth-a05-04c"></a>

### AUTH-A05-04c — test_photo_database_failure_after_new_file

Parent: `AUTH-A05-04` | Operation: `AUTH-A05` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-PARTIAL](../decisions.md#f-partial); [Q-ATOMIC](../decisions.md#q-atomic); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old.png and B other.png exist
  AND allow new file save, then inject profile database write failure
WHEN A uploads synthetic new.png to /auth/update_photo/
THEN Q-ERROR defines controlled failure; Q-ATOMIC defines restored reference/file cleanup
  AND no unreported orphan or dangling reference may be treated as completed replacement
  AND A User/roles/majors and B rows/file remain unchanged
```

<a id="auth-a05-04d"></a>

### AUTH-A05-04d — test_photo_response_lookup_failure_after_save

Parent: `AUTH-A05-04` | Operation: `AUTH-A05` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-ERROR-LEAK](../decisions.md#f-error-leak); [Q-STORAGE](../decisions.md#q-storage); [Q-ERROR](../decisions.md#q-error); [Q-ATOMIC](../decisions.md#q-atomic)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old.png exists; replacement storage and DB writes complete
  AND variants: .path access fails during final logging; AJAX .url access fails
WHEN A uploads synthetic new.png to /auth/update_photo/
THEN Q-ERROR/Q-ATOMIC choose committed-success recovery versus compensated failure
  AND response must not expose internal paths or falsely imply no mutation
  AND assert documented DB/file outcome, with B rows/file and A roles unchanged
```

<a id="auth-a05-05a"></a>

### AUTH-A05-05a — test_photo_missing_upload_is_noop

Parent: `AUTH-A05-05` | Operation: `AUTH-A05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old.png and B other.png exist
  AND variants: GET; POST no file; POST file under wrong key 'avatar'
WHEN A requests /auth/update_photo/ using one variant
THEN response redirects to reverse('profile')
  AND A/B file references and bytes are unchanged
  AND A/B Users/profiles/roles/majors remain unchanged
```

<a id="auth-a05-05b"></a>

### AUTH-A05-05b — test_photo_without_profile

Parent: `AUTH-A05-05` | Operation: `AUTH-A05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-PROFILE](../decisions.md#q-profile); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN make_user(username='no-profile', with_profile=False); B other.png intact
WHEN no-profile user multipart POSTs synthetic profile_photo=new.png
THEN Q-PROFILE/Q-ERROR choose controlled missing-profile response/onboarding
  AND no orphan upload or incidental User/profile/role writes
  AND B image and rows remain unchanged
```

<a id="auth-a05-05c"></a>

### AUTH-A05-05c — test_photo_storage_without_local_path

Parent: `AUTH-A05-05` | Operation: `AUTH-A05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-STORAGE](../decisions.md#q-storage); [F-PATH-DEPENDENCY](../decisions.md#f-path-dependency)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A old image and B image use storage supporting open/save/delete/url, not .path
WHEN A uploads synthetic new.png through /auth/update_photo/
THEN Q-STORAGE decides supported backends and response for unsupported backend
  AND supported backend must produce readable current A image without local-path assumptions
  AND DB/file consistency follows Q-ATOMIC; B image and identity fields unchanged
```

<a id="auth-a05-05d"></a>

### AUTH-A05-05d — test_model_animation_alpha_format_policy

Parent: `AUTH-A05-05` | Operation: `AUTH-A05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-IMAGE](../decisions.md#q-image)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:188–235; SPDWEBAPP/AUTHENTICATE/models.py:101–127`

```text
GIVEN A profile has no image; B distinct
  AND variants: transparent RGBA PNG; synthetic two-frame GIF; unsupported decode format
WHEN assign listed image and call Brother_Profile.save directly
THEN Q-IMAGE defines alpha/frame/format preservation or explicit rejection
  AND stored bytes obey that selected rule and remain decodable
  AND A identity/roles/majors and B files/rows remain unchanged
```

<a id="auth-a06-01a"></a>

### AUTH-A06-01a — test_reset_photo_removes_own_file

Parent: `AUTH-A06-01` | Operation: `AUTH-A06` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:238–253`

```text
GIVEN A old.png and B other.png exist under temporary_media
  AND A role variants: (), ACTIVE, EXEC, NEW_MEMBER, ALUMNI
WHEN A POSTs /auth/reset-photo/ with a real token
THEN response is 200 JSON success=true, message='Profile photo reset successfully'
  AND A image field is empty and old A bytes no longer exist
  AND B image, A/B User/profile text and role/major relations remain unchanged
```

<a id="auth-a06-01b"></a>

### AUTH-A06-01b — test_reset_photo_without_image_idempotent

Parent: `AUTH-A06-01` | Operation: `AUTH-A06` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:238–253`

```text
GIVEN A has no image, either initially or after one completed reset
  AND B other.png exists; variants are those two starting states
WHEN A POSTs /auth/reset-photo/
THEN response is 200 JSON success=true with reset-success message
  AND A image remains empty; no file is created
  AND A/B identities/roles/majors and B bytes remain unchanged
```

<a id="auth-a06-02a"></a>

### AUTH-A06-02a — test_reset_photo_get_is_noop

Parent: `AUTH-A06-02` | Operation: `AUTH-A06` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:238–253`

```text
GIVEN A old.png and B other.png exist
WHEN A GETs /auth/reset-photo/
THEN response is 200 JSON success=false, message='Invalid request'
  AND A/B bytes and image references remain unchanged
  AND A/B User/profile text and role/major links remain unchanged
```

<a id="auth-a06-02b"></a>

### AUTH-A06-02b — test_reset_without_profile

Parent: `AUTH-A06-02` | Operation: `AUTH-A06` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-PROFILE](../decisions.md#q-profile); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:238–253`

```text
GIVEN make_user(username='no-profile', with_profile=False); B image intact
WHEN no-profile user POSTs /auth/reset-photo/
THEN Q-PROFILE/Q-ERROR choose missing-profile response without raw exception detail
  AND no profile, file, role or User update is created
  AND B rows/image remain unchanged
```

<a id="auth-a06-03a"></a>

### AUTH-A06-03a — test_reset_storage_delete_failure

Parent: `AUTH-A06-03` | Operation: `AUTH-A06` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-ATOMIC](../decisions.md#q-atomic); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:238–253`

```text
GIVEN A old.png and B other.png exist
  AND inject storage.delete failure before old bytes are removed
WHEN A POSTs /auth/reset-photo/
THEN Q-ERROR selects controlled failure; no reset-success response
  AND A DB reference and bytes must stay consistent under Q-ATOMIC
  AND A/B identity/relations and B bytes remain unchanged
```

<a id="auth-a06-03b"></a>

### AUTH-A06-03b — test_reset_implicit_database_save_failure

Parent: `AUTH-A06-03` | Operation: `AUTH-A06` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-FILE-LOSS](../decisions.md#f-file-loss); [Q-ATOMIC](../decisions.md#q-atomic); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:238–253`

```text
GIVEN A old.png and B other.png exist
  AND inject profile DB save failure inside FieldFile.delete(save=True), after byte deletion
WHEN A POSTs /auth/reset-photo/
THEN Q-ATOMIC defines restoration/compensation rather than dangling DB reference
  AND Q-ERROR selects non-success response without exception text
  AND B file/rows and A User/profile text/role/major state remain unchanged
```

<a id="auth-a06-03c"></a>

### AUTH-A06-03c — test_reset_final_database_save_failure

Parent: `AUTH-A06-03` | Operation: `AUTH-A06` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-ATOMIC](../decisions.md#q-atomic); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:238–253`

```text
GIVEN A old.png exists; FieldFile.delete and its implicit DB save complete
  AND inject failure on the final explicit profile.save
WHEN A POSTs /auth/reset-photo/
THEN Q-ATOMIC chooses committed reset reporting versus restoration compensation
  AND response must reflect that decision rather than hiding completed deletion
  AND B file/rows and A identity/text/roles/majors remain unchanged
```
