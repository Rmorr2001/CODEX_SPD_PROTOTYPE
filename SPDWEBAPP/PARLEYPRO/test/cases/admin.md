# Domain-owned admin C03

Use the [shared fixture contract](../../../../docs/testing/fixture-contract.md).
Actor A uses `make_user(username="a", roles=(...))`; B uses username="b", and so on.
Missing-profile fixtures use `with_profile=False` with no roles/profile fields.
Requests use `login_actor`; CSRF cases use `csrf_client` and real cookie/token pairs.
Polls/current choices are explicit local ORM rows; current choices have no poll FK.
Unless overridden, open P starts at T-10 seconds with counts 0/0 and NULL end.
Closed H/K start at T-20 seconds and end T-1 with counts 0/0 unless overridden.
T is aware UTC 2026-01-15T18:00:00Z; T-1/T-2 mean one/two seconds earlier.
Use `at_time` for each consumed clock and refresh rows named by `snapshot_scope`.
Each equivalent input/actor variant resets its fixture; no request uses real member data.
Public actions create no files/admin logs; identity/roles and unmentioned rows stay unchanged.
These are proposed designs, not executed tests or approved policy.

Use shared `business` settings, active staff flags and actual Django permissions.
All listed permission codenames have app label PARLEYPRO; no role grants staff access.
URLs use `reverse("admin:PARLEYPRO_vote_poll_<action>")`, not a hard-coded prefix.
GET/denial creates no LogEntry. Permitted writes check action flags, object IDs,
changed fields, and no unrelated logs. The demo /admin/ block stays AUTHENTICATE-owned.

<a id="pp-31a"></a>

### PP-31a — test_admin_result_icon_labels_and_safe_html

Parent: `PP-31` | Operation: `PP-C03-ICON` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/admin.py:20–35`

```text
GIVEN SimpleTestCase with unsaved poll objects, with no database or request fixture
  AND count variants are (2,1), (1,2), (1,1), (0,0)
WHEN VotePollAdmin.poll_result_icon runs on each object
THEN labels/colors are Passed/green, Failed/red, Tied/gold and Tied/gold
  AND output is safe formatted HTML containing the corresponding ✔️, ❌ or ⚖️ symbol and span
  AND short_description is Result
  AND admin_order_field is Vote_Poll_Count_Yes
  AND database/session/file/audit state is untouched
```

<a id="pp-31b"></a>

### PP-31b — test_admin_result_column_sorts_by_yes_count

Parent: `PP-31` | Operation: `PP-C03-READ` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/admin.py:10–18,34–35`

```text
GIVEN active staff A has PARLEYPRO.view_vote_poll permission but no domain roles
  AND polls H1=2/0, H2=3/4, H3=1/0 have nonnull aggregates
  AND before = snapshot_scope([A, H1, H2, H3])
WHEN A GETs the business admin changelist with ?o=7, the ascending Result column
THEN response is 200 and poll PK order is [H3.id, H1.id, H2.id]
  AND display includes name, creator, start, end, Yes, No and Result columns
  AND sorting uses Yes count, not vote margin or Passed/Failed category
  AND assert_unchanged(before); no admin LogEntry is created
```

<a id="pp-32a"></a>

### PP-32a — test_admin_nullable_counts_do_not_crash_or_silently_rewrite

Parent: `PP-32` | Operation: `PP-C03-ICON` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-09: NULL semantics; DEF-04
Source: `SPDWEBAPP/PARLEYPRO/models.py:15–16`; `SPDWEBAPP/PARLEYPRO/admin.py:21–25`

```text
GIVEN active staff A has view_vote_poll permission
  AND ORM H variants have counts NULL/1, 1/NULL and NULL/NULL
  AND before = snapshot_scope([A, H])
WHEN icon formatting and an admin changelist GET encounter H
THEN neither path may raise an incidental comparison TypeError or return 500
  AND POL-09 must choose unknown display, zero interpretation, or explicit data repair
  AND rendered label and response follow that rule; DEF-04 requires a code fix
  AND assert_unchanged(before) unless separate explicit repair is invoked
```

<a id="pp-33a"></a>

### PP-33a — test_admin_denies_anonymous_and_nonstaff_domain_executive

Parent: `PP-33` | Operation: `PP-C03-READ` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–9`

```text
GIVEN business settings; A variants are anonymous or nonstaff EXEC plus ACTIVE
  AND B owns poll H; before = snapshot_scope([B, H])
WHEN each actor GETs admin poll changelist/add/change/delete URLs
THEN each response redirects to the admin login URL with the requested next path
  AND no protected poll form/content is disclosed
  AND assert_unchanged(before)
  AND no poll, choice or LogEntry row is created
  AND domain roles do not grant staff access
