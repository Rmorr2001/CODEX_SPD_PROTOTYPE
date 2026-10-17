# Philanthropy regression specification — Wave 1

## Inspection baseline and evidence

Repository `Rmorr2001/CODEX_SPD_PROTOTYPE`, branch `prototype/railway`, actual
commit `7e25ac2f06b2d88a0220526771585f30df10c57a`. Source inspection only;
responses below describe code paths or proposed assertions, not executed results.
Read root `AGENTS.md` and `docs/testing/wave-1-agent-prompt.md` in full; no nested
AGENTS.md was found in this checkout. All paths below are repository-relative.

Source index (line numbers identify symbols and relevant implementation):

| Reference | Source and inspected responsibility |
| --- | --- |
| R | `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:23–33`; `SPDWEBAPP/PHILANTHROPY/urls.py:4–11`: admin mount and all six mounted domain routes |
| V1 | `SPDWEBAPP/PHILANTHROPY/views.py:14–57`, `philanthropy_dashboard`: ACTIVE, selected year, active members, average, chair flag |
| V2 | `SPDWEBAPP/PHILANTHROPY/views.py:59–81`, `philanthropy_request`: ACTIVE, float parse/minimum, own requested record, broad exception handler |
| V3 | `SPDWEBAPP/PHILANTHROPY/views.py:83–95`, `philanthropy_approve`: ALL PHIL_CHAIR and ACTIVE; helper then pending render |
| V4 | `SPDWEBAPP/PHILANTHROPY/views.py:98–120`, `brother_philanthropy_history`: ACTIVE; any target profile; PHIL_CHAIR flag |
| V5 | `SPDWEBAPP/PHILANTHROPY/views.py:137–239`, `export_approved_philanthropy_hours`: login only; all approved events; name grouping; workbook/response |
| V6 | `SPDWEBAPP/PHILANTHROPY/views.py:243–269`, `philanthropy_edit_event`: PHIL_CHAIR alone; any event status/owner; no minimum or exception handler |
| H1 | `SPDWEBAPP/PHILANTHROPY/views_functions.py:8–20`, `get_academic_year_dates`, `get_available_academic_years`: July–June, three recent starts |
| H2 | `SPDWEBAPP/PHILANTHROPY/views_functions.py:22–61`, `get_user_events_and_total_hours`, `collect_philanthropy_statistics`: inclusive range, approved sums, goal >=10 |
| H3 | `SPDWEBAPP/PHILANTHROPY/views_functions.py:64–86`, `philanthropy_approval_POST`: unrestricted status transitions, approver display name/time, unknown-action save |
| H4 | `SPDWEBAPP/PHILANTHROPY/views_functions.py:89–123`, `retrieve_individual_brother_history`: approved-only year buckets and lifetime sum; brother parameter unused |
| M | `SPDWEBAPP/PHILANTHROPY/models.py:5–52`, `Philanthropy_Hours_Event_and_Request`: IntegerField hours, required title/date, statuses, auto submission time, nullable audit/editor, default date order, no custom save/clean |
| A | `SPDWEBAPP/PHILANTHROPY/admin.py:8–16`, `PhilanthropyHoursEventAndRequestAdmin`: registered standard ModelAdmin, five list columns, no domain permission/audit override |
| T | `SPDWEBAPP/PHILANTHROPY/templatetags/philanthropy_extras.py:5–7`, `hours_remaining`: max(0, float(goal)-float(current)) |
| D | `SPDWEBAPP/PARLEYPRO/pp_decorators.py:7–52`, `requires_role`: authenticated and ALL required roles, missing profile/role message and referrer-or-poll redirect |
| U | `SPDWEBAPP/AUTHENTICATE/models.py:58–99`, `Role`, `Brother_Profile`: PHIL_CHAIR is declared choice; PHILANTHROPY_CHAIR is not; one-to-one profile, many-to-many roles |
| UI | `SPDWEBAPP/PHILANTHROPY/templates/philanthropy_request.html:9–24`: POST+CSRF, title/hours/date, step/min 0.5; `philanthropy_approve.html:11–50`: hidden event_id, action approve/deny, CSRF; `philanthropy_dashboard.html:19–25,33–34,77–92,139–165`: year GET, all-status own list, history/export links; `philanthropy_brother_history.html:16–61`: year totals, edited indicator, chair edit link, empty case |
| B | `SPDWEBAPP/railway_demo/middleware.py:4–12`, `DemoBoundaryMiddleware`: public demo /admin/ blanket403, distinct from domain ModelAdmin permissions |
| E | `SPDWEBAPP/PHILANTHROPY/tests.py:1–3`; `SPDWEBAPP/railway_demo/tests.py:31–40,54–77,99–109`: existing assertions |

