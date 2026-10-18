# NEWMEMBER Wave 1 regression specification

## Provenance and source inventory

Inspected checkout `/workspace/CODEX-SPD-PROTOTYPE`, repository
`Rmorr2001/CODEX_SPD_PROTOTYPE`, actual branch `prototype/railway`, commit
`7e25ac2f06b2d88a0220526771585f30df10c57a`. Root `AGENTS.md` and
[the complete shared contract](../../../docs/testing/wave-1-agent-prompt.md)
were read; no nested AGENTS.md was found. All findings below are inspection,
not executed results. No application tests, network calls, credentials, private
uploads, Git mutations or dependency changes were used.

Documentation refinement baseline: `c8bbc4e94fdd135485c034981c0a25e09e902679`
(`c8bbc4e`), on the same `prototype/railway` branch. The source baseline above
remains the Wave 1 reference. [Wave 1.5 contract](../../../docs/testing/wave-1-5-agent-prompt.md)
and [fixture contract](../../../docs/testing/fixture-contract.md) govern this refinement.

Source keys below are repository-relative and include line numbers:

| Key | Inspected source and relevant symbols |
| --- | --- |
| U | `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:33`; `SPDWEBAPP/NEWMEMBER/urls.py:4–12`: seven mounted routes under `/newmember/` |
| V | `SPDWEBAPP/NEWMEMBER/views.py:9–175`: landing, dashboard, request, approve, history, edit; `:187–330`: export |
| F | `SPDWEBAPP/NEWMEMBER/views_functions.py:9–192`: all ten helpers, including single-role `check_user_role` |
| M | `SPDWEBAPP/NEWMEMBER/models.py:4–61`: status choices, signed IntegerField, audit fields, FK deletion, default ordering; no save override/clean/uniqueness constraint |
| A | `SPDWEBAPP/NEWMEMBER/admin.py:6–15`: registered default ModelAdmin/list_display only |
| T | `SPDWEBAPP/NEWMEMBER/templatetags/newmember_extras.py:5–7`: hours_remaining |
| R | `SPDWEBAPP/NEWMEMBER/templates/newmember_marks_request.html:11–69,223–234`: payload, CSRF, update/deny buttons and client confirmation |
| Q | `SPDWEBAPP/NEWMEMBER/templates/newmember_marks_approve.html:58–63,112–117`: mark_id/action POST, CSRF |
| D | `SPDWEBAPP/NEWMEMBER/templates/newmember_marks_dashboard.html:11–18,25–80,140–170`; `ACTIVE_newmember_marks_dashboard.html:12–13,61–77,103–136`: role UI, lists and exports |
| H | `SPDWEBAPP/NEWMEMBER/templates/newmember_marks_history.html:35–47`: approved rows, edited marker, board edit links; `newmember_dashboard.html:9–23`: public navigation |
| P | `SPDWEBAPP/AUTHENTICATE/models.py:8–77,88–127`: class choices, roles, profile and optional image save hook |
| X | `SPDWEBAPP/NEWMEMBER/tests.py:1–3`; `SPDWEBAPP/railway_demo/tests.py:31–38,58–72,79–97`; `railway_demo/middleware.py:5–10`: existing assertions/demo admin boundary |
| G | `SPDWEBAPP/NEWMEMBER/migrations/0001_initial.py`, `0002_alter_newmember_mark_event_and_request_requesting_user_and_more.py`, `0003_newmember_mark_event_and_request_last_edited_at_and_more.py:15–44`: schema evolution |

No local forms or JavaScript request module exists: raw POST parsing and inline
HTML/JS are the contract. All seven views are mounted. Helpers are used by views;
`check_user_role` is also imported by `AUTHENTICATE/views.py:15,28`. N08 is
registered but no NEWMEMBER template references it; the identically named
PHILANTHROPY filter is separate. Imports/comments are not permission enforcement.

## Operation inventory and current behavior

P = preserve supported behavior; D = defect target, never bless unsafe behavior
or a crash as a passing contract; Q = policy decision needed before final expected
behavior. Priorities: P0 authorization/data integrity, P1 domain correctness,
P2 presentation/pure utility. Legacy HTTP behavior belongs in adapter assertions;
domain outcomes stay reusable for DRF/React migration.

Ten operations, stable IDs including the shared map's N01–N07 and C03:

