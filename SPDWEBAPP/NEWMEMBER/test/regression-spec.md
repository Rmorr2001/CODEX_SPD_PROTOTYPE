# NEWMEMBER Wave 1 regression specification

## Provenance and source inventory

Inspected checkout `/workspace/CODEX-SPD-PROTOTYPE`, repository
`Rmorr2001/CODEX_SPD_PROTOTYPE`, actual branch `prototype/railway`, commit
`7e25ac2f06b2d88a0220526771585f30df10c57a`. Root `AGENTS.md` and
[the complete shared contract](../../../docs/testing/wave-1-agent-prompt.md)
were read; no nested AGENTS.md was found. All findings below are inspection,
not executed results. No application tests, network calls, credentials, private
uploads, Git mutations or dependency changes were used.

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

## Classification and operation inventory

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
| NM-N06 | GET `history/<int:user_id>/`; any authenticated user, target must currently have NEW_MEMBER | Approved rows descending date, signed total/is_negative; any login can view another new member. Missing/ineligible target message+landing redirect. Requester missing profile crashes on board flag (P/Q/D; V:93–117,F:177–188,H) |
| NM-N07 | GET `export-newmember-marks/?pclass=...`; any login except NEW_MEMBER cannot choose non-Current | XLSX MIME/disposition, Current selects NEW_MEMBER role, historical selects pclass regardless of role; approved only, oldest first, four columns/member, name-sorted blocks, signed Total text. Groups by full name, raw strings become cells; BytesIO only, no stored file/session writes (P/D/Q; V:187–330,D:128–136) |
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

## Fixtures, assertion protocol, and cases

Shared proposals: `make_user(roles=(),with_profile=True,**fields)`,
`make_profile(user,**fields)`, controlled `timezone.now()` and date, temporary
media helpers; use image-free profiles. Domain-local `make_mark(requester,target,
status,value,event_date,**audit)` creates real rows. Freeze UTC time at
2026-10-17 12:00 and explicitly set event dates; set auto-added submission times
via controlled clock or an ORM update where required. Use unique names unless
case demands collisions. `snapshot()` records all marks fields/PKs, profiles,
roles and users; `U` below means refresh/snapshot equality for every unmentioned
row/field plus unchanged user/profile/roles, no files created and unchanged auth
session keys. All denied/error/read cases require U for all domain records.
Mutable cases explicitly list the only allowed changed fields. No assertions
against in-memory objects substitute for fresh ORM reads.

Each case below is setup → action → response assertion → fresh state assertion.
Table-driven variants are individual subcases with each assertion required.
“Reject” in D cases is a proposed corrected requirement; status/message shape
is blocked until validation/error policy is agreed, never assert current 500s
or bypasses as approved. Q cases record legacy observation separately and keep
final business assertions pending; they are not unexplained skips or coverage.

### N00 and shared boundary cases

- **NM-00-01 (P2/P, N00):** anonymous and authenticated empty database → GET
  landing → 200 correct template and marks/roster navigation → all records U;
  do not follow/probe the external national-site link.
- **NM-SEC-01 (P0/P, N01–N07):** anonymous client plus existing mark → GET
  and POST each applicable route → login redirect with next URL; protected GETs
  disclose no record values → U. Use valid CSRF for anonymous POST to isolate
  login behavior; CSRF rejection is separate.
- **NM-SEC-02 (P0/P, N01–N04):** each disallowed actor from matrix, own and
  another requester's mark → crafted GET/POST, including hidden deny action →
  marks redirect and appropriate denial message, not successful mutation → U.
  Board-only regular edit allowed; NME-only edit-deny denied; role combinations
  are separate fixtures, never inferred from executive success.
- **NM-SEC-03 (P0/P, N01–N04):** allowed actor, `Client(enforce_csrf_checks=True)`
  → POST missing token and mismatched token → 403/U; GET form to obtain valid
  cookie/token then POST → expected operation result with only listed writes.
- **NM-SEC-04 (P1/D, N01–N07):** authenticated user without profile → each
  protected operation, existing valid target/mark → controlled deny/error rather
  than relation exception → U; N00 remains renderable. Error adapter policy gate.

### Requests

- **NM-01-01 (P1/P, N01):** ACTIVE A, T1/T2 NEW_MEMBER, B and non-new-member
  profiles → GET request → 200 correct form with only T1/T2 IDs, repeated field
  name target_users and CSRF → U; POST both IDs, signed values parameterized
  -3/0/+4, ISO date/reason → marks redirect/success → exactly two rows per
  request, A requester, correct independent targets/value/date/title, requested,
  null approver/approval date/editor fields, submission time frozen; U otherwise.