No domain forms, custom model hooks, file upload/delete actions or JavaScript API
mutations were found. All six views are mounted. All domain helper functions
are called by views; `hours_remaining` is registered and used by both statistics
and history templates. Commented role checks in V5/V6 are inactive. The dashboard
`is_philanthropy_chair` flag is passed but not used by its template; the history
flag controls links only. UI visibility does not authorize an operation.

## Classification and state contract notation

**P (preserve)** identifies source-grounded candidate business behavior for review.
**D (defect)** identifies unsafe/inconsistent behavior; tests should assert the
agreed repaired invariant, never require the exploit or crash to pass.
**Q (decision)** requires policy before its final expected result is encoded.
P is not a claim of product approval. Legacy adapter assertions are separate
from reusable business assertions so DRF/React can reuse the latter.

For every case below: create only synthetic records; `snapshot()` captures all
field values for every event, User, profile and role join row before the action;
`unchanged(except=...)` refreshes from DB and compares snapshots plus row counts.
This includes owner, title, hours, event date, submission timestamp, status,
approver/date and editor/time. Reads leave all rows unchanged. Denials/errors
leave all rows unchanged unless an explicitly described successful target write
is intended. Login/session data may change only for explicit authentication;
domain operations must not mutate arbitrary session keys. Messages may add
Django message storage. No persistent file effects are expected; exports are
in-memory bytes. All fixtures include an unrelated event owned by B to expose
unscoped updates. No unspecified ordering among equal event dates or equal totals
is frozen; use distinct dates/totals except when testing tie membership.

## Verified operation inventory (13 operations)

All routes below are under `/philanthropy/`; GET and POST are listed explicitly.
Other HTTP methods currently fall through GET-like rendering (approval helper
runs only on POST); edit/export also lack method guards. Case PH-C03 covers this
policy gap rather than treating it as approved mutation transport.

| ID | Route/callable, actors and inputs | Current response and effects | Class |
| --- | --- | --- | --- |
| PH-P01-G | GET `request/`, ACTIVE | 200 form, CSRF token, no event write (V2/UI) | P |
| PH-P01-S | POST `request/`, ACTIVE; hours/event_title/event_date | float hours >=0.5; save one current-user requested event, auto submission time; success message+302 dashboard; exception message+200 form; ignores forged owner/status/audit (V2/M) | P own/requested; D/Q validation/precision |
| PH-P02-G | GET `approve/`, ALL PHIL_CHAIR+ACTIVE | 200 pending requested rows across owners, descending date (V3) | P |
| PH-P02-A | POST `approve/`, same roles; event_id, action=approve | any existing status/owner → approved; current profile display name and now; saves; 200 updated pending list+message (H3) | P initial approval; Q repeated/reverse/self |
| PH-P02-D | POST `approve/`, same roles; event_id, action=deny | same path to denied and audit; unknown ID/error caught; unknown action saves unchanged event and success “denied” (H3) | P initial denial; D unknown action; Q transitions |
| PH-P03-G | GET `edit/<int:event_id>/`, PHIL_CHAIR alone | any event rendered into request form or 404, no write (V6) | P/Q authority |
| PH-P03-E | POST same, PHIL_CHAIR alone; title/hours/date | replaces three fields after float parse; sets editor+now; save+302 target history, leaves status/approval/submission metadata; exceptions uncaught (V6) | P audit/preservation; D validation; Q authority/status |
| PH-P04-D | GET root `?year=`, ACTIVE | int year/default July boundary, all ACTIVE profiles progress, approved year sum/goal/average, own all-status year events, render 200; invalid year can raise (V1) | P totals; D validation; Q flag |
| PH-P04-H | H1/H2 helper calls, internal arguments request/profiles/year/dates | date tuple, three-year list, querysets/sums/progress; no writes | P; Q invalid helper inputs |
| PH-P05-H | GET `brother/<int:user_id>/`, ACTIVE; H4 helper | any target profile approved history, year/lifetime totals, chair flag; missing profile message+302 dashboard (V4/H4) | P math; Q visibility |
| PH-P06-X | GET `export-philanthropy-hours/`, any logged-in User, no profile required | all-time approved events including inactive/profileless; active profile name else username; sorted full-name blocks, ascending dates, numeric hours; XLSX bytes+attachment, no DB/file writes (V5) | P output; Q scope/access; D identity/formulas |
| PH-P07-T | `hours_remaining(goal,current)` | float difference clamped at zero, used for ten-hour goal, no writes (T/UI) | P finite numbers; Q invalid inputs |
| PH-C03-A | standard Django admin list/add/change/delete model routes at configured admin prefix; staff with model permissions/superuser | standard forms/log entries; no chair-role check or domain audit override; default deletion also bulk action (A/M/R) | P framework permissions; Q business-rule parity |

## Actor and ownership matrix (current source, not approved policy)

`yes` means decorator permits execution, before parsing/lookup. `no` means
redirect+message, never event mutation; login_required outside D includes `next`
in login redirect, approval's outer D redirects to named login without `next`.
Use reverse names/settings, never guess configured login/admin URLs.

