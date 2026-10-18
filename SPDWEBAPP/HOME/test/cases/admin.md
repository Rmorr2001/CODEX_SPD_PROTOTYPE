# HOME admin and reorder

Uses business settings, never the public demo admin boundary.

### HOME-T13a — test_admin_anonymous_and_nonstaff_are_denied

Parent: `HOME-T13` | Operation: `HOME-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11`

```text
GIVEN business settings with the synthetic admin mount and each HOME model row
  AND actors are anonymous or nonstaff with ACTIVE, EXEC or model permissions
WHEN each GETs list/add/change/delete/history URLs or POSTs a change
THEN admin redirects to its named login with a safe local next target
  AND no business role alone grants site access
  AND captured rows, files and admin LogEntry rows remain unchanged
  AND authenticated identity remains the original actor
  AND demo-wide blocking is AUTHENTICATE coverage, not this test
```

### HOME-T13b — test_admin_individual_model_permissions_are_distinct

Parent: `HOME-T13` | Operation: `HOME-O09` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11`

```text
GIVEN business staff with only view, add, change or delete HOME model permission
  AND separate model A/B rows and files; each variant has a captured admin log
WHEN staff directly requests an action for which its permission is absent
THEN action is 403 even if UI buttons were bypassed
  AND view/change permissions do not imply add/delete grants
  AND allowed view/changelist access renders without mutation
  AND target A, unrelated B, file bytes and admin log remain unchanged
  AND each model is tested with its own actual Django permissions
```

### HOME-T13c — test_admin_unsafe_requests_require_real_csrf

Parent: `HOME-T13` | Operation: `HOME-O09, HOME-O10` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11`

```text
GIVEN business staff has exact action permission and csrf_client is logged in
  AND a GET add/change form supplies a real CSRF cookie/token pair
WHEN add/change/delete/delete_selected or sortable POST has absent or bad token
THEN response is 403 before mutation
  AND captured model rows/orders, files and LogEntry rows remain unchanged
  AND session actor identity remains unchanged
  AND separate success cases supply that acquired token
  AND default test-client CSRF bypass is not evidence
```

### HOME-T13d — test_admin_superuser_can_read_home_models

Parent: `HOME-T13` | Operation: `HOME-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11`

```text
GIVEN business settings and make_user(username="admin-reader", is_staff=True,
  AND is_superuser=True) with no domain roles and explicit synthetic rows/files
WHEN login_actor user GETs each HOME model list/change/history URL
THEN each response is 200 with the expected row or history form
  AND no domain role is needed for the superuser grant
  AND row values, file bytes and LogEntry rows remain unchanged
  AND session identity remains admin-reader
  AND this actor is never used as a seed success fixture
```

### HOME-T14a — test_admin_invalid_forms_do_not_run_singleton_hooks

Parent: `HOME-T14` | Operation: `HOME-O09, HOME-O06, HOME-O07, HOME-O08` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11; SPDWEBAPP/HOME/models.py:3–32`

```text
GIVEN business staff with exact add/change permission and acquired CSRF token
  AND existing target A plus unrelated B and their real synthetic image bytes
WHEN add/change form submits empty required field, malformed URL or invalid image bytes
  AND caption or URL length 201 is also tested as a separate field variant
THEN response is 200 with the relevant field errors
  AND no successful admin redirect occurs
  AND A, B, file bytes and LogEntry rows remain unchanged
  AND destructive singleton save hooks must not run on invalid forms
```

### HOME-T14b — test_admin_add_creates_home_row_and_audit

Parent: `HOME-T14` | Operation: `HOME-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11`

```text
GIVEN business staff with only the target model add permission and real CSRF token
  AND no target singleton; an unrelated opposite singleton and slide/image exist
WHEN staff POSTs a synthetic PNG banner, HTTPS link or 200-character slide caption
THEN response redirects to an allowed named admin success destination
  AND exactly one requested new row stores submitted fields and upload bytes
  AND LogEntry records ADDITION for the actor/model/object
  AND opposite singleton, unrelated slide and sentinel file are unchanged
  AND slide ordering assignment is verified separately by HOME-T15f
```

### HOME-T14c — test_admin_change_updates_home_row_and_audit

Parent: `HOME-T14` | Operation: `HOME-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11`

```text
GIVEN business staff with target model change permission and real CSRF token
  AND target A plus unrelated B and synthetic image bytes