- **NM-01-02 (P1/P, N01):** ACTIVE+NM_BOARD A with known profile names → POST
  two targets with forged requesting_user/status/audit fields → success redirect
  → requester A, approved, A profile full name and frozen approval time;
  attacker fields ignored, submission time set, last-edit fields null, U.
- **NM-01-03 (P0/D, N01):** snapshots with T1/T2 → POST missing/blank/noninteger/
  decimal/huge out-of-range value, missing/blank/invalid/impossible date, missing
  reason; invoke helper with bad typed value/date too → controlled error, no raw
  exception string disclosure → zero new rows, U. Blank/over-100-char reason,
  future date and exact numeric limits are Q01/Q02 rather than invented rules.
- **NM-01-04 (P0/D/Q, N01):** targets [], [T1,T1], [missing ID], ['abc'],
  [non-new-member], [self], [T1,missing], [T1,non-new-member], null/profileless
  user → POST and helper directly → record current empty success/duplicates and
  missing eligibility validation as findings; enforce controlled invalid-ID
  rejection/U, including valid-first mixed invalid batches. Eligibility, self,
  empty/duplicate policy gated by Q01; do not choose dedup versus reject.
- **NM-01-05 (P0/D, N01):** no-role/NEW_MEMBER/NM_BOARD-only requester, valid T1
  → call create_mark_requests directly → future unauthorized result and U;
  current helper can write without ACTIVE, hence not a preserve assertion.
- **NM-01-06 (P0/D/Q, N01):** valid multi-target payload → deliberately fail
  bulk insert/FK validation at later row or deferred commit → controlled failure,
  no partial target rows, U. TransactionTestCase establishes actual commit
  behavior on configured backend; verify error containment, not merely helper
  tuple. Agree atomic batch contract Q03; database exceptions outside helper's
  try block are possible at commit. No claim from SQLite about concurrent races.

### Review and editing

- **NM-02-01 (P1/P, N02):** board R, pending own/other requests plus approved/
  denied marks → GET → pending-only IDs newest event first, proper target and
  requester names; POST each approve/deny on separate pending row → 200 review
  template/message, resolved row removed → only status, approver full name,
  approval time changed; requester/target/value/title/date/submission/editor U.
- **NM-02-02 (P0/D, N02):** board plus pending row → missing/nonnumeric/unknown
  mark_id; missing/unknown/empty action → controlled not-found/validation result,
  never success-denied for unknown action → all U. Existing nonexistent ID
  returns helper False/'Mark not found'; malformed types use generic caught
  error today, so exact future text/status requires error-policy agreement.
- **NM-02-03 (P0/D, N02):** no-role/ACTIVE actor and pending row → direct
  process_mark_approval call with request/user/messages support → future denied
  and U; expose existing absent helper authorization. Missing-profile reviewer
  also controlled failure/U rather than information-bearing exception text.
- **NM-02-04 (P0/Q, N02):** own request and another's requested/approved/denied
  rows → approve twice, deny twice, approved→deny, denied→approve, self-review
  with clock advanced → capture current overwrite of status/name/time; final
  allowed transition/idempotency/audit assertions await Q04. In every branch
  requester/target/value/title/date/submission/editor and unrelated rows U.
- **NM-02-05 (P0/D/Q, N02):** two independent reviewer connections read same
  pending row → bounded synchronization then opposite decisions → assert agreed
  single decision/conflict or approved override behavior after Q04, no lost audit
  per that decision; failed write leaves original fresh row U. PostgreSQL only
  for race proof; use injected save error for ordinary failure containment.
- **NM-03-01 (P1/P, N03):** NM_BOARD R, another requester's approved mark →
  GET → prefilled single target_user fields/editing flag; POST update title,
  -2/date/T2 → history redirect for T2 → only title/value/event date/target,
  last_edited_by R/time change; status/approver/approval date/requester/submission
  U. Repeat for requested and denied rows without changing status; signed zero
  and positive update included. No row count change, U otherwise.
- **NM-03-02 (P0/D, N03):** snapshot mark → POST valid new fields but nonexistent
  target → edit redirect/error (current handled branch) → entire fresh row U;
  then malformed target ID, missing/invalid numeric/date/reason or database save
  failure → controlled validation/error, entire row U. Missing target and same
  target separately preserve old target where current optional-retarget behavior
  is approved; required-field policy Q02 covers final form contract.
