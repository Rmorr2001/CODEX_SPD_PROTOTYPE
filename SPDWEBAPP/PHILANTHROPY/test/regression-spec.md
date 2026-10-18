# Philanthropy regression specification — Wave 1.5

## Baselines and status

Repository `Rmorr2001/CODEX_SPD_PROTOTYPE`, branch `prototype/railway`.
Source baseline: `7e25ac2f06b2d88a0220526771585f30df10c57a`.
Documentation refinement baseline/current inspected HEAD: `c8bbc4e`.
Root AGENTS.md, the full Wave 1.5 prompt, both original domain documents and the
[shared fixture contract](../../../docs/testing/fixture-contract.md) were read.
No nested domain guidance was found. This refinement changes Markdown only.

[The case index and parent mapping](case-index.md) replace all 33 dense old groups
with 118 designs: 66 READY, 41 POLICY_BLOCKED, 11 NEEDS_FIX, 0 INFRA_BLOCKED.
READY means expected-current preservation, not execution or policy approval.
Blocked designs state safety invariants and explicit decision branches without
pretending undefined policy is a settled result. None of the cases ran.

## Source inventory

All paths in this table are beneath `SPDWEBAPP/`; cases cite full repository paths.
Line references are from the source baseline; inspection did not execute behavior.

| Source | Symbols and evidence |
| --- | --- |
| `SPDWEBAPP_CORE/urls.py:23–33`; `PHILANTHROPY/urls.py:4–11` | Configured admin mount and all six mounted domain routes |
| `PHILANTHROPY/views.py:14–57` | philanthropy_dashboard; ACTIVE, year parse, chapter stats, average, unused chair flag |
| `PHILANTHROPY/views.py:59–81` | philanthropy_request; float/minimum, own requested event, caught save errors |
| `PHILANTHROPY/views.py:83–95` | philanthropy_approve; ALL PHIL_CHAIR+ACTIVE, pending list and helper |
| `PHILANTHROPY/views.py:98–120` | brother_philanthropy_history; ACTIVE, any target profile, declared chair flag |
| `PHILANTHROPY/views.py:137–239` | export_approved_philanthropy_hours; login only, all approved events, name grouping/XLSX |
| `PHILANTHROPY/views.py:243–269` | philanthropy_edit_event; PHIL_CHAIR alone, full save, last editor/time, no minimum |
| `PHILANTHROPY/views_functions.py:8–20` | get_academic_year_dates/get_available_academic_years; July–June and three starts |
| `PHILANTHROPY/views_functions.py:22–61` | get_user_events_and_total_hours/collect_philanthropy_statistics; approved sums, goal>=10 |
| `PHILANTHROPY/views_functions.py:64–86` | philanthropy_approval_POST; status/audit overwrite, unknown-action false success |
| `PHILANTHROPY/views_functions.py:89–123` | retrieve_individual_brother_history; approved year buckets/lifetime, unused brother argument |
| `PHILANTHROPY/models.py:5–52` | IntegerField hours, statuses, owner, auto submission time, nullable decision/editor; no save/clean override |
| `PHILANTHROPY/admin.py:8–16` | PhilanthropyHoursEventAndRequestAdmin; ordinary permissions/forms/log, five columns |
| `PHILANTHROPY/templatetags/philanthropy_extras.py:5–7` | hours_remaining; max(0,float(goal)-float(current)) |
| `PARLEYPRO/pp_decorators.py:7–52` | requires_role; authenticated+ALL roles, missing profile/role, referrer-or-poll redirect |
| `AUTHENTICATE/models.py:58–99` | Role/Brother_Profile; declared PHIL_CHAIR, no declared PHILANTHROPY_CHAIR |
| `PHILANTHROPY/templates/philanthropy_request.html:9–24` | POST CSRF; event_title/hours/event_date; UI step/min0.5 |
| `PHILANTHROPY/templates/philanthropy_approve.html:11–50` | Pending UI, hidden event_id and approve/deny POST buttons with CSRF |
| `PHILANTHROPY/templates/philanthropy_dashboard.html:19–25,33–34,77–92,139–165` | GET year, own all-status events, history/export links and remaining tag |
| `PHILANTHROPY/templates/philanthropy_brother_history.html:16–61` | Buckets, edited marker, chair link, remaining tag, empty history |
| `railway_demo/middleware.py:4–12` | Blanket /admin/ demo403 differs from domain admin permissions |
| `PHILANTHROPY/tests.py:1–3`; `railway_demo/tests.py:31–40,54–77,99–109` | Empty scaffold and existing seed/status/submission-existence assertions |

All six views and every domain helper are used. No domain forms, custom model
hooks, upload/delete views, session business mutations or JavaScript API writes
were found. Export uses an in-memory buffer, not persistent storage. Commented
export/edit role checks are inactive. Dashboard's PHILANTHROPY_CHAIR flag is
unused by its template; history's PHIL_CHAIR flag controls links only.

## Operation inventory and case completeness