| Actor with explicit role set | P01/P04/P05 | P02 | P03 | P06 |
| --- | --- | --- | --- | --- |
| Anonymous | login | login via outer D | login | login |
| User without profile | no | no | no | yes, source exposure Q |
| Profile no roles / ALUMNI / NEW_MEMBER / EXEC only | no | no | no | yes, source exposure Q |
| ACTIVE only | yes | no | no | yes |
| PHIL_CHAIR only | no | no | yes | yes |
| ACTIVE+PHIL_CHAIR | yes | yes | yes | yes |
| ACTIVE+PHILANTHROPY_CHAIR only (synthetic invalid-choice role) | yes; dashboard flag true | no | no | yes |
| ACTIVE+EXEC without chair | yes | no | no | yes |

P01 always writes own record despite posted user/user_id. P02 sees/decides own
and others' events with no ownership guard. P03 edits own and others' requested,
approved or denied events. P05 exposes any target with a profile to any ACTIVE
actor, even a non-ACTIVE target; only its results exclude non-approved events.
P06 exports every approved owner regardless of requester, profile or ACTIVE
status. Django staff/superuser status alone does not bypass domain decorators;
admin separately requires staff plus Django model permissions. Verify denied
requests with and without a safe referrer; arbitrary external referrer redirects
in D are a shared security defect, not a required redirect destination.

## Named cases (33 designs, parameterized variants are explicit below)

Each case uses setup → action → response → state pseudocode. Priority P0 is an
authorization/data-integrity blocker; P1 is core behavior; P2 is robustness/UI.
All state references use the full snapshot rules above, including unchanged
unrelated records. Q cases are blocked expectations, not expected failures or
skips counted as completed coverage.

### Submission, transport and access

**PH-C01 — actor boundary matrix (P0, P/Q; all six routes).** Setup each matrix
actor separately, A/B profiles and requested/approved B events; snapshot. Action
GET every route and POST submit/approve/deny/edit with otherwise valid payloads
for each actor. Response assert current explicit decorator acceptance/denial,
message and safe fallback/referrer destinations; for P06 acceptance record Q6
instead of locking broad access as policy. For PHIL_CHAIR-only edit accepted
source behavior is a Q3 branch. State denied requests unchanged; accepted
mutations obey C04/C09/C14 only; reads unchanged. Dependencies shared D/auth
fixture (AUTHENTICATE owns shared decorator specification); resolve Q3/Q5/Q6 for final permission matrix; no “executive” fixture.

**PH-C02 — CSRF on every mutation (P0, P).** Setup ACTIVE A, combined chair C,
B's event; `Client(enforce_csrf_checks=True)` and snapshot. Action POST P01-S,
P02-A, P02-D and P03-E with missing and invalid tokens; response 403, unchanged.
Then GET the relevant form, extract token/cookie, POST valid token as authorized
actor; response follows successful action and only target fields change. No
claim that demo-entry CSRF assertions cover domain routes. Dependency middleware
and token helper; use independent clients, not default CSRF-bypassing client.

**PH-C03 — method safety and referrer (P1, D/Q; all HTTP operations).** Setup
actors with permitted roles, safe referrer, events snapshot. Action PUT/PATCH/
DELETE to submit/approve/edit and POST to dashboard/history/export, with crafted
payloads. Response source is render/download without domain write rather than
405; choose explicit permitted methods in Q9 before future adapter assertions.
State unchanged for all these requests. Denied role GET with no referrer uses
poll fallback; with same-site referrer uses that destination; an external
referrer must not become a future open redirect (shared D defect fix required).
Dependencies shared decorator/method policy.

**PH-C04 — own requested submission (P0, P; P01-G/S).** Setup ACTIVE A/B,
freeze T0; GET form → 200, CSRF, title/hours/date fields. POST hours='2',
event_title='Park cleanup', event_date='2026-07-01', forged user=B/user_id=B,
status='approved', approver/editor/time values. Response 302 dashboard plus
success. State exactly one new event owned by A, title/date/2 persisted,
requested, request time T0, approval/editor fields null; B and all old events
unchanged; no custom session effects. Dependencies clock/factory.

**PH-C05 — minimum and fractional precision (P0, D/Q; P01-S/P03-E).** Setup
A and chair C, existing integer-hours target; parameterize '0','-1','0.49',
'0.5','1.5','2.25','2.0'. Action submit each, then edit target each independently.
Response submission <0.5 error+200/no insert; edit currently has no minimum.
Read saved values afresh: model IntegerField conversion can truncate fractions
(e.g. 0.5→0), although view/template advertises half hours. Record discrepancy,
never approve truncation or zero-hour edits as contract. Q1 must choose precision,
allowed step and common minimum; then assert exact agreed decimal/integer value
or validation response with no change. Old target/unrelated rows unchanged on
rejection; successful edits change only C14 fields. Dependencies Q1/model migration.

