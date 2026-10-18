# Content persistence and failure boundaries

See [decisions](../regression-spec.md).

### HOME-T08a — test_singleton_initial_create_persists_value

Parent: `HOME-T08` | Operation: `HOME-O06, HOME-O07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/models.py:3–22`

```text
GIVEN empty BannerImage or RushFormLink table in separate parameter variants
  AND before = snapshot_scope([opposite_singleton, slide], files=[sentinel_file])
WHEN ORM creates a banner with a synthetic PNG or link https://example.invalid/rush
THEN save returns normally and exactly one corresponding row exists
  AND stored value is the uploaded banners/ file or the exact HTTPS URL
  AND image bytes match fixture bytes for banner
  AND str is Banner Image or the exact link respectively
  AND opposite singleton, slide and sentinel bytes are unchanged
```

### HOME-T08b — test_successful_singleton_replacement_has_one_new_value

Parent: `HOME-T08` | Operation: `HOME-O06, HOME-O07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/models.py:6–19`

```text
GIVEN singleton A and its synthetic image or HTTPS URL
  AND opposite singleton and unrelated slide are captured
WHEN ORM creates singleton B with new image bytes or https://example.invalid/new
THEN save returns normally and A row no longer exists
  AND exactly one row contains B reference/value
  AND B image bytes exist if the model is BannerImage
  AND opposite singleton and slide remain unchanged
  AND old-file retention is not asserted here; it is blocked in HOME-T10d
```

### HOME-T08c — test_singleton_normal_update_and_repeat_remain_single

Parent: `HOME-T08` | Operation: `HOME-O06, HOME-O07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/models.py:6–19`

```text
GIVEN one singleton B and opposite singleton plus slide sentinels
WHEN B value is changed and save() is called normally twice
THEN both calls return normally
  AND one singleton row contains the last image reference or HTTPS URL
  AND no duplicate singleton row is present
  AND new banner bytes persist when applicable
  AND opposite singleton and slide fields are unchanged
  AND no PK-stability or old-file-cleanup contract is invented
```

### HOME-T09a — test_model_full_clean_rejects_required_and_length_errors

Parent: `HOME-T09` | Operation: `HOME-O06, HOME-O07, HOME-O08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/models.py:3–32`

```text
GIVEN unsaved link="", link="not-a-url" or an HTTPS URL of length 201
  AND separate slides with caption="" or caption length 201; banner image=""
  AND captured stored singleton A, slide B and synthetic files
WHEN each instance full_clean() is called
THEN ValidationError names the relevant link, caption or image field
  AND no save or replacement runs
  AND stored singleton A, slide B and file bytes remain unchanged
  AND image-content validation belongs to the admin image form case
```

### HOME-T09b — test_singleton_update_fields_does_not_erase_previous_row

Parent: `HOME-T09` | Operation: `HOME-O06, HOME-O07` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 supported save options; destructive update needs fix
Source: `SPDWEBAPP/HOME/models.py:6–19`

```text
GIVEN singleton A with persisted image or HTTPS link and unrelated slide B
WHEN A value changes and save(update_fields=[image or link]) runs
THEN either the supported update succeeds or an unsupported-option error is explicit
  AND a failed update must not erase previously persisted A
  AND no replacement data may disappear after a raised DB update failure
  AND B and prior image bytes remain unchanged
  AND Q8 settles option support before exact exception/status assertion
  AND current delete-before-update cannot satisfy the no-loss invariant
```

### HOME-T09c — test_singleton_forced_save_options_policy

Parent: `HOME-T09` | Operation: `HOME-O06, HOME-O07` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 force_update/force_insert support; destructive hook also needs fix
Source: `SPDWEBAPP/HOME/models.py:6–19`

```text
GIVEN singleton A with stored image/link and an unsaved instance with missing PK
WHEN each instance uses force_update=True or force_insert=True separately
THEN Q8 chooses supported save modes and explicit unsupported-mode errors
  AND an error must leave prior committed A intact
  AND no opposite singleton, slide or sentinel file may change
  AND successful supported modes must retain the singleton invariant
  AND final return/exception assertions follow Q8
  AND no incidental row deletion is accepted as the error contract
```

### HOME-T09d — test_bulk_and_alias_singleton_boundary_policy

Parent: `HOME-T09` | Operation: `HOME-O06, HOME-O07` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 bulk/alternate alias support; isolated second DB alias if supported
Source: `SPDWEBAPP/HOME/models.py:6–19`