- **NM-03-03 (P0/Q/D, N03):** board mark plus existing non-new-member, profileless
  user and self IDs → crafted retarget and blank/unknown action with valid fields
  → current any existing User accepted, all non-deny actions update; record these
  observations, gate eligibility/action policy Q01/Q02; future rejected variants
  require U, allowed variants allow only NM-03-01 fields.
- **NM-03-04 (P1/P, N03/N04):** authorized board, absent integer mark_id →
  GET/POST → 404 and U; malformed path ID does not match int route → 404/U.
- **NM-04-01 (P0/P/Q, N04):** NM_BOARD-only, NME-only and both-role actors with
  pending row → POST deny → first two denial redirects/U; both-role success
  dashboard redirect → only status denied, approver/name/time and editor/time
  changed, content/requester/target/submission U. Contrast NM-02-01 board-only
  deny succeeds; preserving or unifying this distinction is Q05, not inferred
  from edit's visible deny button or JS confirmation.
- **NM-04-02 (P0/Q, N04):** both-role actor, approved/denied/self-request row →
  deny, repeat deny with advanced clock → current overwrites audit, no irreversible
  guard despite client confirmation; expected transitions/audit await Q04/Q05;
  all content/requester/target/submission and unrelated rows U. Inject save failure
  → no partial persisted audit/status; controlled error adapter remains D.

### Read models, history and filter

- **NM-05-01 (P1/P, N05):** T1 approved +5/-8, T2 approved zero, T3 no marks,
  plus large pending/denied values and former-member approved marks → call
  get_new_members/calculate_member_marks/get_personal_stats → exact T1=-3,
  T2=0,T3=0, average=-1.0, standings by >=0, correct latest approved event,
  ascending totals, lastName source order for equal totals; U. Change dates
  distinct to avoid assuming tie order not guaranteed beyond current stable sort.
- **NM-05-02 (P1/P/Q, N05):** approved events immediately before/on/after
  start/end, future event, non-new-member event; requested/denied mixed → helpers
  with both dates → inclusive range signed totals/submissions; single bound
  currently ignored, reversed range empty; final one-sided/reversed semantics
  Q06. Analytics approved event count (not sum) includes all targets and has
  only lower bound now-7 days, pending global count; test -8/-7/-6 days and
  future dates, class length/good-standing/rounded mean and empty zeros; U.
  DateField versus aware datetime conversion must be verified at midnight and
  a configured non-UTC timezone; do not compare raw datetime to DateField values.
- **NM-05-03 (P1/P, N05):** A/B requested and denied dates -15/-14/-13 days,
  old requested, and approved rows → get_user_submitted_marks(A) and ACTIVE
  dashboard → only A's requested any age plus denied from actual 14-day event
  date cutoff, newest event first; approved and B excluded; inclusive boundary
  after backend date conversion, U. Approval/submission dates do not set cutoff;
  comments saying month do not override timedelta(days=14).
- **NM-05-04 (P1/P/Q, N05):** one-role and mixed actors from matrix, classes
  Current/Alpha/Beta and null/unknown pclass fixture values → GET → correct
  template/context flags, own-only submissions, personal versus class analytics,
  reverse class-choice order excluding Current, all U. ACTIVE+NEW_MEMBER may
  render blank analytics in active template; classify UI/context mismatch D,
  desired mixed-role presentation Q06; unknown/null class tie ordering Q06.
- **NM-05-05 (P1/P, N05):** no members/marks, then member without approved marks
  → read helpers/dashboard → empty lists, zero sums/average/counts, latest None,
  good standing at zero, no divide-by-zero, U. Pending list newest order and
  requested-only filter also checked directly, including related users lacking
  profiles. Lazy queryset evaluation errors are not necessarily caught by helper.
- **NM-06-01 (P1/P/Q, N06):** target T1 approved +4/-7, denied/requested large
  values, T2 approved +20 → owner then other authenticated no-role/ACTIVE/
  NEW_MEMBER/board viewers GET T1 history → approved IDs only descending event,
  total -3, is_negative True, board edit flag only for board; U. Current login-only
  cross-member visibility is Q07; do not bless it if product chooses ownership.
- **NM-06-02 (P1/P, N06):** missing target, target with profile lacking NEW_MEMBER,
  then user without profile → GET → error message/landing redirect and U; target
  NEW_MEMBER with no marks → 200 empty history/zero/nonnegative. Helper direct
  T2 call → only T2 approved, no viewer check; helper is query not auth boundary.
- **NM-08-01 (P2/P/Q, N08):** no database → filter (10,3),(10,12),(0,0),
  numeric strings/decimals/negative operands → exact floored float differences,
  render via loaded newmember_extras; None/nonnumeric/NaN/inf → current exceptions
  or float effects recorded, fallback/rejection policy Q08, no writes in all.

