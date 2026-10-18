# MISC regression specification

Historical design record; Wave 2 execution is recorded in
[wave-2-findings.md](wave-2-findings.md) and [case-map.json](case-map.json).

## Evidence and execution boundary

Inspected branch `prototype/railway`, commit
`7e25ac2f06b2d88a0220526771585f30df10c57a`, checkout
`/workspace/CODEX-SPD-PROTOTYPE`, assigned repository
`Rmorr2001/CODEX_SPD_PROTOTYPE`. Read root `AGENTS.md` and the complete
`docs/testing/wave-1-agent-prompt.md`; no nested MISC guidance was found.
Source baseline remains `7e25ac2`; documentation-refinement baseline is `c8bbc4e`.
This is proposed design, not executed results or approved policy. Only source
reads, branch/commit identification and documentation review were performed;
application checks/tests are reserved to the coordinator. No secrets, real uploads,
private data, network calls, installs or application/Git changes were used.

Source index (all paths repository-relative):

| Ref | Source and observed responsibility |
| --- | --- |
| S1 | `SPDWEBAPP/MISC/models.py:4-24`: DayLightSavingsAlert fields/default/string; AnnouncementAlert required title/content, active default, automatic timestamps/string. No custom save/delete, ownership, audit model or singleton constraint. |
| S2 | `SPDWEBAPP/MISC/admin.py:4-12`: stock ModelAdmin registration; DST exposes is_active/name, announcement exposes only title/content. No custom permissions/actions/save hooks. |
| S3 | `SPDWEBAPP/MISC/utils.py:4-28`: Chicago aware now; second March Sunday and first November Sunday at local 02:00, current/next year; strict future min. |
| S4 | `SPDWEBAPP/MISC/templatetags/dls_tags.py:8-36`: namespaced inclusion tag; utility runs before setting lookup, first record controls visibility/name; defaults visible; only DoesNotExist caught. |
| S5 | `SPDWEBAPP/MISC/views.py:4-20`: unused view; utility/message then unnamespaced `dls_alert.html` render, without settings override. `MISC/urls.py` is empty. |
| S6 | `SPDWEBAPP/MISC/templates/MISC/dls_alert.html:3-42`: conditional button/popup, message marked safe, local toggle script. `announcement_alert.html:7-38`: conditional rows, normal escaped title/content, updated timestamp preferred, client-only close. |
| S7 | `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:23-34`: configured admin prefix and five app includes; no MISC include. `railway_demo/urls.py:4` includes that root. |
| S8 | `SPDWEBAPP/AUTHENTICATE/urls.py:6`, `views.py:26-35`, `templates/AUTHENTICATE/dashboard.html:1-34`: `/auth/dashboard/`, login required, NEW_MEMBER redirect, active-only announcements and DST tag. |
| S9 | `SPDWEBAPP/HOME/views.py:4-12`, `urls.py:5`, `templates/HOME/home.html:1-30`, `templates/HOME/main.html:1-73`: unused announcement import; homepage context and shared base have no MISC integration. |
| S10 | `SPDWEBAPP/NEWMEMBER/views_functions.py:190-192`: role check dereferences brother_profile; absent profile can raise. |
| S11 | `SPDWEBAPP/MISC/migrations/0001_initial.py:14-24`, `0002_announcementalert_alter_daylightsavingsalert_options.py:13-24`, `0003_announcementalert_is_active_and_more.py:13-21`: schema history agrees with fields above. |
| S12 | `SPDWEBAPP/MISC/tests.py:1-3`: placeholder; `railway_demo/tests.py:49-77,88-97`: page status/access and admin block, no MISC semantic assertions; `railway_demo/middleware.py:10-11`: public `/admin/` returns 403. |

## Operations and classification

P = preserve inspected behavior that is suitable as a candidate contract;
D = defect, with desired outcome requiring a fix rather than blessing the crash,
bypass or unsafe rendering; Q = explicit business decision needed. References
above supply symbols and lines for every row. IDs remain stable across migration.

