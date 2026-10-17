# MISC Wave 1 regression specification

## Evidence and execution boundary

Inspected branch `prototype/railway`, commit
`7e25ac2f06b2d88a0220526771585f30df10c57a`, checkout
`/workspace/CODEX-SPD-PROTOTYPE`, assigned repository
`Rmorr2001/CODEX_SPD_PROTOTYPE`. Read root `AGENTS.md` and the complete
`docs/testing/wave-1-agent-prompt.md`; no nested MISC guidance was found.
This is proposed design, not executed results or approved policy. Only source
reads, branch/commit identification and documentation review were performed;
application checks/tests are reserved to the coordinator. No secrets, uploads,
private database, network, dependencies or application/Git changes were used.

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
| Active staff, add only / change only / delete only, separately per model | Same dashboard policy | Only corresponding action granted; verify crafted direct URL/POST, not button visibility |
| Staff with announcement permissions only, or DST permissions only | Same dashboard policy | Other model denied; add+change does not grant delete |
| Active superuser (synthetic, non-demo) | Same dashboard policy, including NEW_MEMBER check | Both models allowed; not a substitute for narrow-role tests |
| Reader A and reader B; staff A-created and staff B-created records | Same global active announcements/setting; neither model has owner field | Permissions model-wide, no creator/owner restriction in current implementation |

Demo middleware's 403 is independently preserved by AUTHENTICATE; it cannot
establish C03 model authorization. Do not disable a deployed boundary. Ask the
coordinator for a test-only settings override shared with all C03 suites.

## Case conventions and invariants

Below are **30 named proposed cases**, not completed tests. Each arrow sequence
is setup → action → response → fresh state assertions. Unless explicitly noted,
all cases assert MISC row PKs/fields, users/profiles/roles and sessions unchanged,
no file operations and no business audit writes. Admin mutation cases allow only
the stated row fields plus stock admin LogEntry, automatic updated_at and normal
admin success-message transport (cookie/session according to shared settings); compare
other rows including a second actor/target. Use TestCase/real ORM, SimpleTestCase
for calendar logic, and TransactionTestCase for commit failures. No mock of
selection/filtering/auth/model logic. Patch the clock at `MISC.utils.datetime`
while retaining real constructors, or use a coordinator-controlled clock seam;
patch tag/view imported utility names only for deliberate boundary failures.
Do not assume patching django.utils.timezone.now controls datetime.now(tz).

### C02 models and read behavior

- **MISC-T01 active_selection** — P0/P, O01. Setup reader A/B, two active
  announcements and one inactive, controlled timestamps → each GET dashboard →
  200, context PK set exactly active set, titles/content present exactly once,
  inactive sentinel absent → refresh all rows; exact original fields/timestamps.
  Repeat after ORM deactivate one/activate another; next GET changes membership
  only. Do not require implicit query order; ordering policy Q1.
- **MISC-T02 empty_selection** — P1/P, O01/O04. Empty DB, then inactive-only DB
  → eligible GET → 200, no announcement table/close control/content → no new
  records. Repeat request proves no auto-created defaults or dismissal state.
- **MISC-T03 announcement_model_lifecycle** — P1/P, O07. Synthetic title/content
  → create at t0 → active true, created/updated aware t0 and str=title → update
  content/title at t1 → created unchanged, updated=t1, unrelated inactive row
  unchanged. Save same values t2 → updated advances (not business idempotency).
- **MISC-T04 announcement_validation_boundary** — P1/P+Q, O07/O09. Required blank
  title/content, 255/256-char title → full_clean/form validation → required and
  max-length errors where applicable; boundary 255 succeeds → invalid admin
  requests leave no rows/logs. ORM save does not call full_clean; do not claim
  universal DB rejection across backends. Decision Q5 for future service/API.
- **MISC-T05 dst_model_defaults** — P1/P, O08. Omit active/name, then name=None,
  empty and 255-char variants → create/read/string → active true; nullable/blank
  accepted, str includes active status → change false/name; only those fields
  change, second row unaffected. 256-char form/full_clean fails without write.
- **MISC-T06 tag_default_and_direction** — P0/P, O02. No settings, real computed
  spring date then fall date under controlled clock → call tag → visible true,
  next_change matches aware utility result, precise date and forward/back
  wording → zero settings created, no writes. Empty/null name does not override.
- **MISC-T07 setting_override_and_activation** — P0/P, O02/O05. One active setting
  custom `line1\nline2` → tag/render → override text and newline break; set false
  → show_alert false, no clock/overlay/popup/script in fragment; set true again
  → visible. State changes only explicit fixture saves; GET never toggles DB.