**PH-C06 — malformed and non-finite hours (P0, D; P01-S/P03-E).** Setup A/C,
snapshot; parameterize missing hours, '', whitespace, 'abc', 'NaN', 'nan',
'Infinity', '-Infinity', '1e309', and a finite huge value '1e100'. Action valid
rest of submit/edit payload. Submission currently catches parse/save errors and
renders 200+error; edit may raise before save; NaN/positive infinity bypass
minimum comparison and fail integer conversion, huge finite range failure is
backend-dependent. Future response assert controlled field error, no raw
exception disclosure; state no new event and target/all other rows unchanged,
including editor/time. Do not assert incidental exception class or 500. Explicit
backend range and approved upper bound Q1 needed; test both supported DBs.

**PH-C07 — title/date field validation (P0, D/Q; P01-S/P03-E).** Setup A/C,
snapshot; for each field omit, blank, invalid date, impossible '2026-02-30',
100/101-character title, whitespace title, and Unicode/HTML-like title. Action
submit/edit with other fields valid. Source no form/full_clean: absent submit
keys caught, empty titles/overlength may reach DB, edit missing title/date may
fail or blank title persist; backend enforcement differs. After policy Q2 assert
normalized accepted text/date or field error, never truncated/lost data; valid
100-char and escaped HTML text render safely, no script execution. State failed
operations unchanged; accepted insert C04 or edit C14 whitelist only. Include
past/future date acceptance as Q2, not invented restriction. Dependencies Q2.

**PH-C08 — submit save failure and duplicate retry (P1, D/Q; P01-S).** Setup A,
snapshot; inject failure at model save before DB write → POST response current
error form, future controlled error; assert no new row/all old unchanged. Then
submit identical valid payload twice without injection: source creates two
rows; choose duplicate/retry policy Q8 before asserting one versus two. In
TransactionTestCase inject save wrapper that writes then raises: current broad
catch may leave committed row; target invariant is either committed success
with retry identity or rollback, not reported failure with silent write.
No storage mock; only deliberate failure boundary. Dependencies Q8/transactions.

### Decisions and audit

**PH-C09 — pending list and initial approval (P0, P; P02-G/A).** Setup combined
C, requested A/B events on distinct dates, approved/denied controls, audit null;
freeze T1. GET → 200 only requested rows descending date, both owners. POST
B requested event approve → 200 list excludes just target, success message.
State target approved, approver C's profile firstName+' '+lastName, approval
T1; owner/title/hours/date/request timestamp/editor fields unchanged; every
other event unchanged. No extra event/log row is created by domain helper.

**PH-C10 — initial denial (P0, P; P02-D).** Setup requested B target, C, T1.
POST deny → 200, target removed from pending, denial success message. State
status denied with C display name/T1; rest target metadata and all other rows
unchanged. Subsequent dashboard/history/export exclude target from approved
sums/content while own all-status dashboard still displays denied status.

**PH-C11 — missing/unknown IDs and actions (P0, D; P02-A/D).** Setup C and
requested target; snapshot. POST event_id missing, '', 'abc', nonexistent int;
response current 200+error, pending unchanged; future controlled validation/not
found response. Then target ID with action missing, '', 'bogus', 'pending' or
'requested': current helper saves unchanged target and falsely reports denied.
Assert future explicit error, no decision/audit change and no save signal side
effects. Do not freeze false success. State every row unchanged. Helpers called
directly with non-POST do nothing; direct POST helper has no auth guard, so
future domain operation must enforce agreed authorization as well as view.

**PH-C12 — repeated/reverse/self decisions (P0, Q; P02-A/D).** Setup combined
C/D, B targets in requested/approved/denied, C-owned requested target; clocks
T1/T2. Action approve→approve, deny→deny, approve→deny, deny→approve, own approve
and own deny in isolated subcases. Source allows all and rewrites latest
approver/date even repeats. Q4 must decide terminal/reversible states, idempotent
repeat audit semantics and self-review. Assert agreed transition/result;
forbidden/no-op actions preserve entire target including first audit; allowed
actions change only status/decision audit; all unrelated rows unchanged. Do
not choose a policy from pending-button visibility.

**PH-C13 — decision failure and competing chairs (P0, D/Q; P02-A/D).** Setup
requested B target/C/D, snapshot. Inject target save failure before write →
current 200 error and unchanged target/audit. TransactionTestCase write-then-raise
checks no false-failure commit per Q8. Race separate PostgreSQL connections,
bounded barrier between read and save, C approve versus D deny; source no
transaction/lock/version check and full saves permit lost updates. Choose Q4/Q8
winner/conflict semantics; assert one consistent final status+matching approver/
time and agreed audit history, never a mixed decision or lost concurrent edit.
SQLite cannot establish race guarantees. All unrelated records unchanged.