### XLSX and admin

- **NM-07-01 (P1/P, N07):** distinct-name current T1/T2, historical Alpha former
  member, +5/-8 approved and pending/denied noise → Current and Alpha GET as
  ACTIVE → 200 XLSX MIME, expected attachment filename; parse with openpyxl,
  data_only=False, assert sheet name, member header positions every fifth col,
  subheaders/date ISO strings/requester names/reasons/integer signed values,
  totals 'Total: -3', oldest-first rows, sorted member blocks, blank spacer,
  historical/current isolation; U. Equal event dates require tie policy Q06.
- **NM-07-02 (P0/P/Q, N07):** NEW_MEMBER and NEW_MEMBER+NM_BOARD → Current
  GET succeeds; Alpha/missing/blank/unknown pclass → denial redirect/message/U.
  No-role/ALUMNI/NM_BOARD actors currently can historical export; gate Q07.
  For allowed actor missing/unknown pclass → current empty workbook/appropriate
  filename, no crash or mutation; allowed-class validation is Q01/Q07.
- **NM-07-03 (P0/D, N07):** two distinct target IDs same full name, each approved
  values/events → export → assert identities stay separate and each own total;
  current by_user[target_name] merges them (V:220–229), a defect rather than
  desired grouping. Exact disambiguating display label is Q09; U always.
- **NM-07-04 (P0/D, N07):** target/requester profile names and reasons beginning
  '=', '+', '-', '@', including '=1+1' → export parse cell.value and data_type
  → untrusted strings remain literal text (no formula cells), signed mark_value
  remains numeric, not apostrophe-corrupted business text; U. Current direct
  ws.cell(value=...) makes '=' strings formula candidates. Escape strategy Q09.
- **NM-07-05 (P1/P/D, N07):** no approved marks/no matching class, missing
  requester profile, anonymous client, and injected Workbook.save failure →
  empty valid XLSX for empty scope; username fallback for missing profile;
  anonymous login redirect/U; save failure controlled adapter error (D), no
  partial file persisted or altered records. Export only writes in-memory buffer.
- **NM-C03-01 (P1/P, C03):** isolated real admin configuration, superuser and
  ordinary staff with/without view/add/change/delete model perms, plus app-board
  nonstaff → reverse admin changelist/add/change/delete URLs → Django permission
  results, list six configured fields, no app-role inheritance; U on denials.
  DemoBoundaryMiddleware rejects /admin/ even for privileged fixtures; do not
  disable it silently or infer model-admin behavior from demo 403.
- **NM-C03-02 (P0/P/Q, C03):** permitted staff and synthetic marks → admin add/
  edit invalid integer/date/status or missing FK → form errors/U; valid add/edit
  approved record/retarget → row persisted per form, default model ordering and
  str format checked; no custom audit auto-fill today, audit enforcement Q10.
  Model choices are form validation, not database guarantees. Validate access
  to another requester's record under standard Django model permissions.
- **NM-C03-03 (P0/P/Q, C03):** permitted admin delete mark, requester/target,
  separately editor → delete confirmation/action → mark deletion only; deleting
  requester/target cascades marks, deleting editor sets last_edited_by null,
  other audit/content U (M:11–20,47–53); retention policy Q10 before migration
  freezes cascading loss. Rejected delete/missing permissions leaves all U.

## Completeness, existing assertions and implementation structure

There are **10 operations and 38 named case groups** (parameter variants require
separate assertions). Mapping includes shared gates, not just happy paths:

| Operation | Cases |
| --- | --- |
| NM-N00 | 00-01, SEC-04 |
| NM-N01 | SEC-01–04, 01-01–06 |
| NM-N02 | SEC-01–04, 02-01–05 |
| NM-N03 | SEC-01–04, 03-01–04 |
| NM-N04 | SEC-01–04, 03-04, 04-01–02 |
| NM-N05 | SEC-01, SEC-04, 05-01–05 |
| NM-N06 | SEC-01, SEC-04, 06-01–02 |
| NM-N07 | SEC-01, SEC-04, 07-01–05 |
| NM-N08 | 08-01 |
| NM-C03 | C03-01–03 |

All short case numbers in this mapping have prefix NM-. Placeholder X has zero
assertions; demo tests check exactly four seeded marks and GET status for a
privileged persona/request/approve/dashboard plus NEW_MEMBER dashboard access.
They do not verify any N01 write or N02–N04 state, role minima, denied targets,
14-day/seven-day semantics, personal totals, history, XLSX, tag or domain admin.
Existing demo CSRF/admin-boundary assertions cover demo entry only, not marks
POSTs or domain ModelAdmin. No measured numerical coverage is claimed.