| ID | Route/action or callable; actor; input | Response and effects | Class |
| --- | --- | --- | --- |
| MISC-O01 | dashboard announcement selection (S8); authenticated eligible reader; active/inactive rows | Active rows in context/fragment; no record/session/file/audit mutation | P; ordering Q |
| MISC-O02 | dls_alert (S4); template caller; zero/one/many settings and computed date | show_alert/message/next_change; first PK setting wins in unordered queryset; no writes | P defaults; singleton Q |
| MISC-O03 | get_next_dst_change (S3); internal caller; aware Chicago now | Aware next strictly future candidate; no persistence | P calendar dates; fall instant D/Q |
| MISC-O04 | namespaced announcement fragment (S6); supplied context | Escaped title/content, timestamp and local close; no backend write | P |
| MISC-O05 | namespaced DST fragment (S6); tag context | Hidden or button/overlay/popup and toggle JS; override rendered safe | P visibility; unsafe HTML D/Q |
| MISC-O06 | daylight_savings_alert (S5); direct caller, any user/method | Message/always visible context then missing unnamespaced template; no mounted URL or mutations | D/Q retirement or repair |
| MISC-O07 | AnnouncementAlert ORM create/update/string (S1); internal trusted caller | Defaults/automatic timestamps/title string; no extra hook or validation on save | P; validation boundary Q |
| MISC-O08 | DayLightSavingsAlert ORM create/update/string (S1); internal trusted caller | Active default, optional nullable name, string reflects active; multiple rows allowed | P; multiplicity Q |
| MISC-O09 | admin announcement list/add/change (S2,S7); active staff + respective Django model permission; title/content | Standard admin HTML/form errors/redirect and LogEntry on mutation; is_active/timestamps/id not editable | P fields; activation UI Q |
| MISC-O10 | admin DST list/add/change (S2,S7); active staff + respective permission; is_active/name | Standard admin HTML/errors/redirect and LogEntry; is_active checkbox absent means false | P |
| MISC-O11 | both model admin detail delete and bulk delete_selected (S2,S7); active staff + delete permission; PK/action list/confirmation | Confirmation GET/POST then deletes selected rows and admin logs; no owner relation/files | P; last-setting fallback Q |
| MISC-O12 | integration boundary (S7-S10); anonymous/roles/missing profile; mounted dashboard/home and resolver | Anonymous login redirect, NEW_MEMBER redirect before MISC query; eligible renders; home no MISC; missing profile can fail | P boundaries; missing-profile D/Q |

Admin paths must use reverse names `admin:MISC_announcementalert_{changelist,add,change,delete}`
and `admin:MISC_daylightsavingsalert_{changelist,add,change,delete}`. Resolve the
configured prefix without reading its value from secrets or hardcoding `/admin/`
as a universal production prefix. No `/misc/`, DST API or announcement API exists.
Stock admin history is an audit read boundary, covered with mutation log checks.

## Actor, permission and ownership matrix

| Actor | Mounted dashboard/MISC reading | Admin operations in isolated admin-enabled test settings |
| --- | --- | --- |
| Anonymous | Login redirect; no fragment disclosed | Login redirect for admin GET; CSRF can reject unsafe anonymous POST first |
| Profile with no roles; ACTIVE only; ALUMNI only; PRESIDENT only | All eligible; no ALL/ANY role requirement for MISC | Nonstaff denied admin regardless of chapter role |
| NEW_MEMBER only; NEW_MEMBER+ACTIVE; NEW_MEMBER+PRESIDENT | Any presence of NEW_MEMBER triggers redirect, no announcement/tag render | Chapter role combination grants no admin permission |
| Authenticated without profile | check_user_role can raise; decision/fix required | Staff Django permissions operate independently of profile |
| Inactive staff / staff without permissions | Dashboard subject to profile/role behavior | Inactive staff cannot enter; staff without permission cannot list/add/change/delete either model |
| Active staff, view only | Same dashboard policy | List/detail view allowed; no add/change/delete |
| Active staff, add only / change only / delete only, separately per model | Same dashboard policy | Add permits creation; change also permits reads; delete alone has no list access. Verify direct requests. |
| Staff with announcement permissions only, or DST permissions only | Same dashboard policy | Other model denied; add+change does not grant delete |
| Active superuser (synthetic, non-demo) | Same dashboard policy, including NEW_MEMBER check | Both models allowed; not a substitute for narrow-role tests |
| Reader A and reader B; staff A-created and staff B-created records | Same global active announcements/setting; neither model has owner field | Permissions model-wide, no creator/owner restriction in current implementation |