### Edits

**PH-C14 — chair edits and audit whitelist (P0, P/Q; P03-G/E).** Setup chair C,
A/B events of each status, original approval audit and editor D, T0 submission;
freeze T2. GET target → 200 editing form with exact original title/date/hours,
no state change. POST title='Updated', hours='3', date='2026-06-30', forged
owner/status/approver/request_date/editor → 302 target owner's history, success.
State only title/hours/date/last_edited_by=C/last_edited_at=T2 change; owner,
status, decision audit and submission time preserved; other rows unchanged.
Repeat at T3 sets latest editor/time without creating another event. Q3 decides
which statuses/own/other targets a chair may edit and whether approval should be
invalidated; accepted metadata preservation is subject to that decision.

**PH-C15 — edit lookup and parse failures (P1, P/D; P03-G/E).** Setup C and
B target/snapshot. GET/POST nonexistent numeric ID → 404, unchanged. Negative
or non-integer path does not resolve → 404 unchanged. POST missing/malformed
hours/date/title follows C06/C07; test editor/time remain original even though
assignments occurred in memory. GET must never set editor/time. Dependency route
resolver and validation repair; do not contract uncaught parse exceptions.

**PH-C16 — edit save failure/concurrent metadata (P0, D/Q; P03-E).** Setup
C/D and B target, snapshot. Inject save failure before write → future controlled
error, all target fields including old editor/time preserved; current uncaught
error is defect. TransactionTestCase save-then-raise checks Q8 rollback. For
PostgreSQL use independent connections and bounded barriers to approve while C
holds stale edit instance, and C/D edit same event. Full-row saves can overwrite
new status/audit; assert Q8 conflict handling or explicitly agreed merge,
preserving unrelated metadata and rejecting silent lost updates. Other rows
unchanged; no atomicity claim until implemented.

### Dashboard, helpers and history

**PH-C17 — July/June dates and default year (P1, P; P04-D/H).** Setup controlled
UTC times 2026-06-30 23:59:59 and 2026-07-01 00:00:00. Call date helper for 2025
→ (2025-07-01,2026-06-30); available years default → [2025,2024,2023] before
July and [2026,2025,2024] after; past=1→one, past=0→empty. GET dashboard with no
year → respective start and en-dash label; explicit year=2024 overrides clock.
State unchanged. Invalid past/year helper API contract deferred Q2; use aware
clock fixture, verify timezone.now rather than assuming browser local date.

**PH-C18 — approved chapter/own totals and goal (P1, P; P04-D/H).** Setup
ACTIVE A/B/zero-member C plus inactive D. Within 2025 AY give A approved 10,
B approved 5, A requested 40/denied 50; D approved 99; A approved outside AY 70.
GET year=2025 as A → chapter total15, active count3, average5, goal count1;
progress [A10,B5,C0] descending; own events contain only A in-range all statuses,
own approved total10. Assert no B own-list leak and all unrelated rows unchanged.
Parameterize approved totals 0/4/5/9/10/11 → goal false through9, true10/11,
remaining max(0,10-total); no double-count with multiple non-ACTIVE roles.

**PH-C19 — inclusive year and empty populations (P1, P; P04-D/H).** Setup A
with approved events 2025-06-30,2025-07-01,2026-06-30,2026-07-01 at distinct
hours; helpers and GET year=2025 include only middle two. Empty selected year
→ own empty list/0; every ACTIVE zero row retained; stats helper empty profiles
→ ([],0,0). To exercise view denominator zero, unit-invoke view with permitted
request while active-profile query deliberately yields empty (or use controlled
role removal after decorator authorization); assert average0/no divide by zero.
This query override is only for otherwise unreachable empty branch, business
aggregations remain real ORM. State unchanged.

**PH-C20 — malformed year and chair-name discrepancy (P1, D/Q; P04-D/H).**
Setup ACTIVE+PHIL_CHAIR C, snapshot. GET year missing uses C17; '', 'abc',
'2025.5', '0','9999', huge integer → source int/date may raise; future controlled
query validation, unchanged DB. Valid historical year outside dropdown is
currently accepted; Q2 chooses supported range. Correct PHIL_CHAIR produces
false dashboard chair flag while history true; synthetic ACTIVE plus
PHILANTHROPY_CHAIR produces dashboard true but cannot approve/edit. Q7 chooses
canonical name and flag removal/repair; do not create invalid-choice role in
shared production seed. Assert no UI link is a substitute for C01.

**PH-C21 — personal approved history and lifetime (P1, P; P05-H).** Setup
ACTIVE A, B profile; B approved 2025-06-30=2,2025-07-01=3,2026-06-30=4,
2026-07-01=5; B requested/denied 99, A approved70. GET B history and helper →
buckets descending starts [2026,2025,2024], totals[5,7,2], lifetime14, events
within bucket descending date; exclude A and non-approved B events. B empty
approved history → [], lifetime0 and empty text. Edited event displays [EDITED],
chair has edit links and nonchair does not. State unchanged. Use helper input
matching target; unused brother parameter must not mask user_id scope bugs.