```

<a id="pp-33b"></a>

### PP-33b — test_admin_staff_without_model_permissions_cannot_read_or_write

Parent: `PP-33` | Operation: `PP-C03-WRITE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–9`

```text
GIVEN business settings; active staff A has no model permissions or domain roles
  AND B owns H and has Nay; before = snapshot_scope([A, B, H, B_choice])
WHEN A GETs poll changelist/add/change/delete and POSTs change or delete
  AND POSTs include a real CSRF cookie/token pair
THEN protected model endpoints return 403
  AND H and B_choice are unchanged; no new poll exists
  AND assert_unchanged(before)
  AND no LogEntry row is created
```

<a id="pp-33c"></a>

### PP-33c — test_admin_view_only_actor_cannot_post_change_or_delete

Parent: `PP-33` | Operation: `PP-C03-WRITE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–18`

```text
GIVEN business settings; active staff A has only PARLEYPRO.view_vote_poll
  AND B owns H and has Nay; before = snapshot_scope([A, B, H, B_choice])
WHEN A GETs changelist/change, then POSTs a changed name and delete confirmation
  AND both POSTs carry a real CSRF cookie/token pair
THEN read GETs are 200; mutation POSTs are 403
  AND add GET is also 403 and H still exists with original fields
  AND assert_unchanged(before)
  AND no poll or LogEntry row is inserted
```

<a id="pp-33d"></a>

### PP-33d — test_admin_granular_permissions_gate_corresponding_actions

Parent: `PP-33` | Operation: `PP-C03-WRITE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–9`

```text
GIVEN business settings; active staff A has no domain roles
  AND isolated permissions are add_vote_poll, change_vote_poll or delete_vote_poll
  AND B owns H; before = snapshot_scope([A, B, H])
WHEN A requests GET add/change/delete forms in each permission variant
THEN only the corresponding action form is permitted; other action forms are 403
  AND no mutation is performed by these GET permission probes
  AND assert_unchanged(before); no new poll or LogEntry exists
  AND superuser variant permits all three forms without domain-role requirements
```

<a id="pp-33e"></a>

### PP-33e — test_inactive_staff_is_not_admitted_to_admin

Parent: `PP-33` | Operation: `PP-C03-READ` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–9`

```text
GIVEN make_user(username="a", is_staff=True, is_active=False) creates A
  AND A has all poll model permissions; B owns H
  AND before = snapshot_scope([A, B, H])
WHEN login_actor(client, A); GET the business admin poll changelist
THEN response redirects to admin login
  AND inactive status is not bypassed by staff/model permissions
  AND assert_unchanged(before)
  AND no poll, choice or LogEntry row is created
```

<a id="pp-34a"></a>

### PP-34a — test_admin_add_has_explicit_creator_and_history_policy

Parent: `PP-34` | Operation: `PP-C03-WRITE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-09/POL-04: admin creator/lifecycle scope
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–35`; `SPDWEBAPP/PARLEYPRO/models.py:12–18`

```text
GIVEN active staff A has add_vote_poll permission; ACTIVE B exists
  AND B has Nay; before = snapshot_scope([A, B, B_choice])
WHEN A POSTs admin add with name "Admin motion", created_by=B, counts 0/0, end blank
  AND request includes a real CSRF cookie/token pair
THEN POL-09/POL-04 must choose explicit creator assignment or actor-bound creation
  AND response/new poll ownership follows that chosen rule
  AND permitted add creates one correct Django ADDITION LogEntry, no unrelated logs
  AND assert_unchanged(before); choices must not reset
```

<a id="pp-34b"></a>

### PP-34b — test_admin_invalid_poll_form_preserves_database

Parent: `PP-34` | Operation: `PP-C03-WRITE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–9`; `SPDWEBAPP/PARLEYPRO/models.py:13–18`

```text
GIVEN active staff A has add/change_vote_poll permissions; B owns H and has Nay
  AND before = snapshot_scope([A, B, H, B_choice])
WHEN separate admin POSTs omit name/creator, exceed 200 name characters
  AND submit a noninteger count "abc" or malformed end date "bad-date"
THEN responses are 200 with corresponding required/max_length/type/date form errors
  AND no new poll is inserted and an existing H edit is not persisted
  AND assert_unchanged(before)
  AND no successful ADDITION/CHANGE LogEntry is created
```

<a id="pp-34c"></a>

### PP-34c — test_admin_history_fields_have_explicit_edit_contract

Parent: `PP-34` | Operation: `PP-C03-WRITE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-09: mutable history fields and audit
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–35`; `SPDWEBAPP/PARLEYPRO/models.py:12–18`

