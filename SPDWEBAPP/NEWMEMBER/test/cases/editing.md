# Editing case designs

Use [the shared fixture contract](../../../../docs/testing/fixture-contract.md) and
[local fixture vocabulary and scope rules](../regression-spec.md#local-fixture-vocabulary).
All fixtures are created independently inside each case; none carry from earlier cases.
Non-admin relative routes in blocks are under `/newmember/`.
[Source, defects and decisions](../regression-spec.md) supply the linked policy gates.

### NM-03-01a — test_edit_form_prefills_single_target

Parent: `NM-03-01` | Operation: `NM-N03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:168–175`

```text
GIVEN NM_BOARD R and A's approved M for NEW_MEMBER T1
  AND NEW_MEMBER T2 plus unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R GETs /newmember/edit/M.id/
THEN response is 200 request template with editing=True
  AND reason/value/date match M and target_user is single select with T1 selected
  AND T2 is another choice; action update and deny buttons exist
  AND the named fixture rows and mark count are unchanged
  AND authenticated identity remains R
  AND assert_unchanged(before)
```

### NM-03-01b — test_board_edit_retargets_and_sets_editor_only

Parent: `NM-03-01` | Operation: `NM-N03` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:147–166`

```text
GIVEN board-only R, A's M for NEW_MEMBER T1 and NEW_MEMBER T2, unrelated Z
  AND M status parameterized requested/approved/denied; at_time(2026-10-17T12:00Z)
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R POSTs edit/M.id/ with {action:"update",mark_reason:"Lab",
  mark_value:"-2"/"0"/"3",mark_date:"2026-10-16",target_user:T2.id}
THEN redirect is history/T2.id/; M content matches payload and target becomes T2
  AND last_edited_by=R,last_edited_at=frozen time
  AND status/requester/approval name/time/submission time remain unchanged
  AND mark count, Z/users/roles/session identity are unchanged
  AND assert_unchanged(before,
      except_fields={M:{mark_event_title,mark_value,mark_event_date,target_user,last_edited_by,last_edited_at}})
```

### NM-03-02a — test_nonexistent_retarget_leaves_entire_mark_unchanged

Parent: `NM-03-02` | Operation: `NM-N03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:152–159`

```text
GIVEN board R, A's approved M for T1 and unrelated Z; ID 999999 absent
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R POSTs edit/M.id/ with {action:"update",mark_reason:"Lab",mark_value:"-2",
  mark_date:"2026-10-16",target_user:"999999"}
THEN response redirects back to edit/M.id/ with invalid-target error
  AND fresh M retains original title/value/date/target/status
  AND requester/submission/approval/editor audit are unchanged
  AND the named fixture rows plus count and session identity are unchanged
  AND in-memory assignments before lookup are not mistaken for saved writes
  AND assert_unchanged(before)
```

### NM-03-02b — test_malformed_edit_cannot_crash_or_partially_save

Parent: `NM-03-02` | Operation: `NM-N03` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D06 raw edit parsing/save errors
Source: `SPDWEBAPP/NEWMEMBER/views.py:148–163`

```text
GIVEN board R, A's M for T1 and unrelated Z; base edit is update/Lab/-2/2026-10-16/T1
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN one field is omitted or malformed per fresh fixture:
  value omitted,"","abc","1.5"; date omitted,"bad","2026-02-30";
  reason omitted; target_user="abc"
THEN controlled non-success replaces uncaught parsing/database errors
  AND no raw exception details reach response
  AND every M field, Z/users/roles and mark count remain unchanged after fresh reads
  AND session identity stays R
  AND assert_unchanged(before)
```

### NM-03-02c — test_edit_save_failure_preserves_database_state

Parent: `NM-03-02` | Operation: `NM-N03` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D06 uncaught save failure
Source: `SPDWEBAPP/NEWMEMBER/views.py:161–163`

```text
GIVEN board R, M for T1 and unrelated Z; inject M.save failure before SQL
  AND declare T2 using the linked local fixture vocabulary
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R POSTs update/Lab/-2/2026-10-16/T2 to edit/M.id/
THEN response is a controlled non-success rather than an uncaught exception
  AND every M content/target/status/requester/submission/approval/editor field is unchanged
  AND Z, R, T1, T2 users/profiles/roles are unchanged
  AND mark count and authenticated session identity stay unchanged
  AND no successful history redirect is returned
  AND a fresh database read, not mutated Python object, establishes preservation
  AND assert_unchanged(before)
```

### NM-03-02d — test_omitted_or_identical_retarget_needs_field_policy

Parent: `NM-03-02` | Operation: `NM-N03` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q02 required versus optional target field
Source: `SPDWEBAPP/NEWMEMBER/views.py:152–153`

```text
GIVEN board R, M for T1 and unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN edit POST uses update/Lab/-2/2026-10-16 and target_user omitted,"",or T1.id
THEN Q02 chooses optional-retarget preservation versus required-target rejection
  AND accepted variants retain T1, update content/editor audit and redirect T1 history
  AND rejected variants preserve every field and produce non-success
  AND status/requester/submission/approval audit and Z stay unchanged
  AND users/roles/session identity remain unchanged
  AND current optional branch is recorded without deciding future requiredness
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-03-02e — test_edit_content_boundaries_need_policy

Parent: `NM-03-02` | Operation: `NM-N03` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q02 content/value/date limits
Source: `SPDWEBAPP/NEWMEMBER/views.py:148–163; models.py:23–31`

```text
GIVEN NM_BOARD R, A's approved M for NEW_MEMBER T1 and unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN edit/M.id/ POST overrides update/Lab/-2/2026-10-16/T1 with reason "",
  100 or 101 x's, value "2147483647","2147483648","-2147483649", or date "2026-10-18"
THEN Q02 chooses content limits and future-date allowance for regular edits
  AND accepted input changes only content/editor audit and redirects to T1 history
  AND rejected input preserves every M field and produces controlled non-success
  AND status/requester/target/submission/approval audit stay unchanged
  AND Z/users/roles/session identity remain unchanged
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-03-03a — test_edit_target_eligibility_needs_policy

Parent: `NM-03-03` | Operation: `NM-N03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q01 edit target eligibility
Source: `SPDWEBAPP/NEWMEMBER/views.py:152–156`

```text
GIVEN board R, M for NEW_MEMBER T1, ALUMNI B and profileless C
  AND declare Z using the linked local fixture vocabulary
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN update/Lab/-2/2026-10-16 retargets to B.id,C.id,R.id separately
THEN Q01 chooses eligibility for non-new-member, profileless and self targets
  AND rejection preserves entire M; acceptance changes only content/target/editor audit
  AND permitted redirect must reference the persisted target
  AND status/requester/submission/approval audit remain unchanged
  AND unrelated Z, users/roles and session identity are unchanged
  AND current arbitrary User lookup is not an inferred eligibility policy
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-03-03b — test_unknown_edit_action_needs_transport_policy

Parent: `NM-03-03` | Operation: `NM-N03` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q02 unknown edit action
Source: `SPDWEBAPP/NEWMEMBER/views.py:130–149`

```text
GIVEN board R and M for NEW_MEMBER T1 plus unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN POST edit/M.id/ uses action omitted,"","archive" and Lab/-2/2026-10-16/T1
THEN Q02 chooses explicit update-only rejection or documented default-update behavior
  AND rejection preserves M; update changes only title/value/date/editor audit
  AND response and actual update agree, with no deny transition
  AND M requester/target/status/submission/approval audit remain unchanged
  AND Z/users/roles/session identity stay unchanged
  AND no unknown action is interpreted as an approval
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-03-04a — test_missing_edit_resource_returns_404

Parent: `NM-03-04` | Operation: `NM-N03,NM-N04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:128; urls.py:11`

```text
GIVEN NM_BOARD+NME R and unrelated M; mark ID 999999 absent
  AND declare T1 using the linked local fixture vocabulary
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN GET or POST edit/999999/ and edit/not-an-int/ under /newmember/
  AND POST uses action="deny" or update/Lab/-2/2026-10-16/T1
THEN each response is 404
  AND no success message or target history redirect is produced
  AND the named fixture rows and mark count remain unchanged
  AND authenticated session identity remains R
  AND malformed path is rejected by the integer URL converter
  AND assert_unchanged(before)
```

### NM-04-01a — test_educator_board_edit_deny_sets_both_audits

Parent: `NM-04-01` | Operation: `NM-N04` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:133–145`

```text
GIVEN NM_BOARD+NME R named "Rae Reviewer", A's requested M for T1 and Z
  AND at_time(2026-10-17T12:00Z); R is neither requester nor target
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R POSTs /newmember/edit/M.id/ with {action:"deny"}
THEN response redirects to marks dashboard with successful-denial message
  AND M becomes denied with approver "Rae Reviewer", approval time frozen
  AND last_edited_by=R,last_edited_at=frozen time
  AND requester/target/title/value/event/submission fields are unchanged
  AND Z/users/roles/mark count/session identity remain unchanged
  AND assert_unchanged(before,
      except_fields={M:{mark_approval_status,mark_approver_name,mark_submission_approval_date,last_edited_by,last_edited_at}})
```

### NM-04-01b — test_deny_endpoint_permission_difference_needs_policy

Parent: `NM-04-01` | Operation: `NM-N02,NM-N04` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q05 endpoint-specific deny roles
Source: `SPDWEBAPP/NEWMEMBER/views.py:72,124–135`

```text
GIVEN NM_BOARD-only R and two identical pending marks M1/M2
  AND declare Z using the linked local fixture vocabulary
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R sends deny for M1 to approve/ and deny for M2 to edit/M2.id/
THEN current paths respectively allow and deny, as isolated READY cases establish
  AND Q05 chooses whether to retain the distinction or unify the roles
  AND final denial leaves row unchanged; final permission changes only chosen audit/status fields
  AND no content/requester/target/submission changes occur
  AND unrelated Z/users/roles/session identity remain unchanged
  AND visible button and browser confirmation do not settle Q05
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-04-02a — test_repeat_override_or_self_edit_deny_needs_policy

Parent: `NM-04-02` | Operation: `NM-N04` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q04 transitions/self/audit; Q05 override authority
Source: `SPDWEBAPP/NEWMEMBER/views.py:133–142`

```text
GIVEN NM_BOARD+NME R, M approved or denied, and separate self-request/self-target variants
  AND advance at_time from 2026-10-17T12:00Z to 13:00Z between repeated denials
  AND declare Z using the linked local fixture vocabulary
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R POSTs action="deny" to edit/M.id/ twice
THEN Q04/Q05 choose rejection, idempotence or authorized override and audit retention
  AND chosen response matches actual status/approval/editor audit outcome
  AND rejected/no-op outcomes retain original audit; overrides follow chosen new audit contract
  AND requester/target/content/submission plus Z/users/roles remain unchanged
  AND session identity is unchanged; JS irreversible wording is not a server guarantee
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-04-02b — test_edit_deny_save_failure_preserves_both_audits

Parent: `NM-04-02` | Operation: `NM-N04` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D06 uncaught edit-deny save failure
Source: `SPDWEBAPP/NEWMEMBER/views.py:137–142`

```text
GIVEN NM_BOARD+NME R, requested M for T1 and unrelated Z
  AND deliberately fail M.save before SQL after denial/editor fields are assigned
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN R POSTs edit/M.id/ with {action:"deny"}
THEN controlled non-success replaces an uncaught save exception
  AND fresh M retains original status, approval name/time and editor name/time
  AND content/requester/target/submission fields remain unchanged
  AND Z/users/roles/mark count/session identity are unchanged
  AND no successful denial redirect/message is emitted
  AND assert_unchanged(before)
```