**PH-C22 — history visibility/unknown target (P0, P/Q; P05-H).** Setup ACTIVE
A, ACTIVE B, inactive D, User E with no profile. GET own/B/D history: source
permits all; Q5 decides whether member-wide approved history is authorized.
Unknown user ID or E ID → message Brother not found+302 dashboard; state
unchanged. Anonymous/missing profile denied as C01. For final Q5 denial also
assert response contains no title/name/hours and no leaked target context.

**PH-C23 — hours_remaining valid arithmetic (P2, P; P07-T).** Setup no rows;
call (10,0)→10.0,(10,5)→5.0,(10,10)→0,(10,12)→0,('10','0.5')→9.5. Render both
using templates with safe synthetic context → remaining/requirement text,
escaped titles. State unchanged; SimpleTestCase, no DB needed. Fractional helper
arithmetic does not settle storage policy Q1.

**PH-C24 — hours_remaining invalid inputs (P2, Q/D; P07-T).** Setup no rows;
parameterize None,'',object(), 'NaN','Infinity','-Infinity', negative goal/current
and huge floats. Source float conversion may raise or yield misleading
non-finite/clamped result; Q10 defines supported helper inputs and fallback or
controlled validation. Assert agreed finite result/rejection, no incidental
crash-as-contract and no state effects. Dependency callers' validated totals;
no unnecessary mocking.

### Workbook export

**PH-C25 — workbook content and numeric totals (P1, P; P06-X).** Setup combined
chair, ACTIVE A/B with distinct display names, approved A events hours2/3 on
distinct dates, B10, requested/denied controls, missing approver, snapshot.
GET → XLSX MIME and attachment filename; `load_workbook(BytesIO(body),
data_only=False)` → sheet 'Philanthropy Hours'; sorted member blocks start A/F
(four data columns plus spacer), merged rows1/2, row3 Date/Event/Hours/Approved
By, row4+ ascending ISO dates and exact titles/numeric hours/approver or em dash.
Totals 'Total: 5'/'Total: 10' match parsed numeric rows; no controls; no duplicate
rows; boundary fills <5 red,5–9 yellow,>=10 green. Do not compare ZIP bytes or
incidental widths beyond usable Event wrapping. State all rows unchanged, no
persistent file; openpyxl dependency.

**PH-C26 — scope, active status and permissions (P0, Q; P06-X).** Setup
ACTIVE A, inactive D, profileless E, one approved row each across two AYs;
requested/denied controls. GET with `?year=2025&user_id=A` as ACTIVE, ALUMNI,
no-role and profileless actors → source exports all-time/all-owner approved,
active names and inactive/profileless usernames; query ignored. Q6 chooses
export actors, year scope and active-owner inclusion; final assertions must
restrict body to agreed scope and deny others without XLSX/content leakage.
Anonymous redirect per C01. Approved counts/totals not altered; all rows unchanged.

**PH-C27 — same-name identities (P0, D/Q; P06-X).** Setup distinct ACTIVE A/B
both 'Alex Example', approved hours2/7, optional inactive username colliding with
that display text. Export source merges by string into one block total9.
Future invariant preserve separate user identity and independently correct
hours/totals; Q6 chooses disambiguated display format. Parse every owner block,
assert each event once and no accidental cross-owner total; state unchanged.
Do not freeze name-based identity merge as contract.

**PH-C28 — spreadsheet formula text (P0, D; P06-X).** Setup ACTIVE name,
profileless username, event title and approver each separately beginning
'=1+1', '+SUM(A1:A2)', '-1+2', '@SUM(A1:A2)', tabs/newlines, and Unicode.
GET and parse with data_only=False; source writes raw strings, '=' can be
formula-typed by openpyxl. Future output preserves display text as text,
assert cell.data_type != 'f' for all user-supplied cells and agreed escaping
that also handles other spreadsheet clients. Do not execute a spreadsheet or
external link. Numeric hours remain numeric. State unchanged; sanitizer design
must avoid corrupting legitimate text and Q6 presentation.

**PH-C29 — empty/failing workbook (P1, P/D; P06-X).** Setup no approved events
(but requested controls); export → valid readable workbook with named sheet and
no member data, state unchanged. Inject Workbook.save serialization failure →
current uncaught error; future controlled error without partial XLSX/attachment
or private data disclosure, unchanged DB/files. In-memory buffer needs no disk
compensation. Mock only serializer failure; never mock event query or sums.

### Admin and model lifecycle