| Operation | Route/callable, actor and input | Current response and effects; classification/source |
| --- | --- | --- |
| NM-N00 | GET `/newmember/`; any visitor | Render `newmember_dashboard.html`, no marks writes; deliberately inspect anonymous render, no login decorator (P; V:9–10, H) |
| NM-N01 | GET/POST `request/`; ACTIVE; repeated target_users, mark_value, mark_reason, mark_date; `create_mark_requests` | GET eligible choices; POST int parsing before helper, success/error message then marks redirect. Bulk insert requested rows; ACTIVE+NM_BOARD auto-approved with name/time; requester from session. Helpers lack ACTIVE/target validation (P/D/Q; V:46–68,F:116–137,R) |
| NM-N02 | GET/POST `approve/`; NM_BOARD; mark_id/action; `process_mark_approval`, `get_pending_mark_requests` | Render pending requested rows descending event date; approve/deny update status/name/approval time, success message, same page. No helper auth/state guard; unknown action still saves and reports denied success (P/D/Q; V:70–91,F:140–175,Q) |
| NM-N03 | GET/POST `edit/<int:mark_id>/`; NM_BOARD; reason/value/date/target_user, non-deny action | Render prefilled request template; update one row, last editor/time, optional retarget, redirect new target history. Requester, approval audit/status remain. Invalid nonexistent target redirects edit without save; malformed parsing can crash; arbitrary existing User accepted (P/D/Q; V:121–175,R) |
| NM-N04 | POST same edit route, action=deny; NM_BOARD AND NME | Denied status plus approver/time AND editor/time; dashboard redirect. NME alone fails outer board gate; differs from N02 (P/Q; V:124–145) |
| NM-N05 | GET `marks/`; logged in; read helpers `get_new_members`, `calculate_member_marks`, `get_user_submitted_marks`, `get_personal_stats`, `get_active_member_analytics`; optional helper date bounds | ACTIVE template if ACTIVE; personal stats if NEW_MEMBER else analytics; mixed ACTIVE+NEW_MEMBER gets ACTIVE template with personal context. Class totals approved/signed ascending; new-member names lastName order; personal latest date; requester's requested/recent-denied list; class choices reverse enum excluding Current. No marks writes (P/Q/D; V:12–44,F:9–114,D) |
| NM-N06 | GET `history/<int:user_id>/`; any authenticated user, target must currently have NEW_MEMBER | Approved rows descending date, signed total/is_negative; any login can view another new member. Missing/ineligible target message+landing redirect. Viewer missing profile crashes on board flag (P/Q/D; V:93–117,F:177–188,H) |
| NM-N07 | GET `export-newmember-marks/?pclass=...`; any login; NEW_MEMBER actors cannot choose non-Current | XLSX MIME/disposition, Current selects NEW_MEMBER role, historical selects pclass regardless of role; approved only, oldest first, four columns/member, name-sorted blocks, signed Total text. Groups by full name, raw strings become cells; BytesIO only, no stored file/session writes (P/D/Q; V:187–330,D:128–136) |
| NM-N08 | `hours_remaining(goal,current)` pure filter | max(0,float(goal)-float(current)); no persistence; numeric conversion exceptions/nonfinite handling need policy (P/Q; T) |
| NM-C03 | configured admin model URLs/default ModelAdmin; staff+model perms or superuser | Standard Django list/add/change/delete; list six fields; no custom domain role, audit, transition or target checks; model form validation differs from raw views (P/D/Q; A,M; CORE/urls.py:25) |

No application transaction wrapper, file upload, model hook or session mutation
exists in these marks operations. Messages may use Django session storage;
snapshot auth/session keys separately from message consumption. Bulk_create's
Django/backend transaction behavior must be established, including deferred FK
failures; do not infer atomicity from the single helper call or caught exception.

## Actors and ownership

Use separate requesters A/B, new-member targets T1/T2, and reviewer R, not the
demo executive. Role names are independent M2M entries; no implicit hierarchy.
`check_user_role` tests one exact role, not a decorator with ANY semantics.

| Actor (explicit roles) | Request N01 | Approve N02 / edit N03 | Edit-deny N04 | Reads/export |
| --- | --- | --- | --- | --- |
| Anonymous | login redirect | login redirect | login redirect | N00 public; other mounted routes login redirect |
| Profile, no roles; ALUMNI; EXEC alone; NME alone | denied redirect | denied redirect | denied redirect | N05/N06/N07 allowed by login alone; historical scope Q |
| ACTIVE alone | requested rows | denied | denied | active template, own submissions; all new-member histories; historical export currently allowed |
| NEW_MEMBER alone | denied | denied | denied | personal stats; Current export only, even when requesting own prior class |
| NM_BOARD alone | denied | allowed | denied | non-active dashboard, class analytics; export allowed |
| ACTIVE+NM_BOARD | auto-approved | allowed | denied | active template; export allowed |
| NM_BOARD+NME | denied without ACTIVE | allowed | allowed (ALL required) | analytics/export allowed |
| ACTIVE+NEW_MEMBER | requested unless also board | denied without board | denied | ACTIVE template wins; personal stats wins; previous class export denied |
| NM_BOARD+NEW_MEMBER | denied without ACTIVE | allowed | only with NME | previous class export denied even though board |
| Missing Brother_Profile | login succeeds, role helper raises | role helper raises | role helper raises | N00 renders; history valid target also raises; export/marks role helper raises (D) |