- **MISC-T08 multi_setting_selection** — P1/Q, O02/O08. Create lowest-PK inactive
  A and higher-PK active B in opposite name order → tag → current first-PK A
  controls both message/visibility; edit B no effect; delete A → B takes over;
  delete B → computed visible default. Assert no automatic singleton repair.
  Q2 must approve deterministic selection or replacement singleton before a
  permanent business assertion; retain characterization separately.
- **MISC-T09 announcement_escape_and_dates** — P0/P, O04. Rows containing
  `<script>`, `<img onerror=...>`, quotes and ampersands → render fragment →
  title/content encoded, no executable nodes, updated date rendered; controlled
  created!=updated proves correct date. Supply unsaved context object with
  updated_at=None to exercise created fallback → no writes. Missing/empty context
  yields no table. Check semantic DOM, not full snapshots.
- **MISC-T10 dst_override_escape** — P0/D+Q, O02/O05. Store override containing
  `<img src=x onerror=...>`, `<script>` and newline → render tag → inspected code
  emits raw HTML through safe. Future acceptance: malicious markup inert while
  approved linebreak presentation remains; Q3 chooses plain text vs sanitized
  rich text. Never make executable raw override the passing business contract.
  DB stays original, other rows/session unchanged; no browser/network required.
- **MISC-T11 local_controls** — P2/P, O04/O05. Render eligible fragments → assert
  announcement close targets containing table and DST toggle refers existing
  alert/overlay IDs; no mutation endpoint/form. Optional future browser check
  click open/close/reopen and announcement dismiss → expected DOM state, reload
  restores display, zero network writes/cookies/session dismissal. Backend tests
  assert markup interface only; JavaScript execution requires shared browser
  tooling decision, not a new MISC runner.

### Chicago calendar and deliberate failures

Use UTC instants to distinguish repeated local hours. Candidate spring for 2026
is March 8 02:00 -06:00 (08:00Z; pytz default localizes nonexistent wall time);
physical spring jump is March 8 08:00Z. Candidate fall is November 1 02:00
-06:00 (08:00Z): `is_dst=True` cannot make unambiguous 02:00 daylight time.
Physical fall rollback is November 1 07:00Z (02:00 CDT → 01:00 CST). This
one-hour discrepancy requires a defect decision, not a false timezone guarantee.

- **MISC-T12 spring_strict_future** — P0/P+Q, O03. Clock March 8 2026 at
  07:59:59Z / 08:00:00Z / 08:00:01Z → real utility → before returns spring;
  at/after returns fall candidate because strict `>`; returned values aware,
  compared in UTC, calendar/date/direction correct → zero DB/session/file writes.
  Q4 decides exact-at semantics and spring returned nonexistent wall-time label.
- **MISC-T13 fall_physical_boundary** — P0/D+Q, O03. Clock November 1 2026 at
  06:59:59Z / 07:00:00Z / 07:00:01Z → utility → inspected implementation still
  chooses same-day 08:00Z candidate for all three; desired physical transition
  semantics would choose next spring at/after 07:00Z. Assert aware result and
  capture discrepancy; do not approve incorrect instant. No writes. Block final
  acceptance on Q4 and corrected implementation.
- **MISC-T14 fall_candidate_boundary** — P1/Q, O03. Clock November 1 2026 at
  07:59:59Z / 08:00:00Z / 08:00:01Z → current utility → before returns candidate,
  at/after returns March 14 2027 02:00 -06:00 (08:00Z). Separately label this
  characterization rather than accepting the physical fall error. No writes.
- **MISC-T15 year_rollover_and_calendar** — P1/P, O03. Clock December 31 2026
  23:59:59 Chicago and January 1 2027 00:00:00 Chicago → utility → both next
  March 14 2027; March 7/14 and November 1/7 calendar variants for 2027/2028
  verify second/first Sunday with independently enumerated expected dates,
  not a copied weekday formula. Next-year availability means ordinary clocks
  do not produce None. Check server timezone override cannot alter Chicago
  results for the same instant; no mutation.
- **MISC-T16 utility_failure_and_fallback** — P0/D+Q, O02/O03/O06. Inject utility
  return None at tag/view boundary → tag returns visible fallback message,
  next_change=None; view prepares its distinct fallback. Then inject timezone
  lookup error, clock error, DB OperationalError during setting read and
  utility exception → current uncaught exceptions propagate before render
  (even inactive setting still calls utility). No writes/partial defaults.
  Q6 chooses fallback/logging vs error response; do not normalize outage crashes
  as approved behavior. The tag DoesNotExist handler may be exercised by
  deliberate injection only: `.first()` normally returns None, never that error.