WHEN staff changes A caption/link/image through its admin form and repeats the save
THEN each response redirects to an allowed named admin success destination
  AND refreshed content contains the submitted final fields without duplicates
  AND LogEntry records CHANGE for the submitted actor/model/object
  AND unrelated B, opposite singleton and sentinel bytes remain unchanged
  AND old-file cleanup and singleton PK identity remain Q7 decisions
```

### HOME-T14d — test_admin_delete_confirmation_and_cancel

Parent: `HOME-T14` | Operation: `HOME-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11`

```text
GIVEN business staff with target delete permission and acquired CSRF token
  AND A/B rows with synthetic files
WHEN staff GETs delete confirmation then navigates back without confirming
THEN confirmation is 200 and A/B rows, bytes and logs remain unchanged
WHEN staff POSTs confirmed deletion for A with post="yes"
THEN response redirects to the named allowed admin success destination
  AND A row is absent; B and opposite singleton remain unchanged
  AND LogEntry records DELETION; file cleanup is separately Q7-blocked
```

### HOME-T14e — test_admin_bulk_delete_removes_only_selected_rows

Parent: `HOME-T14` | Operation: `HOME-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11`

```text
GIVEN business staff with RushSlide delete permission and acquired CSRF token
  AND slides A, B, C have distinct real image files
WHEN delete_selected POST selects A/B, then confirmation POST includes post="yes"
THEN first response shows confirmation and second redirects after deletion
  AND A/B rows are absent; C and singleton rows are unchanged
  AND LogEntry records DELETION for A and B under that actor
  AND sentinel file bytes remain unchanged
  AND selected image-file disposition remains governed by Q7
```

### HOME-T14f — test_admin_stale_object_redirects_without_writes

Parent: `HOME-T14` | Operation: `HOME-O09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11`

```text
GIVEN business staff with model change/delete permission and real CSRF token
  AND A row was deleted before staff uses its remembered PK
WHEN staff GETs or POSTs the stale A change/delete URL
THEN Django redirects to its admin index missing-object flow
  AND no replacement A row appears
  AND unrelated B, singleton rows and image bytes remain unchanged
  AND no new successful CHANGE or DELETION log for A is written
  AND any warning message may change while session identity stays fixed
```

### HOME-T14g — test_admin_db_failure_rolls_back_singleton_and_audit

Parent: `HOME-T14` | Operation: `HOME-O09, HOME-O06, HOME-O07` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11; SPDWEBAPP/HOME/models.py:6–19`

```text
GIVEN business staff with change permission and CSRF token; committed singleton A
  AND TransactionTestCase with prior LogEntry and opposite singleton snapshots
WHEN replacement base insert raises IntegrityError during admin save
THEN injected failure propagates without a successful redirect
  AND after leaving admin atomic scope, A DB value is restored
  AND no successful CHANGE log is committed
  AND opposite singleton and old image bytes remain unchanged
  AND new upload residue is explicitly outside this DB rollback assertion
```

### HOME-T15a — test_sortable_requires_post_and_change_permission

Parent: `HOME-T15` | Operation: `HOME-O10` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11 (SortableAdminMixin.update_order dependency)`

```text
GIVEN business staff with RushSlide view-only or change permission and real CSRF
  AND slides A/B orders 1/2 and a captured log/file snapshot
WHEN change staff GETs adminsortable2_update/ and view-only staff POSTs updatedItems=[]
THEN GET returns 405 and view-only POST returns 403
  AND nonstaff/anonymous admission remains denied by admin login
  AND A/B orders, captions, image bytes and logs remain unchanged
  AND session identities remain fixed
  AND dependency route is resolved via admin:HOME_rushslide_sortable_update
```

### HOME-T15b — test_sortable_updates_only_named_orders_and_repeats

Parent: `HOME-T15` | Operation: `HOME-O10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11 (SortableAdminMixin._update_order dependency)`

```text
GIVEN business staff with RushSlide change permission and acquired CSRF token
  AND slides A/B/C have orders 1/2/4 and captured captions/images
WHEN staff POSTs JSON {"updatedItems":[[A.pk,3],[B.pk,1]]} twice
THEN each response is 200 with Updated 2 items
  AND A/B reload with order 3/1; C remains order 4
  AND captions, image references/bytes and singleton rows remain unchanged
  AND no duplicate slide is created
  AND custom sortable audit requirements are separate Q10 policy
```

### HOME-T15c — test_sortable_malformed_batches_are_not_partially_written

Parent: `HOME-T15` | Operation: `HOME-O10` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11 (SortableAdminMixin.update_order dependency)`