Routes below follow /philanthropy/. Mutation operations may add messages but
have no intended arbitrary session/file effects. Reads leave named rows unchanged.
Case files contain concrete payloads, responses and field-level state assertions.

| ID | Route/callable | Current actor/input → response and effects | Case parents |
| --- | --- | --- | --- |
| PH-P01-G | GET request/ | ACTIVE →200 form/CSRF, no event write | C01,C02,C04 |
| PH-P01-S | POST request/ | ACTIVE, title/hours/date → own requested row,302 dashboard; error200 | C01–C08,C33 |
| PH-P02-G | GET approve/ | ALL chair+ACTIVE →200 requested rows descending date | C01–C03,C09 |
| PH-P02-A | POST approve/, action=approve | Same roles, event_id → approved+name/time,200 pending list | C01–C03,C09,C11–C13,C33 |
| PH-P02-D | POST approve/, action=deny | Same roles, event_id → denied+name/time,200 pending list | C01–C03,C10–C13,C33 |
| PH-P03-G | GET edit/<int:event_id>/ | PHIL_CHAIR alone →200 populated form or404 | C01–C03,C14,C15 |
| PH-P03-E | POST same | Chair, title/hours/date → edit/editor/time,302 owner history; uncaught errors | C01–C03,C05–C07,C14–C16,C33 |
| PH-P04-D | GET root, year | ACTIVE →200 own events, approved totals/goal/average; int/date may raise | C01,C03,C10,C17–C20,C23,C33 |
| PH-P04-H | H1/H2 year/stat helpers | Internal dates/profiles/request → inclusive dates/querysets/sums, no writes | C10,C17–C19 |
| PH-P05-H | GET brother/<int:user_id>/; H4 | ACTIVE, any target →200 approved buckets/lifetime; absent profile302 | C01,C03,C10,C20–C23,C33 |
| PH-P06-X | GET export-philanthropy-hours/ | Any login, ignores scope query → all-time approved XLSX, no DB/file writes | C01,C03,C25–C29,C33 |
| PH-P07-T | hours_remaining | Float-convertible operands → nonnegative difference | C23,C24 |
| PH-C03-A | Standard admin add/change/list/delete/bulk | Staff+model permissions → forms, data changes and Django LogEntry | C30–C32 |

Approval has no owner/current-status check. Unknown action saves and reports
“denied”; repeated/reverse actions overwrite decision audit. Edit updates full
rows without locking/transaction or approval invalidation. Other HTTP methods
fall through read-like behavior; these are Q9 designs, not accepted API contracts.

## Current role/ownership matrix

Decorator acceptance precedes parsing/lookup. It is evidence, not permission to
freeze broad visibility or chair-only edits as product policy. “Denied” means
message+302 with no event write. AUTHENTICATE owns shared decorator specifications.

| Actor roles/profile | P01/P04/P05 | P02 | P03 | P06 |
| --- | --- | --- | --- | --- |
| Anonymous | Login | Login via outer role decorator | Login | Login |
| No profile | Denied | Denied | Denied | Source permits; Q6 |
| No roles / ALUMNI / NEW_MEMBER / EXEC only | Denied | Denied | Denied | Source permits; Q6 |
| ACTIVE only / ACTIVE+EXEC | Permitted | Denied | Denied | Source permits; Q6 |
| PHIL_CHAIR only | Denied | Denied | Source permits; Q3 | Source permits; Q6 |
| ACTIVE+PHIL_CHAIR | Permitted | Permitted | Permitted, target policy Q3 | Source permits; Q6 |
| ACTIVE+undeclared PHILANTHROPY_CHAIR | Permitted, wrong flag Q7 | Denied | Denied | Source permits; Q6 |

P01 ignores forged owner/status/audit and creates only request.user's event.
P02 sees and decides own/other requested rows; direct POST can address any status.
P03 accepts own/other targets of every status. P05 accepts any target profile,
including inactive targets, but returns only that person's approved events (Q5).
P06 includes inactive/profileless approved owners, ACTIVE name otherwise username,
and groups by that display string (Q6/D9). Staff/superuser grants no domain role;
admin requires Django staff/model permissions separately. login_required's outer
wrapper includes next; approval's outer requires_role redirects without next.

## Decisions and defects

The safety assertions in NEEDS_FIX cases are separate from unresolved choices.
A POLICY_BLOCKED primary label takes precedence whenever its expected outcome
still depends on a decision. Additional defect/infra blockers remain listed.