- **MISC-T17 unused_view_and_routes** — P1/D+Q, O06/O12. Inspect resolver under
  actual core/demo root → no MISC include/name and no invented public route.
  Direct RequestFactory calls with GET/POST and spring/fall/None utility values
  → context wording/always-visible differs from tag; actual render attempts
  `dls_alert.html`, absent from inspected template inventory. Capture
  TemplateDoesNotExist as defect if confirmed in isolated settings. No DB
  changes and no per-user settings applied. Q7 retire or namespaced repair/
  mount with explicit authentication; never invent intended HTTP contract.

### Cross-domain interfaces only

- **MISC-T18 eligible_actor_matrix** — P0/P, O01/O12. Minimal users for each
  eligible role row in matrix plus reader B → GET dashboard → 200 and same
  active PK set; no owner filtering, unrelated rows unchanged. AUTHENTICATE
  owns complete login/session/role route behavior; MISC checks fragment contract.
- **MISC-T19 redirected_actor_matrix** — P0/P, O12. Anonymous and each NEW_MEMBER
  combination → GET mounted dashboard → login redirect or literal `/newmember/`
  respectively; no announcement content or tag output; rows/session unchanged
  except normal auth fixture login. This is ANY presence of one role, not ALL
  combinations or staff privilege override. AUTHENTICATE owns redirect details.
- **MISC-T20 missing_profile_and_home** — P1/D+Q/P, O12. Authenticated user
  without Brother_Profile → dashboard currently raises related-object error
  through S10; Q8 requires handling policy, no passing crash contract. Separately
  anonymous/eligible GET `/` with active announcements and DST setting → HOME
  has neither MISC table nor clock; its unused import does not make integration.
  Both paths leave MISC records untouched. HOME owns page/media/nav assertions.

### C03 admin, permissions and transactions

Admin cases run for **each model separately** with reversed real URLs in shared
isolated admin-enabled settings. Minimal staff users A/B have exactly named
`MISC.view_*`, `add_*`, `change_*`, `delete_*` permissions; use fresh clients after
permission changes to avoid permission caching. Stock admin behavior is inferred
from ModelAdmin registration and must be runtime-verified in Wave 2.

- **MISC-T21 admin_permission_matrix** — P0/P, O09/O10/O11. Each actor/permission
  row above, both own-created and other-created PKs → direct list/add/change/
  delete GET plus crafted valid POST (and delete_selected) → nonstaff/inactive
  cannot enter, staff lacking action permission gets 403; view-only reads but
  cannot write; respective permissions allow only granted model/action. Assert
  no target/other row/log mutation on denial. Superuser smoke once, never as
  coverage for narrow grants. No ownership field means no owner bypass to test.
- **MISC-T22 admin_announcement_create_edit** — P0/P+Q, O09/O07. Authorized staff,
  t0/t1, second existing inactive record → GET form/list → only title/content
  editable; list title/created_at; valid add then edit POST → 302, fresh row
  values/default true/timestamps correct, logs correct actor/object/action,
  unrelated row unchanged. Craft is_active=false/id/created_at/updated_at
  extras on edit → excluded fields ignored, existing active flag/created/id
  unchanged, updated autochanges; inactive row edit stays inactive. Q9 governs
  missing activation UI; do not claim admins can deactivate announcements.
  Parameterize `_save`, `_continue`, `_addanother` and forged `_saveasnew`
  (save_as is not enabled): assert standard authorized redirect destinations
  and exactly intended insert/update count; no hidden privilege or duplicate edit.
- **MISC-T23 admin_dst_create_edit** — P0/P, O10/O08. Authorized staff and second
  setting → valid add/edit POST → 302, only selected is_active/name persisted,
  string/list label consistent, correct add/change log; omitted checkbox false,
  omitted/empty name accepted (form normalization verified at runtime), whitespace
  name follows Django form stripping. Repeated identical POST does not create
  duplicate row on change but may create another change log; unrelated row stable.
  Exercise the same save/continue/add-another flags as T22 for DST fields.
- **MISC-T24 admin_invalid_and_missing** — P1/P, O09/O10/O11. Authorized staff →
  missing required announcement fields, 256-char title/name, invalid PK URL,
  nonexistent numeric PK, stale deleted PK update/delete, unknown action and
  empty bulk selection → form errors or framework not-found/redirect behavior
  verified per endpoint; never mutate a different object or create accidental
  replacement. Assert no success log for invalid writes, other rows untouched.
  Pin legacy status only after actual isolated observation, not incidental crash.