**PH-C30 — C03 admin permissions/list (P0, P; PH-C03-A).** Setup nonstaff
ACTIVE+PHIL_CHAIR, staff no permissions, staff view-only, separate add/change/
delete permission actors and superuser; synthetic A/B events. Under non-demo
admin-enabled test configuration reverse admin model URLs rather than fixed
prefix. List → only appropriate staff permission actors allowed; permitted list
shows configured five columns; nonstaff chair cannot enter. Read state unchanged;
permission-denied POST add/change/delete no writes/log entries. Demo settings may
block admin wholesale: test that separately with AUTHENTICATE, never mistake
blanket demo403 for ModelAdmin permission verification. Dependency safe non-demo
admin test settings supplied centrally, no runtime config secrets.

**PH-C31 — C03 admin add/change validation and audit (P0, P/Q; PH-C03-A).**
Setup authorized staff with explicit permissions and target audit, snapshot.
POST add with valid model data → admin redirect, one event, auto submission time,
one Django LogEntry; POST change approved/denied/status/owner/hours/title/date
→ standard model-form validation and log. Invalid status, missing required fields,
non-integer/NaN hours, overlong title/date errors → form response, no event/log
mutation. Standard IntegerField admin permits negative integers, allows owner/
status change, and does not automatically set domain editor or decision audit;
Q11 decides staff authority, minimum/precision and audit parity. Final allowed
updates assert explicit whitelist/preserved metadata, others unchanged; do not
bless admin bypass of settled invariants. Audit LogEntry is distinct from domain
approver/editor fields. Dependency Q1/Q3/Q4/Q11.

**PH-C32 — C03 delete/bulk delete and model cascade (P1, P/Q; PH-C03-A).**
Setup staff delete permission, two selected target events and unrelated B event;
GET confirmation unchanged, POST confirmed single then bulk delete selected
IDs → standard admin redirects, only authorized selected rows removed and
correct deletion log entries. With no delete permission response denied and
all unchanged. Q11 must approve whether deletion/audit retention is allowed.
Separately ORM delete event owner → owned event cascades; delete editor User
→ last_edited_by null on surviving other-owner events, other fields unchanged;
no hidden audit preservation claimed. Both are model lifecycle assertions,
subject to Q11 retention policy, unrelated profiles/events unchanged except
Django's documented ownership cascades.

**PH-C33 — cross-operation aggregate consistency (P0, P/Q; P01/P02/P03/P04/P05/P06).**
Setup ACTIVE A/B and combined C, approved B control; submit A integer2 (C04),
assert requested excluded from all approved totals but visible own dashboard;
approve at T1 → dashboard/year history/export each gain exactly2; edit to3/date
crossing AY boundary at T2 → agreed Q3 reapproval semantics, no double-count,
expected year bucket movement, lifetime/export consistent with current status;
deny/reverse only once Q4 resolved → all approved projections exclude denied.
Assert only intended target whitelist changes at each step, submission time/
owner and unrelated B remain unchanged. Reuse business assertions across future
API/legacy adapters; Q1/Q3/Q4/Q6 block final end-to-end expectations.

## Completeness and existing assertion gaps

| Operation | Cases |
| --- | --- |
| PH-P01-G | C01,C02,C03,C04 |
| PH-P01-S | C01–C08,C33 |
| PH-P02-G | C01–C03,C09 |
| PH-P02-A | C01–C03,C09,C11–C13,C33 |
| PH-P02-D | C01–C03,C10–C13,C33 |
| PH-P03-G | C01–C03,C14,C15 |
| PH-P03-E | C01–C03,C05–C07,C14–C16,C33 |
| PH-P04-D | C01,C03,C10,C17–C20,C33 |
| PH-P04-H | C17–C20 |
| PH-P05-H | C01,C03,C10,C14,C21,C22,C33 |
| PH-P06-X | C01,C03,C10,C25–C29,C33 |
| PH-P07-T | C18,C23,C24 |
| PH-C03-A | C30–C32 |

Case references abbreviate PH-Cxx. All 13 operations map to at least one named
case; this is design completeness, not a measured coverage percentage.

`PHILANTHROPY/tests.py` contains zero assertions. Demo E tests seed count9 and
nonprivileged demo users, anonymous dashboard302, executive dashboard/request/
approval GET200, ACTIVE dashboard200/approval302, and integer-hours submission
302 plus existence by user/title. They do not assert stored hours/date/status/
audit, ownership-forgery resistance, narrow chair roles, missing profiles,
CSRF for these routes, decisions, edit/history/export/admin/tag behavior,
invalid input, transitions, totals or failure atomicity. No existing assertion
establishes any of the complete named cases above. Shared demo seed/admin-block
coverage belongs to HOME/AUTHENTICATE; reuse only their infrastructure, not their
privileged personas as proof of this matrix.

## Decisions, defects and dependencies before implementation