| Decision | Candidate outcomes needing confirmation |
| --- | --- |
| Q1 | Integer-only versus fractional storage; accepted step, shared minimum and finite maximum |
| Q2 | Title trimming/required/max handling, permitted event dates/year range, helper preconditions |
| Q3 | Chair-only versus ACTIVE+chair edits; target owners/statuses; retained approval versus reapproval |
| Q4 | Self-review allowed/denied; repeats idempotent/rejected; reversal and decision audit retention |
| Q5 | Member-wide approved history versus self/chair-limited object visibility |
| Q6 | Export actors, year/owner/ACTIVE scope, fallback names and disambiguated identity labels |
| Q7 | Canonical PHIL_CHAIR flag versus removing unused dashboard flag; undeclared-role handling |
| Q8 | Duplicate submissions versus retries; rollback versus reported commit; merge/version/lock conflicts |
| Q9 | Permitted methods and controlled legacy/API error transport; no incidental500 contract |
| Q10 | Tag operand preconditions versus explicit validation/finite fallback |
| Q11 | Admin business-rule parity/exceptions; owner/status/domain-audit edits and deletion retention |
| Q12 | Formula-like text protection across named spreadsheet clients and reversible text escaping |

| Defect | Specific unsafe behavior and repair invariant |
| --- | --- |
| D1 | Untrusted HTTP_REFERER redirect; denied requests must stay on a safe local destination |
| D2 | float inputs reach IntegerField; accepted values must never silently truncate |
| D3 | Edit parse/save exceptions escape; rejected edit must be controlled and preserve persisted fields |
| D4 | Request renders raw exception details; public error must omit internal exception text |
| D5 | Unknown approval action falsely saves/reports denied; reject without write/success |
| D6 | Direct decision helper trusts actor; protected callable must enforce decision authority |
| D7 | Malformed dashboard year raises; query validation must be controlled |
| D8 | Dashboard chair role name differs from declared/history role; resolve Q7 |
| D9 | Same display name merges distinct owners; keep identities/totals separate |
| D10 | Equals-prefixed raw user text becomes an XLSX formula; literal text must not be formula typed |
| D11 | Workbook serialization errors escape; return no partial attachment or traceback |

Lost updates, post-write false failures and audit replacement risks additionally
require Q3/Q4/Q8 rather than an invented winner/rollback guarantee. No Wave 1.5
application fixes are authorized. No expected failures/skips count as coverage.

## Fixtures, failure boundaries and existing gaps

Use the shared fixture contract exactly: explicit username/roles, make_user,
make_profile only for a missing profile, login_actor, csrf_client, temporary_media,
at_time, snapshot_scope and assert_unchanged. No parallel shared helper API is
proposed. Corrupt-role setup C20d deliberately uses local ORM to bypass declared
role validation. Domain-local event construction stays thin and explicit.

Named snapshots include affected rows, unrelated controls and their specified
role/permission relations. Successful mutations allow only named fields; every
denied/error/read case states what is unchanged. Compare refreshed ORM values
and event/log counts. Messages and CSRF may alter session metadata; session user
identity stays fixed. At_time patches each view/model import actually consumed.

Mock only deliberate failure boundaries, not aggregate math or authorization.
Pre-write failures differ from write-then-raise cases. Workbook parsing uses
openpyxl with data_only=False, inspecting values/types/totals, never ZIP bytes.
No storage compensation is assumed for an in-memory export. Pure helpers use
SimpleTestCase; ORM requests use TestCase; post-write and PostgreSQL connection
races require TransactionTestCase, bounded barriers and independent connections.
The unwrapped empty-dashboard branch is not an authorization test or mocked query.

Existing PHILANTHROPY/tests.py has no assertions. Demo tests cover seed count9,
nonprivileged demo users, anonymous dashboard302, privileged GET statuses,
ACTIVE dashboard200/approval302 and integer submission302 plus existence.
They do not assert saved hours/date/status/audit, forged ownership, narrow chair
roles, CSRF on these four mutations, decisions/transitions, edit behavior,
statistics/history/export/tag/admin, invalid inputs, retries or races. Demo
/admin/ blanket403 is AUTHENTICATE's boundary coverage, not proof of ModelAdmin
permissions; business safe settings are required for C30–C32.

## Wave 2 sequence and actual validation

1. Coordinator verifies source references and the [118-case index](case-index.md),
   including all 33 old parents and shared fixture compatibility.
2. Resolve Q1/Q3/Q4/Q5/Q6/Q8/Q11 first; then Q2/Q7/Q9/Q10/Q12. Keep defect repair
   changes separate from documentation/test implementation authorization.
3. Implement shared safe settings/factories and discovery under singular test/;
   resolve tests.py coexistence and retain demo assertions.
4. Implement READY authorization/CSRF, integer submissions and initial decisions;
   follow with real-ORM statistics/history, workbook parsing and admin permissions.
5. Implement NEEDS_FIX safety assertions alongside separately authorized fixes;
   turn policy cases into concrete assertions only after decisions are recorded.
6. Establish PostgreSQL independent connections and bounded failure/race facilities;
   SQLite cannot close the concurrency claims. Verify post-write outcomes explicitly.
7. Run targeted suites/shared baseline only in Wave 2, recording actual discovery,
   results and remaining blockers. No numerical coverage claim without measurement.

This refinement performed read-only source/baseline checks and document structure,
ID/name uniqueness, parent completeness, link/anchor, status-count and whitespace
validation. No app tests, migrations, installs, Git mutations, secret reads or
network calls were performed. All proposals await coordinator review.