Demo middleware's 403 is independently preserved by AUTHENTICATE; it cannot
establish C03 model authorization. Use the agreed shared business settings mode
for C03 authorization; do not disable a deployed boundary.

## Refined case index and execution status

[Case/status index, complete original mapping and operation mapping](case-index.md)
links 30 original parent groups to 103 independent designs: 80 READY,
20 POLICY_BLOCKED, 2 NEEDS_FIX and 1 INFRA_BLOCKED. No proposed case was run.
READY means an expected-current passing preservation design once the ordinary
shared harness exists; it is not an approval or measured coverage statement.

Detailed workflows:

- [Announcement fields, filtering and escaping](cases/announcements.md)
- [Alert defaults, selection and controls](cases/alerts.md)
- [Chicago calendar and deliberate utility failures](cases/calendar-failures.md)
- [Mounted boundaries and the unmapped callable](cases/integration.md)
- [Admin capability and permissions](cases/admin-permissions.md)
- [Admin forms, writes and malformed requests](cases/admin-writes.md)
- [Admin CSRF, delete, transactions and audit](cases/admin-audit-failures.md)

Use the exact [shared fixture contract](../../../docs/testing/fixture-contract.md).
`make_user` always has explicit username; `make_profile` only creates the missing
profile. Settings modes are `business` and `demo`; shared interfaces include
`login_actor`, `csrf_client`, `at_time`, `snapshot_scope`, `assert_unchanged`.
They are agreed interfaces, not installed helpers. Grant real Django permissions
through ORM; no parallel factory, settings module, harness or CI is introduced.
`at_time` must patch `MISC.utils.datetime.now(tz)` and Django model/log clocks
when those are asserted. Patching timezone.now alone cannot freeze this utility.

Use TestCase/real ORM for ordinary cases, SimpleTestCase for pure date logic,
TransactionTestCase for commit/rollback. Mock only render/external/failure seams
explicitly identified in cases; do not mock filtering, role logic or persistence.
Refresh named rows and compare relation sets. Reads/denials compare session
identity, not an identical session blob; CSRF metadata/messages may change.
No MISC operation has uploads/exports, file storage, business ownership or custom
commit hooks. No storage compensation claim is made. Admin writes permit only
the named fields, automatic timestamps, stock LogEntry and message transport.
Compare unrelated model rows and second actors' identities as specified.

## Defects, decisions and current evidence

| Defect | Source-backed finding | Independent safety design |
| --- | --- | --- |
| D1 | Setting name reaches message\|safe; executable HTML can be emitted (S4/S6). | T10a NEEDS_FIX; harmless presentation remains Q3/T10b. |
| D2 | Fall candidate is 02:00 CST=08:00Z, one hour after 2026 physical rollback. | T13a NEEDS_FIX; candidate/exact-at decisions remain Q4. |
| D3 | Unmounted direct view requests absent unnamespaced dls_alert.html (S5). | T17c POLICY_BLOCKED because retire/repair is Q7. |
| D4 | Dashboard role helper can raise for absent profile (S8/S10). | T20a POLICY_BLOCKED because safe transport is Q8. |

| Decision | Candidate outcomes and owner |
| --- | --- |
| Q1 | Announcement order: newest-first, oldest-first or unspecified; product/coordinator. |
| Q2 | DST singleton versus first-PK precedence; absent row enables default or stays disabled; product. |
| Q3 | Escape literal override text or permit sanitized harmless rich text; product/security. |
| Q4 | Physical transition versus compatibility label, strict/inclusive exact instant, normalized spring label; product/coordinator. |
| Q5 | Future service/form validation boundary and permitted blank values; migration owner. |
| Q6 | Unavailable fragment with 200 versus explicit safe error, error logging; cross-domain owner. |
| Q7 | Remove direct view or repair template, with separately decided route/auth/method if mounted; coordinator. |
| Q8 | Missing profile: controlled denial, profile setup redirect or restricted dashboard; AUTHENTICATE. |
| Q9 | Expose active field/action or retain trusted ORM control; last-delete/deactivate policy; admin/product. |
| Q10 | Sequential/concurrent last writer wins versus version conflict/retry; migration owner. |
| Q11 | Business audit event schema, retention/access, atomic success logs versus failed-attempt events; shared audit owner. |