```text
GIVEN one singleton per temporary test DB alias and named opposite/slide sentinels
WHEN bulk_create, queryset.update or save(using="secondary") is called separately
THEN Q8 chooses prohibition or enforced singleton behavior for each entry point
  AND final result/exception assertions follow that supported API decision
  AND no action may delete data in the unintended database alias
  AND failed actions must preserve prior committed singleton references and bytes
  AND unrelated named rows in both aliases remain unchanged
  AND no real configured secondary database is used
```

### HOME-T09e — test_direct_save_validation_boundary_policy

Parent: `HOME-T09` | Operation: `HOME-O06, HOME-O07, HOME-O08` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 bare-save validation guarantees; Q3 URL schemes
Source: `SPDWEBAPP/HOME/models.py:3–32`

```text
GIVEN deliberate bare model instances with missing caption/image and invalid URL
  AND existing committed singleton A and sentinel slide/file
WHEN each instance save() is called without full_clean()
THEN Q8 chooses supported bare-save validation versus caller-only validation
  AND Q3 chooses allowed interest-link schemes
  AND final error/result assertions follow those decisions
  AND rejected writes must not erase prior committed A
  AND sentinel slide, opposite singleton and sentinel bytes remain unchanged
```

### HOME-T10a — test_storage_save_failure_preserves_prior_banner_row

Parent: `HOME-T10` | Operation: `HOME-O06` | Priority: P0
Status: `NEEDS_FIX` | Blockers: delete-before-storage-save data loss; Q7 cleanup choice
Source: `SPDWEBAPP/HOME/models.py:6–9`

```text
GIVEN committed banner A, real bytes old.png and an unrelated slide/link
  AND TransactionTestCase observes state outside any enclosing test transaction
WHEN replacement upload storage.save raises OSError before new bytes are written
THEN caller receives the injected failure without a false success
  AND refreshed A must still reference old.png with its original bytes
  AND no replacement row/file is committed
  AND slide, link and sentinel file remain unchanged
  AND retry after removing failure is covered separately in HOME-T10c
```

### HOME-T10b — test_db_insert_failure_preserves_prior_singleton

Parent: `HOME-T10` | Operation: `HOME-O06, HOME-O07` | Priority: P0
Status: `NEEDS_FIX` | Blockers: delete-before-base-save loses old row; Q7 orphan cleanup
Source: `SPDWEBAPP/HOME/models.py:6–19`

```text
GIVEN committed singleton A plus opposite singleton and slide sentinels
  AND TransactionTestCase sees direct calls outside a surrounding atomic block
WHEN replacement base insert raises IntegrityError after deletion
THEN caller receives IntegrityError without a success result
  AND previously committed A must still exist with its original value
  AND opposite singleton, slide and prior file bytes remain unchanged
  AND any new uploaded file residue is recorded separately from DB state
  AND Q7 decides how new orphan bytes must be compensated
```

### HOME-T10c — test_failed_replacement_retry_preserves_then_replaces

Parent: `HOME-T10` | Operation: `HOME-O06, HOME-O07` | Priority: P0
Status: `NEEDS_FIX` | Blockers: delete-before-save loss; depends on safe replacement fix
Source: `SPDWEBAPP/HOME/models.py:6–19`

```text
GIVEN committed singleton A and an unrelated slide/file sentinel
  AND first replacement insert is deliberately failed
WHEN the failed direct replacement is retried after removing the injected error
THEN first error must leave A usable and unchanged
  AND retry returns normally with exactly one new singleton value
  AND no duplicate replacement row remains
  AND sentinel slide/file and opposite singleton remain unchanged
  AND old/new file retention follows the separate Q7 decision
```

### HOME-T10d — test_successful_replacement_and_delete_file_retention_policy

Parent: `HOME-T10` | Operation: `HOME-O06, HOME-O07, HOME-O08` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q7 retain old files versus delete-on-commit/retention window
Source: `SPDWEBAPP/HOME/models.py:3–32`

```text
GIVEN a banner and slide each reference real old synthetic image bytes
  AND an outside sentinel file plus opposite singleton are captured
WHEN image is replaced or the corresponding row is deleted in separate variants
THEN DB reflects replacement or deletion after success
  AND Q7 chooses retention, immediate safe cleanup or deferred cleanup
  AND exact old/new file existence assertions follow Q7
  AND unrelated sentinel bytes and opposite singleton remain unchanged
  AND a repeated ORM delete reports zero affected rows
```