```text
GIVEN business change staff, acquired CSRF token and slides A/B at orders 1/2
WHEN POST body is invalid JSON, {}, {"updatedItems":null} or {"updatedItems":[[]]}
  AND separately updatedItems is [[A.pk,9],[unknown_pk,1]]
THEN response is 400 and no earlier pair is partially applied
  AND A/B orders, captions, file bytes and singleton rows remain unchanged
  AND session identity remains unchanged
  AND unknown_pk is absent from RushSlide, even if it exists in another model
  AND sensitive exception disclosure is separately HOME-T15g
```

### HOME-T15d — test_sortable_empty_batch_is_noop

Parent: `HOME-T15` | Operation: `HOME-O10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11 (SortableAdminMixin.update_order dependency)`

```text
GIVEN business change staff with CSRF and slides A/B at orders 1/2
  AND before = snapshot_scope([slide_A, slide_B, banner, link], files=[image_A, image_B])
WHEN JSON {"updatedItems":[]} is POSTed to named sortable update route
THEN response is 200 with Updated 0 items
  AND A/B orders remain 1/2
  AND all captured rows and real image bytes remain unchanged
  AND no duplicate row or custom audit event is invented
  AND authenticated identity remains unchanged
```

### HOME-T15e — test_sortable_page_move_policy

Parent: `HOME-T15` | Operation: `HOME-O10` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q10 page bounds/audit; pinned action payload verification
Source: `SPDWEBAPP/HOME/admin.py:8–11` (SortableAdminMixin page actions)

```text
GIVEN business change staff with CSRF and more than one page of synthetic slides
  AND selected A/B and unselected C have captured orders, captions and image bytes
WHEN move actions use first/last/forward/back/exact-page boundary destinations
THEN Q10 chooses invalid destination handling and reorder audit requirements
  AND final response, selected orders and log assertions follow that decision
  AND unselected captions/image bytes and singleton rows remain unchanged
  AND concrete pinned action names/form payloads must be recorded before implementation
  AND invalid batches must not commit partial reorder writes
```

### HOME-T15f — test_admin_new_slide_uses_maximum_plus_one

Parent: `HOME-T15` | Operation: `HOME-O10` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/admin.py:5–11 (SortableAdminMixin.save_model dependency)`

```text
GIVEN business staff with RushSlide add permission and acquired CSRF token
  AND slides A/B have orders 3/7 and real synthetic images
WHEN staff adds C with caption="Third" and a synthetic PNG through admin
THEN response redirects after success
  AND C order is 8 regardless of omitted order form field
  AND A/B fields and image bytes remain unchanged
  AND singleton rows and sentinel file remain unchanged
  AND standard ADDITION log records C and that actor
```

### HOME-T15g — test_sortable_errors_do_not_disclose_database_detail

Parent: `HOME-T15` | Operation: `HOME-O10` | Priority: P0
Status: `NEEDS_FIX` | Blockers: dependency returns raw caught exception string; sanitize adapter
Source: `SPDWEBAPP/HOME/admin.py:5–11 (SortableAdminMixin.update_order dependency)`

```text
GIVEN business change staff with real CSRF and slides A/B
  AND bulk_update deliberately raises IntegrityError with synthetic private-detail canary
WHEN JSON {"updatedItems":[[A.pk,2],[B.pk,1]]} is POSTed
THEN response must be 400 without the canary or DB implementation detail
  AND A/B orders remain unchanged after failure
  AND captions, image bytes, singleton rows and actor identity remain unchanged
  AND a safe generic error replaces the raw exception text
  AND only synthetic exception data is used, never real database diagnostics
```

### HOME-T15h — test_sortable_noncanonical_order_policy

Parent: `HOME-T15` | Operation: `HOME-O10` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q10 duplicate PKs, ties, order types and audit
Source: `SPDWEBAPP/HOME/admin.py:8–11` (SortableAdminMixin.update_order)

```text
GIVEN business change staff with CSRF and slides A/B/C at orders 1/2/3
WHEN updatedItems repeats A.pk or supplies negative, tied, string or noninteger orders
THEN Q10 chooses rejection, normalization or explicit acceptance for each category
  AND exact response, affected orders and audit assertions follow that decision
  AND no invalid batch may commit partial reorder writes
  AND unrelated C caption/image bytes and singleton rows remain unchanged
  AND duplicate-PK last/first update semantics are not selected by this design
  AND authenticated identity remains unchanged
```