Ownership is currently requester-fixed on create, unrestricted board edits of
other people's marks, own-submissions-only dashboard list, target-scoped helper
history but no viewer ownership gate. Both own/other rows must be exercised.
Direct helpers are not HTTP-authenticated; future service boundary must define
actor authorization instead of relying on hidden buttons. Staff/superuser grants
alone do not imply app roles; app roles alone do not imply admin permissions.

## Fixture and execution contract

Use the agreed [shared fixture contract](../../../docs/testing/fixture-contract.md)
without parallel factories/settings. `make_user` always names `username`; domain-local
mark constructors must name requester, target, status, value, event date and audit.
Use `login_actor`, `csrf_client`, `at_time`, `temporary_media`, `snapshot_scope` and
`assert_unchanged` exactly as shared interfaces describe. Roles are exact sets.
Use business mode for ordinary/admin tests and actual demo mode only for demo boundaries.
All named existing rows/relations in cases are refreshed before state assertions;
new-row counts and stored-file assertions are separate from row snapshots.

`READY` means an unambiguous preservation design expected to pass current source
with the common harness; no case was executed or approved here. `NEEDS_FIX` states
a concrete safety target. `POLICY_BLOCKED` takes precedence when the expected
outcome is undecided, even if PostgreSQL or fixes are also required. There are no
purely infrastructure-blocked cases: the race contract itself is still Q04.
Ordinary signed values -3/0/4 are preserved; no new numeric bound is selected.

## Local fixture vocabulary

These are domain-local real-ORM setup rules, not new shared harness interfaces.
Each GIVEN creates fresh rows; a symbol's definition never comes from a previous
case. Every symbolic user has an explicit unique username: A=`nm-a`, B=`nm-b`,
C=`nm-c`, R=`nm-r`, R1=`nm-r1`, R2=`nm-r2`, S=`nm-s`, T1=`nm-t1`,
T2=`nm-t2`, T3=`nm-t3`; table-driven viewers get separate fresh fixtures.
Use shared `make_user(username=..., roles=..., profile_fields=...)` with exactly
GIVEN roles; `board` means only NM_BOARD, `educator board` means NM_BOARD+NME.
T1/T2/T3 are NEW_MEMBER unless a case explicitly sets another role or no profile.
Other undeclared roles are empty; no actor is implicitly ACTIVE or staff.
Profiles have first/last names Alex/Able (A), Blake/Baker (B), Rae/Reviewer (R),
Tess/TargetOne (T1), Terry/TargetTwo (T2), Taylor/TargetThree (T3), overridden
by explicit case names. Classes default None, images/majors empty.

A named M/M1/M2/M3/M4 is a thin local mark constructor: requester B, target T1,
requested, value 2, title Workshop, event 2026-10-16, submitted 2026-10-16T15:00Z,
null approval/editor audit, unless GIVEN overrides. All dates abbreviated Oct/Sep
mean 2026. A declared approved/denied row gets approver "Prior Reviewer" and
approval 2026-10-16T16:00Z unless the case overrides it. Z is an unrelated approved
mark by B for T2, value 7, title Stable, event 2026-10-01, submitted Oct01 15:00Z,
approved Oct02 12:00Z, approver "Prior Reviewer", no edit audit. Constructors
create the named requester/target users in GIVEN, not during the action.
Unnamed date-series events are an explicit local `mark_rows` list in that case;
each supplied date/value/status produces one row with requester A, target T1
unless another owner/target is declared. Arithmetic-only progress arrays need
no corresponding marks except the explicitly declared analytics event rows.

`scope_rows` names exactly the fixture's existing marks (including date-series
`mark_rows`), users and profiles created by GIVEN. `scope_relations` names their
actual role, major and permission M2M links; `scope_files` is the existing files
in `temporary_media` (normally empty). These local collections are passed to
the agreed snapshot interface, never a purported whole-database snapshot.
Capture `before` before WHEN and call `assert_unchanged` after fresh reads.
Create cases snapshot existing rows only and assert inserted rows separately;
delete cases exclude the explicitly deleted row and assert its absence separately.
For policy cases `fields_explicitly_allowed_by_selected_decision` is empty for
reject/no-op, or only the allowed fields spelled out in that case's THEN after
owners choose the named decision. It cannot allow unrelated fixture changes.
Authenticated identity checks allow messages/CSRF metadata to change.

## Defects and decisions

| Defect | Source-backed issue |
| --- | --- |
| D01 | Missing profiles dereferenced by role/view helpers (F:190–192; V:103) |
| D02 | Raw request parsing and exception string disclosure (V:53–58; F:136–137,157–158) |
| D03 | Request helper lacks ACTIVE check (F:116–137) |
| D04 | Unknown approve action saves and reports success-denied (F:143–154) |
| D05 | Approval helper lacks NM_BOARD check (F:140–158) |
| D06 | Raw edit parsing and uncaught save failures (V:148–163,142) |
| D07 | XLSX dictionary merges different target IDs by full name (V:220–229) |
| D08 | XLSX raw text writes can become formulas (V:265,286) |
| D09 | Workbook save failure is not handled (V:315–330) |