### HOME-T10e — test_cleanup_and_orphan_failure_policy

Parent: `HOME-T10` | Operation: `HOME-O06, HOME-O08, HOME-O09` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q7 compensation boundary; no current file-delete hook
Source: `SPDWEBAPP/HOME/models.py:3–32`

```text
GIVEN old image bytes and new upload bytes in temporary_media
  AND a storage delete failure or DB failure after new bytes are written
WHEN direct replacement or business admin replacement/deletion is attempted separately
THEN Q7 chooses retention/compensation and handling of storage cleanup failures
  AND final result, rollback and file-residue assertions follow that choice
  AND prior valid content must not be silently lost on failure
  AND unrelated files, slide/link sentinels and actor identity stay unchanged
  AND DB rollback is never treated as proof of file rollback
```

### HOME-T11a — test_concurrent_singleton_replacement_conflict_policy

Parent: `HOME-T11` | Operation: `HOME-O06, HOME-O07` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q9 conflict winner; NEEDS_FIX singleton enforcement; PostgreSQL facility
Source: `SPDWEBAPP/HOME/models.py:6–19`

```text
GIVEN PostgreSQL independent connections and committed singleton A
  AND bounded barriers surround each replacement delete and base save
WHEN workers concurrently replace A with B and C
THEN committed state must not expose multiple singleton rows or lose all valid values
  AND Q9 chooses serialization/last-writer versus explicit conflict rejection
  AND return/exception and winning-value assertions follow that decision
  AND unrelated slide/link records and sentinel files remain unchanged
  AND orphan-file expectations also await Q7; SQLite cannot establish this result
```

### HOME-T11b — test_concurrent_first_singleton_create_policy

Parent: `HOME-T11` | Operation: `HOME-O06, HOME-O07` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q9 create conflict; NEEDS_FIX uniqueness; PostgreSQL facility
Source: `SPDWEBAPP/HOME/models.py:6–19`

```text
GIVEN PostgreSQL independent connections and an empty singleton table
  AND named opposite singleton and slide/file sentinels
WHEN two workers concurrently create first singleton B and C with bounded barriers
THEN committed state must contain at most one accepted singleton value
  AND Q9 chooses one successful create plus conflict or serialized replacement
  AND exact worker results and retained value follow that choice
  AND unrelated rows, relations and sentinel bytes remain unchanged
  AND file ownership and cleanup outcomes also depend on Q7
```

### HOME-T12a — test_slide_create_and_edit_persists_target_fields

Parent: `HOME-T12` | Operation: `HOME-O08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/models.py:24–32`

```text
GIVEN slide B and before = snapshot_scope([slide_B], files=[sentinel_image])
WHEN slide A is created with caption="First", order=0 and a synthetic image
  AND then A caption, image and order=7 are saved
THEN saves return normally and refreshed A has those exact final fields
  AND str(A) equals its new caption
  AND new image bytes exist under rush_slides/
  AND B fields and sentinel bytes remain unchanged
  AND old image retention remains a separate Q7 decision
```

### HOME-T12b — test_slide_integer_order_and_caption_boundary

Parent: `HOME-T12` | Operation: `HOME-O08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/models.py:24–30`

```text
GIVEN slides A and B with synthetic images and caption length 200
WHEN A.full_clean() and save() run for order -1, 0 and 2147483647 separately
THEN calls return normally and A reloads with that integer and 200-character caption
  AND ordering query includes both A and B
  AND a tie retains both rows without promising a stable tie order
  AND B fields and both image bytes remain unchanged
  AND no uniqueness or positivity rule is invented
  AND admin max-plus-one behavior is a separate test
```

### HOME-T12c — test_slide_row_delete_is_repeatable

Parent: `HOME-T12` | Operation: `HOME-O08` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/models.py:24–32`

```text
GIVEN slide A and slide B reference separate synthetic files
  AND before = snapshot_scope([slide_B], files=[image_A, image_B])
WHEN QuerySet.filter(pk=A.pk).delete() runs twice
THEN first delete removes A and second reports zero affected rows
  AND B fields and image bytes remain unchanged
  AND no replacement slide is inserted
  AND A old-file disposition is assessed only after Q7
  AND no session or audit event is assumed for direct ORM deletion
```