- **MISC-T25 admin_csrf** — P0/P, O09/O10/O11. `Client(enforce_csrf_checks=True)`
  authenticated authorized staff → add/change/delete/bulk POST without/invalid
  token → 403, rows and logs unchanged; GET form valid cookie/token → identical
  valid-token POST succeeds with only intended mutation/log. GET delete
  confirmation and bulk first-stage confirmation never delete rows. Repeat
  under public-demo boundary through AUTHENTICATE-owned interface: 403 regardless
  of permission; no production middleware edits.
- **MISC-T26 admin_delete_detail_bulk** — P0/P+Q, O11. Two selected and one
  unselected row per model → detail confirmation then POST yes → target absent,
  log records correct user/representation/action; bulk initial action POST →
  confirmation only, confirmed delete_selected → exactly selected absent and
  per-object logs, other model/row intact. Repeated stale deletion changes
  nothing. Deleting selected first DST setting exposes next/default per T08;
  no files/cascaded business rows exist. Q2/Q9 for last-row visibility policy.
- **MISC-T27 admin_atomic_failure** — P0/P verification+D/Q, O09/O10/O11. In
  TransactionTestCase with real DB and deliberate exception at admin log/write
  boundary after model mutation → POST add/change/detail delete → expected
  exception or safe error per shared handler; verify framework atomic request
  blocks leave complete original rows and no partial success LogEntry. Repeat
  model save/delete failure. For bulk action, separately inject failure after
  logging but before queryset deletion: inspect actual log/row state, because
  an action may lack the encompassing changeform/delete-view transaction. Any
  surviving success log or partial deletion is D/Q11 for atomicity policy, never
  an approved success contract. Verify selected DB alias and transaction scopes;
  do not claim custom MISC transaction support or storage compensation. Commit
  callbacks/external file operations are absent.
- **MISC-T28 concurrent_admin_edits** — P1/Q, O09/O10. Two authorized independent
  users load same target; A saves then stale B saves → characterize last writer
  fields, unchanged PK/other rows and both logs. Q10 decides optimistic conflict
  handling for migration; no approved version/locking guarantee today. Any true
  simultaneous race requires independent PostgreSQL connections and bounded
  synchronization in shared harness; SQLite sequential saves prove no race.
- **MISC-T29 audit_history_boundary** — P1/P+Q, O09/O10/O11. Staff A mutates one
  object, staff B another → admin history with view/change permissions → correct
  permitted object's add/change history actor/time/content, no wrong-object logs;
  unauthorized history access denied. Plain ORM fixture edits and reader GETs
  do not create admin LogEntry. Q11 defines future cumulative business audit,
  distinct from stock admin logs; no assertion claims broader logging exists.
- **MISC-T30 read_failure_isolation** — P1/D+Q, O01/O02/O12. Inject DB failure at
  lazy announcement evaluation or setting lookup during dashboard rendering →
  current request fails rather than partial success guarantee; other domain rows,
  sessions and MISC fields unchanged. Repeat after recovery → correct content,
  no cached failure/default persisted. Q6 chooses graceful fragment isolation;
  no test mocks queryset filtering itself or calls real external services.

## Completeness, transaction registry and cumulative audit contribution

| Operation | Named cases |
| --- | --- |
| O01 | T01,T02,T18,T30 |
| O02 | T06,T07,T08,T10,T16,T30 |
| O03 | T12,T13,T14,T15,T16 |
| O04 | T02,T09,T11 |
| O05 | T07,T10,T11 |
| O06 | T16,T17 |
| O07 | T03,T04,T22 |
| O08 | T05,T08,T23 |
| O09 | T04,T21,T22,T24,T25,T27,T28,T29 |
| O10 | T21,T23,T24,T25,T27,T28,T29 |
| O11 | T21,T24,T25,T26,T27,T29 |
| O12 | T17,T18,T19,T20,T30 |

Domain registry rows to merge into the coordinator's single shared transaction
registry (not another runner): `MISC-TX-READ` O01-O06/O12 no writes; `MISC-TX-ORM`
O07/O08 plain ORM save/delete with no explicit domain atomic grouping or audit;
`MISC-TX-ADMIN-SAVE` O09/O10 row plus standard LogEntry; `MISC-TX-ADMIN-DELETE`
O11 selected rows plus logs. Registry columns should record action ID, touched
models/fields, boundary and database alias, injected failure point, expected
rollback, non-DB effect (none here), evidence/case ID and observed backend.
T27 supplies candidate atomicity proof only after execution; T28 is a policy/race
entry, not an established concurrency guarantee.