| Decision | Required policy; source risk and affected cases |
| --- | --- |
| Q1 | Integer versus fractional hours, allowed granularity, shared minimum and finite upper bound. View/template half-hour input conflicts with IntegerField; silent conversion/data loss D. C05–C07,C31,C33 |
| Q2 | Required/trimmed title, max length, date range and valid selected year/helper inputs. Missing form validation and uncaught errors are D, not compatibility rules. C07,C17,C20 |
| Q3 | PHIL_CHAIR-only versus ALL ACTIVE+chair editing, statuses/own targets, approval invalidation on edit. Source rules differ from approval; metadata preservation alone cannot settle policy. C01,C05,C14,C16,C33 |
| Q4 | Self-review, terminal/reverse transitions, duplicate decision idempotency and audit retention. Source overwrites decision identity/time; no immutable history. C12,C13,C33 |
| Q5 | Whether any ACTIVE member may see another/inactive member's approved history; final object permissions. C01,C22 |
| Q6 | Export roles, ownership/year/ACTIVE scope and identity-disambiguation. Login-only all-time exposure is not an approved access contract; merging names D, formula text D. C01,C25–C28,C33 |
| Q7 | Canonical PHIL_CHAIR name and remove/repair unused dashboard flag; PHILANTHROPY_CHAIR is absent from choices. C20 |
| Q8 | Submission retries, transaction boundaries, error-after-write compensation, conflict strategy for decisions/edits. Current full saves/no atomic blocks permit lost updates; avoid claimed guarantees until PostgreSQL tests. C08,C13,C16 |
| Q9 | Explicit allowed methods and legacy versus API validation/error adapters; shared referrer security repair. C03 |
| Q10 | Tag invalid/non-finite inputs and whether caller guarantees only validated finite numbers. C24 |
| Q11 | Admin's authority to alter owners/status/audit, negative hours, hard deletion and audit retention. Standard Django permissions currently differ from business roles. C30–C32 |

Additional confirmed defects: H3 unknown action saves/reports denial without
making a decision; request exposes raw exception details; edit/dashboard invalid
input may cause uncaught errors; raw formula-like cells become active formulas.
Remediation is outside Wave 1. No test should preserve these defects as passing
business contracts or count expected failures as completed coverage.

Shared interfaces proposed, not implemented: `make_user(roles=(), with_profile=True,
**fields)`, `make_profile(user, **fields)`, aware controlled-clock helper, snapshot/
refresh helper, enforced-CSRF client helper, and a centrally supplied admin-enabled
safe test settings variant. Domain-local `make_event(owner, status, hours, date,
**audit)` may build real ORM records with explicit timestamps. Role factory must
separate Django staff/model permissions from domain roles; decide whether to
reject undeclared role names except C20's deliberate invalid-choice fixture.
Use TestCase for ORM/request cases, SimpleTestCase for pure dates/tag, and
TransactionTestCase for deliberate post-write failure and PostgreSQL races.
No external calls or uploads; temporary BytesIO workbooks only. openpyxl is an
existing import/dependency; no new dependency installation requested.

Proposed singular `test/` layout is in [README](README.md). Keep
`assertions.py` reusable for owner/status/hour/audit/totals/workbook invariants;
legacy request tests own redirects/messages/templates/HTTP200 error behavior.
Future DRF adapters may return explicit validation403/404/409 responses after
Q9; core invariants remain independent of transport.

## Actual checks and ordered Wave 2 checklist

Executed only read-only branch/commit queries, file enumeration, line-numbered
source reads and targeted text searches; reviewed these two documents for scope
and source references. No application tests, migrations, dependency installation,
network calls, real data or secret/config values were accessed. The shared
baseline is coordinator-owned. No runtime or race guarantee is claimed.

1. Coordinator source-verifies this spec/13-operation matrix at recorded commit;
   reconcile shared D semantics, fixtures and safe admin settings with owners.
2. Resolve Q1,Q3,Q4,Q5,Q6,Q8,Q11 first; record approved decisions and remediation
   scope. Decide remaining Q2/Q7/Q9/Q10 before their assertions are finalized.
3. Establish safe synthetic settings and factories, controlled UTC clock,
   explicit role sets, enforced-CSRF helper and unrelated-row snapshot assertions.
4. Create singular test package/files, resolve coexistence with scaffold
   `tests.py`, verify explicit-package and app-label discovery/counts; keep
   setup documentation portable (.venv), never assume coordinator venv path.
5. Implement P0 authorization/CSRF/owner-audit/precision/transition/export/admin
   invariants first, with agreed defect fixes tracked separately from tests.
6. Implement P1 statistics/year/history/XLSX parsing and serializer/save failures;
   then P2 tag/render cases. Assert fresh DB state for success and denial.
7. Use approved PostgreSQL environment for independent-connection bounded races
   and post-write failure rollback; SQLite success cannot close those items.
8. Run targeted domain suite then coordinator shared integration baseline, record
   exact discovered counts/results and blockers; only claim coverage after an
   actual measurement with declared tooling. Update transport adapters during
   migration without dropping approved business assertions.