```text
GIVEN active staff A has change_vote_poll permission; B owns closed H
  AND ACTIVE C exists; B has Nay; before = snapshot_scope([A, B, C, H, B_choice])
WHEN A POSTs changed name, creator C, counts 8/3 and a different end datetime
THEN POL-09 must name editable history fields and any coordinated transition
  AND rejected changes preserve H and produce no successful CHANGE log
  AND accepted changes alter only approved fields and record one CHANGE LogEntry
  AND B_choice, profiles/roles and unrelated polls remain unchanged
  AND response follows the selected reject-or-save rule
```

<a id="pp-34d"></a>

### PP-34d — test_admin_single_delete_has_explicit_retention_contract

Parent: `PP-34` | Operation: `PP-C03-WRITE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-09: poll/history deletion retention
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–9`; `SPDWEBAPP/PARLEYPRO/models.py:12–18`

```text
GIVEN active staff A has delete_vote_poll permission; B owns H1 and H2
  AND B has Aye; before = snapshot_scope([A, B, H1, H2, B_choice])
WHEN A GETs H1 delete confirmation then POSTs confirmation with real CSRF token
THEN POL-09 must choose reject/protect, soft retention, or authorized hard deletion
  AND response, H1 existence and DELETION LogEntry follow that selected rule
  AND H2, B_choice, users/profiles/roles must remain unchanged
  AND no user or choice may be deleted as a side effect of deleting H1
  AND no unrelated admin audit entry is added
```

<a id="pp-34e"></a>

### PP-34e — test_admin_bulk_delete_has_explicit_confirmation_and_retention

Parent: `PP-34` | Operation: `PP-C03-WRITE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-09: bulk deletion retention
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–9`

```text
GIVEN active staff A has delete_vote_poll permission; B owns H1/H2/H3
  AND B has Nay; before = snapshot_scope([A, B, H1, H2, H3, B_choice])
WHEN A selects H1/H2 with action=delete_selected, then confirms with real CSRF token
THEN selection alone cannot remove rows before the confirmation step
  AND POL-09 must define rejection, soft retention or authorized hard deletion
  AND only H1/H2 may be affected; H3/B_choice/users/profiles remain unchanged
  AND permitted delete records corresponding DELETION logs and no unrelated logs
  AND response and retained fields follow that selected rule
```

<a id="pp-35a"></a>

### PP-35a — test_admin_close_cannot_bypass_count_reset_protocol

Parent: `PP-35` | Operation: `PP-C03-WRITE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-09/POL-06: admin lifecycle bypass; DEF-03
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–35`; `SPDWEBAPP/PARLEYPRO/pp_functions.py:24–41`

```text
GIVEN active staff A has change_vote_poll and EXEC plus ACTIVE
  AND A owns open P and has Aye; ACTIVE B has Nay
WHEN A admin-edits P end/counts, then POSTs /poll/ with {end_vote: "1"}
THEN POL-09/POL-06 must choose reject-direct-close or coordinated close/reset
  AND no accepted protocol may leave silently stranded current choices
  AND finalized totals/end and CHANGE log follow that named transition
  AND P's creator/name/start and choice PK/user ownership remain unchanged
  AND public close must not reconstruct missing historical ballots
```

<a id="pp-35b"></a>

### PP-35b — test_admin_reopen_cannot_silently_overwrite_history

Parent: `PP-35` | Operation: `PP-C03-WRITE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-01/POL-09: reopening and historical immutability
Source: `SPDWEBAPP/PARLEYPRO/admin.py:8–35`; `SPDWEBAPP/PARLEYPRO/pp_functions.py:24–41`

```text
GIVEN active staff A has change_vote_poll and EXEC plus ACTIVE
  AND A owns closed P with counts 5/2 and end T; A has a new Nay choice
WHEN A clears P's end through admin and POSTs {end_vote: "1"} publicly
THEN POL-01/POL-09 must choose forbidden reopen or an explicit new lifecycle
  AND old finalized history must not be overwritten as an incidental edit
  AND response, logs and stored history follow that selected rule
  AND actor roles, choice ownership and unrelated history remain unchanged
  AND reopening must not invent per-poll individual ballots
```

<a id="pp-35c"></a>

### PP-35c — test_admin_negative_counts_have_explicit_validation_policy

Parent: `PP-35` | Operation: `PP-C03-WRITE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-09: aggregate value range
Source: `SPDWEBAPP/PARLEYPRO/models.py:15–16`; `SPDWEBAPP/PARLEYPRO/admin.py:8–35`

```text
GIVEN active staff A has change_vote_poll; ACTIVE B owns closed H
  AND before = snapshot_scope([A, B, H])
WHEN A admin-POSTs counts -1/2, then separately 2/-1 with a real CSRF token
THEN POL-09 must choose nonnegative validation or an explicit exceptional domain rule
  AND rejection redisplays errors and preserves H with no CHANGE log
  AND any allowed exception must define display/result semantics and audit output
  AND H's creator/name/start and all choices remain unchanged
  AND integer parsing alone is not evidence that negative totals are legitimate
```