| Gate | Decision needed (do not select policy in Wave 1) |
| --- | --- |
| Q01 | Eligible target/class/self rules; whether historical/profileless targets are allowed; empty batches and duplicate semantics |
| Q02 | Upper/lower value bounds, blank/length reason, future date, unknown edit action and required retarget fields; consistent safe error/status/message contract |
| Q03 | Batch all-or-nothing contract and transaction/error containment through commit; desired repeated HTTP submission behavior/idempotency |
| Q04 | Repeated/reverse/self approvals, who may override, audit retention/versioning, concurrency winner/conflict semantics; current last-writer overwrite is observation only |
| Q05 | Keep NM_BOARD+NME edit-deny versus NM_BOARD approve-deny distinction or unify; JS says irreversible but server allows overrides |
| Q06 | Partial/reversed ranges, tie ordering, future events/seven-day global scope, mixed-role dashboard presentation and timezone date cutoffs |
| Q07 | Intended history/dashboard/historical-export visibility for no-role/alumni and other users; NEW_MEMBER+board export precedence |
| Q08 | Filter invalid/nonfinite numeric input behavior; whether unused local duplicate should remain |
| Q09 | Export unique identity labeling and literal-text treatment while preserving numeric marks; XLSX display/encoding details |
| Q10 | Admin domain authorization/transition/audit parity and deletion/retention contract |


## Case readiness and index

**38 original groups → 88 independent case designs across 10 operations.**

| Status | Cases |
| --- | ---: |
| READY | 50 |
| NEEDS_FIX | 14 |
| POLICY_BLOCKED | 24 |
| INFRA_BLOCKED | 0 |