Source correction to old grouped designs: `_saveasnew` is not disabled merely
by hiding the button. Its POST changes Django's operation to add; add permission
is required, and authorized cloning inserts a fresh row. T22f/T22g and T23f cover
these explicit actions. A forged bulk action excluded by permissions may return
a normal changelist rather than detail-delete's 403; state denial is asserted.
Supplemental read-only framework inspection used the coordinator environment's
`django/contrib/admin/options.py` (changeform_view, _changeform_view,
_get_obj_does_not_exist_redirect, response_add/change, delete_view, history_view)
and `actions.py:delete_selected`. This is not an application execution result;
Wave 2 must verify behavior with the agreed installed framework/settings.

Existing `MISC/tests.py:1–3` remains a scaffold with no business assertions.
Demo tests (S12) assert dashboard access/status and admin blocking, not MISC
fields/filtering/escaping/date instants/admin permissions/failure atomicity.
No coverage number is measured. This agent executed only documentation/source
inspection and document structure/link/count/whitespace validation. Coordinator
owns the shared application baseline; no test, check, installation or network
operation was run here.

## Shared transaction and audit contributions

Merge these domain rows into the coordinator's single registry, not another runner:

| Registry ID | Operations / expected boundary | Design evidence |
| --- | --- | --- |
| MISC-TX-READ | O01–O06/O12: no writes, including failure/default paths. | T01/T02/T06/T07/T16/T17/T30 descendants. |
| MISC-TX-ORM | O07/O08: plain ORM saves, no custom validation/atomic/audit hook. | T03/T04/T05/T29c. |
| MISC-TX-ADMIN-SAVE | O09/O10: row plus stock add/change log under changeform atomic block. | T22/T23; injected failures T27a/T27b. |
| MISC-TX-ADMIN-DELETE | O11: detail delete atomic block; bulk action has separate log/delete steps. | T26; T27c preserves detail rollback, T27d blocks audit semantics. |

Contribute source commit, action/field allowlists, refreshed state deltas,
LogEntry actor/content_type/object/action/time, failure point/database alias,
rollback observations and no-write evidence. Existing custom business audit is
absent; ORM changes do not create admin logs (T29c). Q11 decides broader audit.
T28b names PostgreSQL independent connections/barriers/timeouts as additional
facilities, but remains POLICY_BLOCKED primarily because winner semantics are
undefined. SQLite sequential saves cannot establish concurrency guarantees.
Only T11b is INFRA_BLOCKED with a clear DOM contract and missing browser capture.

AUTHENTICATE owns complete dashboard eligibility/session/login, missing-profile
policy and demo admin boundary; MISC checks the content interface only. HOME owns
public media/navigation/seeding composition and currently has no MISC display.
No test uses the demo executive, member data, secret imports or runtime credentials.

## Ordered Wave 2 checklist

1. Verify inventory, 30-parent mapping, 103 names and statuses with coordinator.
2. Implement ordinary shared business/demo settings, fixture signatures and consumed clocks.
3. Add singular test package/discovery and domain-local assertions from the README layout.
4. Implement READY models/filtering/default/date/escaping and minimal integration adapters.
5. Implement READY narrow admin/CSRF/field/save-flag/delete/history/rollback cases.
6. Resolve Q1–Q11 independently; fix D1/D2 outside this design-only wave.
7. Resolve Q7/Q8 before asserting repaired direct-view or missing-profile transport.
8. Add browser or PostgreSQL cases only after their facilities and policies exist.
9. Run coordinator-approved targeted and app-wide discovery; preserve demo assertions.
10. Record actual pass/fail/blocked evidence in the shared registry and cumulative audit.