Use the [README proposed layout](README.md). Django TestCase with real ORM for
most cases; SimpleTestCase for N08; TransactionTestCase for deferred failure and
commit boundaries; PostgreSQL independent-connection races in dedicated module.
Keep `assert_mark_content`, `assert_audit`, `assert_unchanged` and parsed workbook
assertions separate from adapter redirect/template/message/status assertions.
Mock only Workbook.save/database write failure deliberately or the controlled
clock, never approval/role/aggregation business behavior. Shared factories must
coordinate AUTHENTICATE reverse profile creation and role assignment; do not
seed broad demo data. No temp media should be necessary except fixture isolation.

## Defects, decisions and shared dependencies

Highest-risk defects: helper authorization bypass; raw parsing/absent validation;
unknown approval action falsely succeeds; arbitrary-target acceptance; name-keyed
XLSX identity merging and formula-like data; missing-profile crashes. Proposed
reject/error assertions above are correction targets requiring implementation,
not expected failures counted as completed coverage.

| Gate | Decision needed (do not select policy in Wave 1) |
| --- | --- |
| Q01 | Eligible target/class/self rules; whether historical/profileless targets are allowed; empty batches and duplicate semantics |
| Q02 | Value bounds/zero, blank/length reason, future date, unknown edit action and required retarget fields; consistent safe error/status/message contract |
| Q03 | Batch all-or-nothing contract and transaction/error containment through commit; desired repeated HTTP submission behavior/idempotency |
| Q04 | Repeated/reverse/self approvals, who may override, audit retention/versioning, concurrency winner/conflict semantics; current last-writer overwrite is observation only |
| Q05 | Keep NM_BOARD+NME edit-deny versus NM_BOARD approve-deny distinction or unify; JS says irreversible but server allows overrides |
| Q06 | Partial/reversed ranges, tie ordering, future events/seven-day global scope, mixed-role dashboard presentation and timezone date cutoffs |
| Q07 | Intended history/dashboard/historical-export visibility for no-role/alumni and other users; NEW_MEMBER+board export precedence |
| Q08 | Filter invalid/nonfinite numeric input behavior; whether unused local duplicate should remain |
| Q09 | Export unique identity labeling and literal-text treatment while preserving numeric marks; XLSX empty output expectations |
| Q10 | Admin domain authorization/transition/audit parity and deletion/retention contract |

Dependencies: coordinator-owned shared settings/factories and baseline; AUTHENTICATE
profile/role behavior and test admin composition; timezone helper; openpyxl to
parse cell values/types; actual Django dependency compatibility; PostgreSQL test
service for race proof. Existing SQLite may expose basic integrity failures but
cannot establish production locking or races. Do not create independent shared
settings, change dependencies or read runtime configuration values.

## Actual checks and Wave 2 order

Performed source listing, numbered reads, symbol/reference searches and branch/
commit inspection only. Final documentation review checks scope, operation/case
mapping and relative links. No executable tests/system checks/lint/type/coverage
were run; the coordinator owns the one shared baseline. No application files or Git history/index were changed by this domain assignment.
The two owned documentation files are the only writes. Local validation found
38 unique case IDs, existing relative-link targets and no trailing whitespace;
`git diff --check -- SPDWEBAPP/NEWMEMBER/test/README.md
SPDWEBAPP/NEWMEMBER/test/regression-spec.md` returned no output (untracked files
are additionally checked directly).

1. Coordinator source-verifies this proposal and reconciles Q01–Q10 with owners;
   prioritize authorization, transitions and export data integrity before contracts.
2. Confirm supported dependency/settings baseline and shared synthetic factories;
   establish isolated admin configuration and PostgreSQL availability.
3. Add singular test/__init__.py and proposed modules; verify discovery alongside
   existing tests.py with explicit NEWMEMBER.test command; do not count imports
   or empty tests as coverage.
4. Implement reusable state/audit assertions, narrow role/ownership/CSRF gates,
   request/approval/edit success and validation cases. Resolve defects instead
   of preserving crashes/bypasses as green expected behavior.
5. Implement deterministic analytics/history/filter boundaries and parsed XLSX
   checks including identity collisions/formula strings, then admin parity.
6. Establish deferred-commit rollback and save/export-failure behavior; run bounded
   independent PostgreSQL reviewers only after transition policy is approved.
7. Run domain and shared regression commands, record actual results and remaining
   decision/infrastructure blockers; translate business assertions to migration
   services/API adapters without replacing them with status-only tests.