| New ID | test_name | Primary status | Design |
| --- | --- | --- | --- |
| NM-00-01a | `test_landing_renders_public_navigation` | READY | [case](cases/boundaries.md#nm-00-01a--test_landing_renders_public_navigation) |
| NM-SEC-01a | `test_anonymous_routes_redirect_to_login` | READY | [case](cases/boundaries.md#nm-sec-01a--test_anonymous_routes_redirect_to_login) |
| NM-SEC-02a | `test_request_requires_explicit_active_role` | READY | [case](cases/boundaries.md#nm-sec-02a--test_request_requires_explicit_active_role) |
| NM-SEC-02b | `test_review_and_regular_edit_require_board_role` | READY | [case](cases/boundaries.md#nm-sec-02b--test_review_and_regular_edit_require_board_role) |
| NM-SEC-02c | `test_edit_deny_requires_both_roles` | READY | [case](cases/boundaries.md#nm-sec-02c--test_edit_deny_requires_both_roles) |
| NM-SEC-03a | `test_mutating_routes_reject_missing_or_bad_csrf` | READY | [case](cases/boundaries.md#nm-sec-03a--test_mutating_routes_reject_missing_or_bad_csrf) |
| NM-SEC-03b | `test_create_accepts_acquired_csrf_token` | READY | [case](cases/boundaries.md#nm-sec-03b--test_create_accepts_acquired_csrf_token) |
| NM-SEC-03c | `test_approve_accepts_acquired_csrf_token` | READY | [case](cases/boundaries.md#nm-sec-03c--test_approve_accepts_acquired_csrf_token) |
| NM-SEC-03d | `test_update_accepts_acquired_csrf_token` | READY | [case](cases/boundaries.md#nm-sec-03d--test_update_accepts_acquired_csrf_token) |
| NM-SEC-03e | `test_edit_deny_accepts_acquired_csrf_token` | READY | [case](cases/boundaries.md#nm-sec-03e--test_edit_deny_accepts_acquired_csrf_token) |
| NM-SEC-04a | `test_profileless_actor_fails_safely` | NEEDS_FIX | [case](cases/boundaries.md#nm-sec-04a--test_profileless_actor_fails_safely) |
| NM-01-01a | `test_request_form_lists_new_member_targets` | READY | [case](cases/requests.md#nm-01-01a--test_request_form_lists_new_member_targets) |
| NM-01-01b | `test_signed_multi_target_submission_creates_requested_marks` | READY | [case](cases/requests.md#nm-01-01b--test_signed_multi_target_submission_creates_requested_marks) |
| NM-01-02a | `test_board_submission_autoapproves_and_ignores_forged_audit` | READY | [case](cases/requests.md#nm-01-02a--test_board_submission_autoapproves_and_ignores_forged_audit) |
| NM-01-03a | `test_malformed_request_fields_never_crash_or_insert` | NEEDS_FIX | [case](cases/requests.md#nm-01-03a--test_malformed_request_fields_never_crash_or_insert) |
| NM-01-03b | `test_request_content_boundaries_require_policy` | POLICY_BLOCKED | [case](cases/requests.md#nm-01-03b--test_request_content_boundaries_require_policy) |
| NM-01-04a | `test_empty_and_duplicate_target_batches_require_policy` | POLICY_BLOCKED | [case](cases/requests.md#nm-01-04a--test_empty_and_duplicate_target_batches_require_policy) |
| NM-01-04b | `test_ineligible_and_self_targets_require_policy` | POLICY_BLOCKED | [case](cases/requests.md#nm-01-04b--test_ineligible_and_self_targets_require_policy) |
| NM-01-04c | `test_invalid_target_identifiers_cannot_partially_persist` | NEEDS_FIX | [case](cases/requests.md#nm-01-04c--test_invalid_target_identifiers_cannot_partially_persist) |
| NM-01-05a | `test_request_helper_enforces_actor_authorization` | NEEDS_FIX | [case](cases/requests.md#nm-01-05a--test_request_helper_enforces_actor_authorization) |
| NM-01-06a | `test_batch_commit_failure_requires_atomicity_policy` | POLICY_BLOCKED | [case](cases/requests.md#nm-01-06a--test_batch_commit_failure_requires_atomicity_policy) |
| NM-02-01a | `test_pending_review_lists_only_requested_marks` | READY | [case](cases/decisions.md#nm-02-01a--test_pending_review_lists_only_requested_marks) |
| NM-02-01b | `test_board_approves_another_request` | READY | [case](cases/decisions.md#nm-02-01b--test_board_approves_another_request) |
| NM-02-01c | `test_board_denies_another_request` | READY | [case](cases/decisions.md#nm-02-01c--test_board_denies_another_request) |
| NM-02-02a | `test_unknown_mark_id_reports_not_found` | READY | [case](cases/decisions.md#nm-02-02a--test_unknown_mark_id_reports_not_found) |
| NM-02-02b | `test_unknown_approval_action_never_claims_success` | NEEDS_FIX | [case](cases/decisions.md#nm-02-02b--test_unknown_approval_action_never_claims_success) |
| NM-02-02c | `test_malformed_approval_ids_fail_without_exception_details` | NEEDS_FIX | [case](cases/decisions.md#nm-02-02c--test_malformed_approval_ids_fail_without_exception_details) |
| NM-02-03a | `test_approval_helper_enforces_board_authorization` | NEEDS_FIX | [case](cases/decisions.md#nm-02-03a--test_approval_helper_enforces_board_authorization) |
| NM-02-03b | `test_profileless_direct_reviewer_fails_safely` | NEEDS_FIX | [case](cases/decisions.md#nm-02-03b--test_profileless_direct_reviewer_fails_safely) |
| NM-02-04a | `test_repeat_and_reverse_review_need_transition_policy` | POLICY_BLOCKED | [case](cases/decisions.md#nm-02-04a--test_repeat_and_reverse_review_need_transition_policy) |
| NM-02-04b | `test_self_review_needs_actor_policy` | POLICY_BLOCKED | [case](cases/decisions.md#nm-02-04b--test_self_review_needs_actor_policy) |
| NM-02-05a | `test_simultaneous_review_needs_conflict_policy` | POLICY_BLOCKED | [case](cases/decisions.md#nm-02-05a--test_simultaneous_review_needs_conflict_policy) |
| NM-02-05b | `test_approval_save_failure_keeps_original_row` | READY | [case](cases/decisions.md#nm-02-05b--test_approval_save_failure_keeps_original_row) |
| NM-03-01a | `test_edit_form_prefills_single_target` | READY | [case](cases/editing.md#nm-03-01a--test_edit_form_prefills_single_target) |
| NM-03-01b | `test_board_edit_retargets_and_sets_editor_only` | READY | [case](cases/editing.md#nm-03-01b--test_board_edit_retargets_and_sets_editor_only) |
| NM-03-02a | `test_nonexistent_retarget_leaves_entire_mark_unchanged` | READY | [case](cases/editing.md#nm-03-02a--test_nonexistent_retarget_leaves_entire_mark_unchanged) |
| NM-03-02b | `test_malformed_edit_cannot_crash_or_partially_save` | NEEDS_FIX | [case](cases/editing.md#nm-03-02b--test_malformed_edit_cannot_crash_or_partially_save) |
| NM-03-02c | `test_edit_save_failure_preserves_database_state` | NEEDS_FIX | [case](cases/editing.md#nm-03-02c--test_edit_save_failure_preserves_database_state) |
| NM-03-02d | `test_omitted_or_identical_retarget_needs_field_policy` | POLICY_BLOCKED | [case](cases/editing.md#nm-03-02d--test_omitted_or_identical_retarget_needs_field_policy) |
| NM-03-02e | `test_edit_content_boundaries_need_policy` | POLICY_BLOCKED | [case](cases/editing.md#nm-03-02e--test_edit_content_boundaries_need_policy) |
| NM-03-03a | `test_edit_target_eligibility_needs_policy` | POLICY_BLOCKED | [case](cases/editing.md#nm-03-03a--test_edit_target_eligibility_needs_policy) |
| NM-03-03b | `test_unknown_edit_action_needs_transport_policy` | POLICY_BLOCKED | [case](cases/editing.md#nm-03-03b--test_unknown_edit_action_needs_transport_policy) |
| NM-03-04a | `test_missing_edit_resource_returns_404` | READY | [case](cases/editing.md#nm-03-04a--test_missing_edit_resource_returns_404) |
| NM-04-01a | `test_educator_board_edit_deny_sets_both_audits` | READY | [case](cases/editing.md#nm-04-01a--test_educator_board_edit_deny_sets_both_audits) |
| NM-04-01b | `test_deny_endpoint_permission_difference_needs_policy` | POLICY_BLOCKED | [case](cases/editing.md#nm-04-01b--test_deny_endpoint_permission_difference_needs_policy) |
| NM-04-02a | `test_repeat_override_or_self_edit_deny_needs_policy` | POLICY_BLOCKED | [case](cases/editing.md#nm-04-02a--test_repeat_override_or_self_edit_deny_needs_policy) |
| NM-04-02b | `test_edit_deny_save_failure_preserves_both_audits` | NEEDS_FIX | [case](cases/editing.md#nm-04-02b--test_edit_deny_save_failure_preserves_both_audits) |
| NM-05-01a | `test_signed_class_totals_and_order_exclude_unapproved` | READY | [case](cases/read-models.md#nm-05-01a--test_signed_class_totals_and_order_exclude_unapproved) |
| NM-05-01b | `test_personal_stats_use_approved_signed_totals` | READY | [case](cases/read-models.md#nm-05-01b--test_personal_stats_use_approved_signed_totals) |
| NM-05-02a | `test_two_bound_date_ranges_are_inclusive` | READY | [case](cases/read-models.md#nm-05-02a--test_two_bound_date_ranges_are_inclusive) |
| NM-05-02b | `test_one_sided_reversed_and_tied_ranges_need_policy` | POLICY_BLOCKED | [case](cases/read-models.md#nm-05-02b--test_one_sided_reversed_and_tied_ranges_need_policy) |
| NM-05-02c | `test_active_analytics_count_events_and_signed_standing` | READY | [case](cases/read-models.md#nm-05-02c--test_active_analytics_count_events_and_signed_standing) |
| NM-05-02d | `test_future_week_events_and_timezone_cutoffs_need_policy` | POLICY_BLOCKED | [case](cases/read-models.md#nm-05-02d--test_future_week_events_and_timezone_cutoffs_need_policy) |
| NM-05-03a | `test_own_denied_visibility_uses_actual_fourteen_days` | READY | [case](cases/read-models.md#nm-05-03a--test_own_denied_visibility_uses_actual_fourteen_days) |
| NM-05-04a | `test_single_role_dashboard_selects_matching_context` | READY | [case](cases/read-models.md#nm-05-04a--test_single_role_dashboard_selects_matching_context) |
| NM-05-04b | `test_mixed_roles_and_unprivileged_dashboard_need_visibility_policy` | POLICY_BLOCKED | [case](cases/read-models.md#nm-05-04b--test_mixed_roles_and_unprivileged_dashboard_need_visibility_policy) |
| NM-05-04c | `test_class_choices_follow_reverse_enum_order` | READY | [case](cases/read-models.md#nm-05-04c--test_class_choices_follow_reverse_enum_order) |
| NM-05-04d | `test_unknown_and_null_class_order_needs_policy` | POLICY_BLOCKED | [case](cases/read-models.md#nm-05-04d--test_unknown_and_null_class_order_needs_policy) |
| NM-05-05a | `test_empty_analytics_and_personal_totals_are_zero` | READY | [case](cases/read-models.md#nm-05-05a--test_empty_analytics_and_personal_totals_are_zero) |
| NM-05-05b | `test_pending_query_handles_missing_related_profiles` | READY | [case](cases/read-models.md#nm-05-05b--test_pending_query_handles_missing_related_profiles) |
| NM-06-01a | `test_history_helper_returns_approved_target_total` | READY | [case](cases/history-filter.md#nm-06-01a--test_history_helper_returns_approved_target_total) |
| NM-06-01b | `test_history_view_audience_and_edit_flags_need_policy` | POLICY_BLOCKED | [case](cases/history-filter.md#nm-06-01b--test_history_view_audience_and_edit_flags_need_policy) |
| NM-06-02a | `test_missing_or_non_new_member_history_redirects` | READY | [case](cases/history-filter.md#nm-06-02a--test_missing_or_non_new_member_history_redirects) |
| NM-06-02b | `test_empty_target_history_helper_returns_zero` | READY | [case](cases/history-filter.md#nm-06-02b--test_empty_target_history_helper_returns_zero) |
| NM-06-02c | `test_empty_history_view_needs_audience_policy` | POLICY_BLOCKED | [case](cases/history-filter.md#nm-06-02c--test_empty_history_view_needs_audience_policy) |
| NM-08-01a | `test_hours_remaining_converts_numbers_and_floors_zero` | READY | [case](cases/history-filter.md#nm-08-01a--test_hours_remaining_converts_numbers_and_floors_zero) |
| NM-08-01b | `test_invalid_and_nonfinite_filter_operands_need_policy` | POLICY_BLOCKED | [case](cases/history-filter.md#nm-08-01b--test_invalid_and_nonfinite_filter_operands_need_policy) |
| NM-07-01a | `test_export_current_workbook_has_signed_approved_values` | READY | [case](cases/exports.md#nm-07-01a--test_export_current_workbook_has_signed_approved_values) |
| NM-07-01b | `test_historical_export_scope_needs_audience_policy` | POLICY_BLOCKED | [case](cases/exports.md#nm-07-01b--test_historical_export_scope_needs_audience_policy) |
| NM-07-02a | `test_new_member_current_export_is_allowed` | READY | [case](cases/exports.md#nm-07-02a--test_new_member_current_export_is_allowed) |
| NM-07-02b | `test_previous_class_export_role_precedence_needs_policy` | POLICY_BLOCKED | [case](cases/exports.md#nm-07-02b--test_previous_class_export_role_precedence_needs_policy) |
| NM-07-03a | `test_duplicate_names_never_merge_member_identities` | NEEDS_FIX | [case](cases/exports.md#nm-07-03a--test_duplicate_names_never_merge_member_identities) |
| NM-07-04a | `test_formula_like_export_text_remains_literal` | NEEDS_FIX | [case](cases/exports.md#nm-07-04a--test_formula_like_export_text_remains_literal) |
| NM-07-05a | `test_empty_current_export_is_a_valid_workbook` | READY | [case](cases/exports.md#nm-07-05a--test_empty_current_export_is_a_valid_workbook) |
| NM-07-05b | `test_export_requester_without_profile_uses_username` | READY | [case](cases/exports.md#nm-07-05b--test_export_requester_without_profile_uses_username) |
| NM-07-05c | `test_workbook_save_failure_returns_controlled_error` | NEEDS_FIX | [case](cases/exports.md#nm-07-05c--test_workbook_save_failure_returns_controlled_error) |
| NM-C03-01a | `test_admin_nonstaff_redirects_even_with_board_role` | READY | [case](cases/admin.md#nm-c03-01a--test_admin_nonstaff_redirects_even_with_board_role) |
| NM-C03-01b | `test_admin_changelist_shows_configured_columns` | READY | [case](cases/admin.md#nm-c03-01b--test_admin_changelist_shows_configured_columns) |
| NM-C03-01c | `test_admin_staff_without_permissions_is_forbidden` | READY | [case](cases/admin.md#nm-c03-01c--test_admin_staff_without_permissions_is_forbidden) |
| NM-C03-01d | `test_admin_staff_explicit_permission_allows_corresponding_page` | READY | [case](cases/admin.md#nm-c03-01d--test_admin_staff_explicit_permission_allows_corresponding_page) |
| NM-C03-01e | `test_admin_staff_without_write_permission_cannot_add_or_change` | READY | [case](cases/admin.md#nm-c03-01e--test_admin_staff_without_write_permission_cannot_add_or_change) |
| NM-C03-01f | `test_admin_nonstaff_cannot_add_or_change_through_admin` | READY | [case](cases/admin.md#nm-c03-01f--test_admin_nonstaff_cannot_add_or_change_through_admin) |
| NM-C03-02a | `test_admin_forms_reject_invalid_model_fields` | READY | [case](cases/admin.md#nm-c03-02a--test_admin_forms_reject_invalid_model_fields) |
| NM-C03-02b | `test_admin_write_audit_and_transition_parity_need_policy` | POLICY_BLOCKED | [case](cases/admin.md#nm-c03-02b--test_admin_write_audit_and_transition_parity_need_policy) |
| NM-C03-02c | `test_mark_string_representation_names_target` | READY | [case](cases/admin.md#nm-c03-02c--test_mark_string_representation_names_target) |
| NM-C03-03a | `test_admin_mark_delete_removes_only_selected_mark` | READY | [case](cases/admin.md#nm-c03-03a--test_admin_mark_delete_removes_only_selected_mark) |
| NM-C03-03b | `test_foreign_key_deletion_retention_needs_policy` | POLICY_BLOCKED | [case](cases/admin.md#nm-c03-03b--test_foreign_key_deletion_retention_needs_policy) |
| NM-C03-03c | `test_admin_delete_without_permission_preserves_records` | READY | [case](cases/admin.md#nm-c03-03c--test_admin_delete_without_permission_preserves_records) |

## Original-to-new completeness mapping

Shared boundary references in this mapping cover original overlaps without adding
duplicate designs or inflating readiness totals.

| Original parent | New IDs |
| --- | --- |
| NM-00-01 | NM-00-01a |
| NM-SEC-01 | NM-SEC-01a |
| NM-SEC-02 | NM-SEC-02a, NM-SEC-02b, NM-SEC-02c |
| NM-SEC-03 | NM-SEC-03a, NM-SEC-03b, NM-SEC-03c, NM-SEC-03d, NM-SEC-03e |
| NM-SEC-04 | NM-SEC-04a |
| NM-01-01 | NM-01-01a, NM-01-01b |
| NM-01-02 | NM-01-02a |
| NM-01-03 | NM-01-03a, NM-01-03b |
| NM-01-04 | NM-01-04a, NM-01-04b, NM-01-04c |
| NM-01-05 | NM-01-05a |
| NM-01-06 | NM-01-06a |
| NM-02-01 | NM-02-01a, NM-02-01b, NM-02-01c |
| NM-02-02 | NM-02-02a, NM-02-02b, NM-02-02c |
| NM-02-03 | NM-02-03a, NM-02-03b |
| NM-02-04 | NM-02-04a, NM-02-04b |
| NM-02-05 | NM-02-05a, NM-02-05b |
| NM-03-01 | NM-03-01a, NM-03-01b |
| NM-03-02 | NM-03-02a, NM-03-02b, NM-03-02c, NM-03-02d, NM-03-02e |
| NM-03-03 | NM-03-03a, NM-03-03b |
| NM-03-04 | NM-03-04a |
| NM-04-01 | NM-04-01a, NM-04-01b, NM-SEC-02c |
| NM-04-02 | NM-04-02a, NM-04-02b |
| NM-05-01 | NM-05-01a, NM-05-01b |
| NM-05-02 | NM-05-02a, NM-05-02b, NM-05-02c, NM-05-02d |
| NM-05-03 | NM-05-03a |
| NM-05-04 | NM-05-04a, NM-05-04b, NM-05-04c, NM-05-04d |
| NM-05-05 | NM-05-05a, NM-05-05b |
| NM-06-01 | NM-06-01a, NM-06-01b |
| NM-06-02 | NM-06-02a, NM-06-02b, NM-06-02c |
| NM-08-01 | NM-08-01a, NM-08-01b |
| NM-07-01 | NM-07-01a, NM-07-01b |
| NM-07-02 | NM-07-02a, NM-07-02b |
| NM-07-03 | NM-07-03a |
| NM-07-04 | NM-07-04a |
| NM-07-05 | NM-07-05a, NM-07-05b, NM-07-05c, NM-SEC-01a |
| NM-C03-01 | NM-C03-01a, NM-C03-01b, NM-C03-01c, NM-C03-01d, NM-C03-01e, NM-C03-01f |
| NM-C03-02 | NM-C03-02a, NM-C03-02b, NM-C03-02c |
| NM-C03-03 | NM-C03-03a, NM-C03-03b, NM-C03-03c |

## Existing assertions and Wave 2 order

`NEWMEMBER/tests.py:1–3` remains an assertion-free placeholder. Demo assertions at
`railway_demo/tests.py:31–38,58–72` verify seeded count and privileged/new-member
page rendering, not mark writes, narrow roles, totals, decisions, history or XLSX.
The demo CSRF/admin assertions at `:79–97` concern demo entry and its admin boundary,
not marks CSRF or default domain ModelAdmin. No measured coverage is claimed.

1. Coordinator verifies sources, old-parent coverage and shared fixture compatibility.
2. Resolve Q01–Q10; implement READY cases in singular `test/`, verifying discovery
   alongside existing `tests.py` without dropping demo tests.
3. Fix D01–D09 independently; implement safety cases against agreed error adapters.
4. Resolve blocked policies, then implement exact assertions instead of unexplained skips.
5. Establish batch commit behavior with TransactionTestCase, and only after Q04
   run bounded PostgreSQL independent-connection review races; SQLite proves no races.
6. Keep real ORM business assertions separate from legacy response/template adapters;
   SimpleTestCase is sufficient for filter arithmetic. Mock only controlled clocks
   and deliberate save/storage failure boundaries, never roles or business decisions.
7. Coordinator runs domain/shared tests and records actual outcomes in Wave 2.

Refinement checks inspect Markdown only: IDs/names, exact metadata, statuses,
GIVEN/WHEN/THEN, all 38 original parents, anchors/local links and whitespace.
No application tests, system checks, network calls, secrets, dependency/config
changes or Git mutations were performed in this refinement.

Markdown-only validation found 88 unique IDs and names, all 38 baseline parents
covered, matching index/status counts, exact metadata/pseudocode shape and
existing local link/anchor targets. Every database case captures a before snapshot
in GIVEN; scope rules distinguish permitted field changes and deletions.
No proposed case has been executed.
