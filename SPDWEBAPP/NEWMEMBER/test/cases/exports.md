# Exports case designs

Use [the shared fixture contract](../../../../docs/testing/fixture-contract.md) and
[local fixture vocabulary and scope rules](../regression-spec.md#local-fixture-vocabulary).
All fixtures are created independently inside each case; none carry from earlier cases.
Non-admin relative routes in blocks are under `/newmember/`.
[Source, defects and decisions](../regression-spec.md) supply the linked policy gates.

### NM-07-01a — test_export_current_workbook_has_signed_approved_values

Parent: `NM-07-01` | Operation: `NM-N07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:197–329`

```text
GIVEN ACTIVE A and distinct-name NEW_MEMBER T1/T2; T1 approved +5 Oct14/-8 Oct16
  AND T2 approved +2; requested/denied noise and historical ALUMNI B approved +90
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs export-newmember-marks/?pclass=Current under /newmember/
  AND openpyxl loads response bytes with data_only=False
THEN status=200,XLSX MIME,attachment Approved_Current_Class_Newmember_Marks.xlsx
  AND sheet is New Member Marks; alphabetical name blocks start at columns 1,6
  AND row3 headers are Date/Requesting Member/Reason/Mark Value; spacer column is blank
  AND T1 rows have ISO dates ascending, correct requester/reason, numeric 5/-8,total "Total: -3"
  AND B/unapproved rows are absent; all named rows/roles/files/session identity are unchanged
  AND assert_unchanged(before)
```

### NM-07-01b — test_historical_export_scope_needs_audience_policy

Parent: `NM-07-01` | Operation: `NM-N07` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q07 historical export audience
Source: `SPDWEBAPP/NEWMEMBER/views.py:193–217`

```text
GIVEN ACTIVE A, ALUMNI B with pclass Alpha, NEW_MEMBER T1 with pclass Beta
  AND B approved +5/-8, requested +99; T1 approved +20
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs export-newmember-marks/?pclass=Alpha under /newmember/
THEN Q07 chooses audience; allowed response is XLSX attachment
      Approved_Alpha_Class_Newmember_Marks.xlsx
  AND allowed workbook contains B approved rows oldest first,total "Total: -3",no T1/requested
  AND role NEW_MEMBER is not required for historical class membership
  AND rejected audience sees no workbook member data
  AND all named rows/roles/files/session identity are unchanged
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-07-02a — test_new_member_current_export_is_allowed

Parent: `NM-07-02` | Operation: `NM-N07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:193–200`

```text
GIVEN viewer A has roles NEW_MEMBER or NEW_MEMBER+NM_BOARD, separate variants
  AND A and T1 are current NEW_MEMBER with distinct-name approved marks
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs /newmember/export-newmember-marks/?pclass=Current
THEN response is 200 XLSX, not a previous-class permission redirect
  AND parsed workbook includes only current NEW_MEMBER approved marks
  AND values/types/totals agree with persisted signed integer marks
  AND no historical-only target block appears
  AND named marks/users/profiles/roles/files/session identity are unchanged
  AND assert_unchanged(before)
```

### NM-07-02b — test_previous_class_export_role_precedence_needs_policy

Parent: `NM-07-02` | Operation: `NM-N07` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q01 selector semantics; Q07 audience and role precedence
Source: `SPDWEBAPP/NEWMEMBER/views.py:193–203`

```text
GIVEN viewers NEW_MEMBER, NEW_MEMBER+NM_BOARD, (), ALUMNI or NM_BOARD
  AND historical Alpha marks plus unrelated Z
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN each GETs export with pclass "Alpha",omitted,"","Unknown"
THEN Q07 chooses audience and NEW_MEMBER+board role precedence
  AND Q01 chooses class selector validation versus empty historical export
  AND permitted workbook matches exact selected class; denied output reveals no historical data
  AND response cannot silently claim a different class scope
  AND marks/users/roles/files/session identity remain unchanged
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-07-03a — test_duplicate_names_never_merge_member_identities

Parent: `NM-07-03` | Operation: `NM-N07` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D07 full-name dictionary key merges distinct users; Q09 display label
Source: `SPDWEBAPP/NEWMEMBER/views.py:220–229`

```text
GIVEN distinct NEW_MEMBER T1/T2 both named "Sam Same"
  AND T1 approved +5 and T2 approved -8; ACTIVE exporter A
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A exports Current and response bytes are parsed with data_only=False
THEN two independent identities and per-target event groups are retained
  AND no merged "Total: -3" substitutes for T1 total 5 and T2 total -8
  AND each row remains attached to its original target identity
  AND exact label disambiguation is left to Q09 without weakening separation
  AND named rows/roles/files/session identity are unchanged
  AND assert_unchanged(before)
```

### NM-07-04a — test_formula_like_export_text_remains_literal

Parent: `NM-07-04` | Operation: `NM-N07` | Priority: P0
Status: `NEEDS_FIX` | Blockers: D08 direct openpyxl values can create formulas; Q09 encoding strategy
Source: `SPDWEBAPP/NEWMEMBER/views.py:265,286`

```text
GIVEN ACTIVE exporter A and NEW_MEMBER T1 with approved integer value=-3
  AND target name, requester name or reason begins "=1+1","+SUM(1,2)","-1+2","@SUM(1,2)"
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN Current XLSX is exported; parameterize each text field/string independently
  AND load response bytes with openpyxl,data_only=False
THEN every untrusted text cell has literal text value and data_type not "f"
  AND no extra visible apostrophe corrupts the original text value
  AND mark value remains numeric -3; signed total remains "Total: -3"
  AND marks/users/roles/files/session identity remain unchanged
  AND assert_unchanged(before)
```

### NM-07-05a — test_empty_current_export_is_a_valid_workbook

Parent: `NM-07-05` | Operation: `NM-N07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:231–236,315–330`

```text
GIVEN ACTIVE A and current NEW_MEMBER T1 with no approved marks
  AND requested/denied rows only; historical approved M belongs to ALUMNI B
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A exports Current; separate variant has no NEW_MEMBER profiles at all
THEN response is 200 with expected Current filename and XLSX MIME
  AND workbook opens with sheet New Member Marks and no member data blocks
  AND no historical/unapproved row appears
  AND the named fixture rows and mark count are unchanged
  AND no stored files or authenticated identity changes occur
  AND assert_unchanged(before)
```

### NM-07-05b — test_export_requester_without_profile_uses_username

Parent: `NM-07-05` | Operation: `NM-N07` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:205–229`

```text
GIVEN ACTIVE A, requester B=make_user(username="requester-fallback",with_profile=False)
  AND NEW_MEMBER T1 has B's approved mark M; unrelated Z exists
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A exports Current and parses XLSX values/types
THEN response is 200; Requesting Member cell is literal "requester-fallback"
  AND date/reason/signed value/target name come from M and T1
  AND no missing-profile exception occurs for B
  AND all M/Z/user/profile/role fields remain unchanged
  AND no stored files or authenticated identity changes occur
  AND assert_unchanged(before)
```

### NM-07-05c — test_workbook_save_failure_returns_controlled_error

Parent: `NM-07-05` | Operation: `NM-N07` | Priority: P1
Status: `NEEDS_FIX` | Blockers: D09 uncaught workbook save error
Source: `SPDWEBAPP/NEWMEMBER/views.py:315–330`

```text
GIVEN ACTIVE A, NEW_MEMBER T1 approved M and unrelated Z
  AND deliberately inject Workbook.save RuntimeError before bytes are returned
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs /newmember/export-newmember-marks/?pclass=Current
THEN controlled non-success replaces uncaught exception and no attachment is returned
  AND response contains no raw traceback or partial workbook
  AND fresh M/Z/users/profiles/roles remain unchanged
  AND temporary_media has no new persisted files
  AND authenticated identity and mark count remain unchanged
  AND assert_unchanged(before)
```