For the cumulative audit, contribute operation/case IDs, source commit, changed
field allowlists, denied/read no-write evidence, fresh-state diffs, LogEntry
actor/object/action/timestamp checks and failure rollback results. No MISC custom
audit exists; record that gap, not a fabricated business event. Never put content
from real announcements, private accounts or credentials into reports. Shared
runner should aggregate defects/decisions and actual outcomes once, keeping
proposed, implemented, passed and blocked counts distinct.

Existing assertions: MISC scaffold contains none. Demo tests assert eligible
executive 200, anonymous/new-member redirect and `/admin/` block (S12), but no
active/inactive selection, timestamp/string, field exposure, permission model,
escaping, DST/failure/atomicity or other-row invariants. No measured coverage.
No application command was executed by this agent; coordinator baseline is the
only shared execution result and must be linked after it is available.

## Shared interfaces, decisions and Wave 2 order

Use the layout in README. `assertions.py` should assert business membership,
visibility, dates, allowed state deltas and audit identities independently of
legacy redirects/HTML. Legacy `test_rendering.py`/`test_admin.py` adapters own
status, template/context, escaped DOM and Django ModelAdmin form assertions.
No private copy of shared factories, test settings, transaction registry, CI or
browser harness. Proposed shared interfaces are
`make_user(roles=(), with_profile=True, **fields)`, `make_profile(user, **fields)`,
aware controlled clock and isolated database; amend with explicit staff/active
flags and per-model Django permission grants. No media fixture is needed here.

| Question | Blocking decision / owner |
| --- | --- |
| Q1 | Announcement ordering absent explicit Meta/order_by; product/coordinator choose whether chronological ordering is required. |
| Q2 | First-PK DST settings vs singleton, and deleting last row re-enabling alert; product/coordinator. |
| Q3 | Trusted HTML vs escaped plain text/sanitized rich text for override; stored executable HTML is a defect; product/security owner. |
| Q4 | Exact transition semantics, physical fall instant, nonexistent spring label and current-vs-future strictness; product/coordinator. |
| Q5 | Model full_clean vs service validation for future callers; title/content limits and blank policy; migration owner. |
| Q6 | Clock/database/utility failures: fragment unavailable vs whole-page failure and expected error logging; cross-domain owner. |
| Q7 | Retire or repair unused view, and whether any authenticated/public endpoint is wanted; coordinator. |
| Q8 | Missing-profile dashboard behavior; AUTHENTICATE owns response/fix, MISC consumes safe rendering interface. |
| Q9 | Announcement activation editing and delete/deactivate policy; current admin omits active/timestamps; product/admin owner. |
| Q10 | Last writer wins vs conflict/version control for concurrent admin edits; migration owner. |
| Q11 | Required cumulative business audit beyond stock admin LogEntry, retention and failure semantics; shared audit owner. |

Dependencies sent to coordinator: AUTHENTICATE owns dashboard eligibility/redirects,
missing-profile behavior and demo admin blocking; MISC owns fragment contract
assertions only. HOME owns public composition; no MISC home display is currently
implemented. Shared C03 test settings must expose real admin without production
changes. Coordinate controlled clock, narrow permission fixtures and cumulative
registry/audit schema before implementation; no tests rely on demo executive or
seed contents. Pseudocode Q/D cases may become acceptance tests only after the
specific decision/fix is approved, not silently converted into expected failures.

1. Coordinator verifies this commit/source inventory and reconciles 12 operations,
   30 case IDs, cross-domain ownership and shared baseline results.
2. Resolve P0 Q3/Q4/Q6/Q8; record behavior changes separately from preserved
   contracts. Decide Q2/Q9 before freezing admin/default selection expectations.
3. Agree shared test settings/fixtures/clock, admin CSRF setup and audit registry;
   create singular `test/__init__.py` only in Wave 2 and verify discovery.
4. Implement model/calendar/selection business assertions, including physical
   transition discrepancies; keep characterization and accepted contracts separate.
5. Add fragment escaping and minimal AUTHENTICATE/HOME interface assertions;
   avoid duplicating their full route/login/seed/media suites.
6. Implement narrow C03 admin action matrix, malicious/excluded fields, invalid
   requests, CSRF, delete detail/bulk and fresh-state/audit assertions.
7. Add deliberate failure/transaction tests; PostgreSQL races only if applicable
   and shared harness exists. Confirm no hidden writes on read/error/denial.
8. Run coordinator-approved targeted/discovery commands, review actual results
   and migration adapters, then merge evidence into the single cumulative audit.
