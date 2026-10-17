# PARLEYPRO Wave 1 regression specification

Status: source-inspected proposal, awaiting coordinator verification; no executable tests or application-test results. Checkout `/workspace/CODEX-SPD-PROTOTYPE`, repository `Rmorr2001/CODEX_SPD_PROTOTYPE`, actual branch `prototype/railway`, actual HEAD `7e25ac2f06b2d88a0220526771585f30df10c57a`.

## Evidence and boundaries

All citations below are repository-relative and refer to that inspected commit. Prefix `P/` means `SPDWEBAPP/PARLEYPRO/`; `A/` means `SPDWEBAPP/AUTHENTICATE/`. Root `AGENTS.md` and `docs/testing/wave-1-agent-prompt.md` were read; no nested AGENTS.md was found. No credentials, environment values, real uploads or member data were read. No network, dependency installation, Git mutation or application tests were performed.

- `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:23-34` mounts `/poll/` and configured admin prefix. `P/urls.py:4-13` mounts all four view functions; the identical live-results path/name is defined twice at lines 8 and 11. First match handles inbound requests; the redundant entry is not a second operation.
- `P/views.py:15-34` selects newest open poll before POST dispatch, counts all choices after dispatch, and renders without PRG; `:35-50` creates; `:51-58` lists closed polls; `:61-68` serves login-only JSON.
- `P/pp_functions.py:11-14` counts literal choices; `:16-41` selects newest open poll, checks EXEC ineffectively, saves aggregates/end, then globally resets; `:45-72` dispatches by key presence, ignoring values. No transaction, lock, poll relation or eligibility check is present in these helpers.
- `P/pp_decorators.py:7-52` is a **public cross-domain dependency**. ALL roles are required (`:35-36`); anonymous gets message and named login redirect (`:21-23`); missing roles/profile redirect to raw Referer or `poll` (`:26-48`). Imported by AUTHENTICATE, PHILANTHROPY and HOME as well as this domain. Shared callable contract tests belong to [AUTHENTICATE](../../AUTHENTICATE/test/regression-spec.md), as reconciled by the coordinator; PARLEYPRO owns route-specific access assertions and documents these dependencies without duplicating their harness.
- `P/models.py:12-24`: `Vote_Poll` has nullable name/counts/end, required creator FK with CASCADE, start `auto_now_add`, no model hooks; `Brother_votes` has nullable OneToOne user and nullable choice, no poll FK. There are no historical individual ballots. `P/migrations/0005_vote_poll.py:16-25` agrees on poll schema. `A/models.py:58-79,88-95` supplies unique role names and optional one-to-one user profile plus roles M2M.
- `P/forms.py:5-14`: only `Vote_Poll_Name` is exposed; required because model `blank=False`, max 200, standard form stripping. `P/admin.py:8-35` registers only Vote_Poll, default ModelAdmin CRUD, result icon and sorting by raw Yes count. Brother_votes is not registered here. No custom admin save/action hooks enforce close/reset policy.
- `P/templates/create_poll.html:11-24` posts name with CSRF; `poll_index.html:22-42` posts aye/nay/end_vote only when open poll appears, without EXEC button protection. The start link is navigation (`:9-10`), **not** a `start_vote` form key. Hidden manual requests remain reachable. `poll_index.html:85-108,114-155` stores preference in browser localStorage and polls JSON every 1500ms; bars may not exist when zero initial votes/no poll. `past_polls.html:14-54` shows creator/start/end, count bars or no-votes, Chicago display time. Templates escape normal name/creator output.
- `P/tests.py:1-3` is empty scaffolding. `SPDWEBAPP/railway_demo/tests.py:58-67` checks executive GET 200 for four polling routes/current name; `:99-104` checks ACTIVE Aye response/row; `:31-40` checks seeded poll count. Those are existing assertions inspected, not executed here.
- `SPDWEBAPP/SPDWEBAPP_CORE/settings.py:95-100,126-131` includes CSRF/auth/messages middleware and SQLite DB; `SPDWEBAPP/railway_demo/settings.py:24,28-32` uses demo SQLite, boundary middleware and login URL. No `ATOMIC_REQUESTS` occurrence was found in these settings. `SPDWEBAPP/railway_demo/middleware.py:9-12` blocks `/admin/` with JSON 403; `railway_demo/urls.py:4` includes core URLs. Do not mistake that outer block for a domain admin permission test.

No unused/unmounted PARLEYPRO views were found. The commented logout routes and old model comments are not supported operations. The dispatcher start branch is callable via forged POST but its redirect return is discarded; it is unused by the current UI. No PARLEYPRO session mutation except messages, file write, upload, export or audit model exists. Browser localStorage is not a server session contract.

## Classification and invariant vocabulary

**P = preserve** supported non-harmful business behavior; legacy response assertions stay separate from business assertions. **D = defect** observed insecure, lossy or crash-prone implementation; design a safe regression target after an authorized fix, never a passing assertion that the defect is correct. **Q = decision needed** ambiguous policy; characterization may document current mechanics but cannot approve policy. A case can contain P/D/Q variants explicitly. P0 security/data integrity; P1 core flow; P2 presentation/compatibility.

Every case below uses synthetic users A and B, snapshots affected tables, then refreshes rows after action. Unless explicitly affected, preserve other users' choices, all poll names/creators/start times, historical counts/end times, profile/role rows, user attributes and row counts. A denied/invalid read or write must not mutate polls/votes. Message storage may change on denial; do not assert session byte equality. No file/audit effects should appear. Fault injection is at the named persistence boundary only; real ORM counting and business functions still run. No proposed D/Q case counts as completed passing coverage or an unexplained skip/xfail.

Base fixtures: `make_user(roles=(), with_profile=True, **fields)` and `make_profile(user, **fields)` are shared proposals owned by the coordinator/AUTHENTICATE; avoid images. Domain-local `open_poll(creator, start)`, `closed_poll(creator, start, end, yes, no)` and `current_choice(user, choice)` are proposed thin ORM factories, not new schema. Since start is auto-generated, set deterministic older starts via a controlled clock at creation or an explicit test-only queryset update. Freeze aware UTC time T (including Django model clock as well as view/helper clock); use unique T offsets and separate same-time cases. Snapshot includes PKs to detect replacement rows. Use `assert_poll_snapshot`, `assert_current_choices` as business assertions, and separate helpers for redirect/status/template/JSON compatibility.

## Verified operation inventory (14 operations)

| Stable ID / wave slice | Route or callable, actor and input | Observed response and effects; classification |
| --- | --- | --- |
| PP-V01-FORM / V01 | GET `/poll/start_vote/`, EXEC+ACTIVE | 200 create template and unbound form, no writes; `views:35-50`, P |
| PP-V01-CREATE / V01 | POST same, EXEC+ACTIVE, name | Valid: new creator=request.user, start via auto_now_add, zero counts/open, 302 named poll; invalid 200 bound errors/no writes. No check for existing open poll; `views:38-45`, `forms:5-14`, P/Q |
| PP-V02-DISPATCH / V02 | POST `/poll/`, ACTIVE, key presence | `start_vote` wins and ignores returned redirect; else end_vote wins; else get/create own choice, Nay then Aye; unknown POST can create No Vote. Always page render after helper; `functions:45-72`, D/Q |
| PP-V02-CAST / V02 | Dispatcher else branch, ACTIVE, aye/nay, optional forged fields | Current actor's global choice created/changed, no poll needed; no new historical ballot; `functions:60-71`, P/Q |
| PP-V02-COUNT / V02,V03,V04 | `count_all_current_votes(queryset/manager)` | `(aye,nay)` counts exact strings, no writes; includes all users regardless role/poll; `functions:11-14`, P/Q |
| PP-V03-CLOSE / V03 | end_vote POST/helper, intended EXEC+ACTIVE; no poll ID | Newest open poll gets counts/end then every current choice reset. ACTIVE without EXEC also closes (D). No-open no writes; nonatomic two-step write; `functions:16-41`, P/D/Q |
| PP-V04-PAGE / V04 | GET `/poll/`, ACTIVE | 200 newest open poll or none, global live counts; POST reuses pre-dispatch poll object; `views:15-34`, P/D/Q |
| PP-V04-HISTORY / V04 | GET `/poll/past_polls/`, ACTIVE | 200 closed polls ordered descending end, all creators; no individual ballots; `views:51-58`, P/Q equal-time ordering |
| PP-V04-LIVE / V04 | `/poll/poll-results/`, authenticated any roles/profile | JSON integer aye_votes/nay_votes, independent of open poll; login redirect anonymous; `views:61-68`, P/Q audience |
| PP-V04-ROUTES / V04 | resolver/reverse, clients using supported paths | Four view functions mounted, duplicate live path resolves same callable; no method guards other than creation/dispatch checking POST; `urls:4-13`, P/D/Q |
| PP-C03-READ / C03 | Django poll changelist/detail, authorized staff model permissions | Default ModelAdmin access, configured fields/list columns; demo outer block separate; `admin:8-18`, P |
| PP-C03-WRITE / C03 | Admin add/change/delete/bulk delete, staff + corresponding perms | Default CRUD can alter creator/end/counts, delete polls, without global reset; no custom hooks; `admin:8-35`, `models:12-18`, P/Q retention and invariants |
| PP-C03-ICON / C03 | `VotePollAdmin.poll_result_icon(obj)` | Passed green / Failed red / Tied gold, ordering metadata Yes count; NULL comparisons crash; `admin:20-35`, P/D |
| PP-SHARED-ROLE / shared dependency | public `requires_role(*names)` wrapping consumers | ALL semantics, profile/anonymous messages and redirects; no superuser bypass; raw Referer defect and fallback self-loop risk; `pp_decorators:7-52`. Shared contract implementation owned by AUTHENTICATE; route integration owned here, P/D |

## Actor and ownership matrix

`allow` assumes valid CSRF for unsafe methods. `deny` describes access boundary, never a permission to mutate. Extra unrelated roles must not remove granted access.

| Actor | Page / cast / history | Create GET+POST | Live JSON | Close desired / observed | Admin |
| --- | --- | --- | --- | --- | --- |
| Anonymous | deny via decorator, named login + message | login_required first; login with next | login with next | deny / denied at page boundary | login boundary or demo 403 |
| Authenticated, no profile | deny profile message | deny profile message | allow | deny / denied at page boundary | Django staff/perms independent of profile |
| Profile, roles empty; ALUMNI only; NEW_MEMBER only; PHIL_CHAIR only | deny | deny | allow | deny / denied at boundary | same |
| EXEC only | deny (ACTIVE missing) | deny (ACTIVE missing) | allow | deny / boundary denies | EXEC does not imply staff/perms |
| ACTIVE only | allow | deny (EXEC missing) | allow | **deny / currently closes, P0 defect** | ACTIVE does not imply staff/perms |
| EXEC+ACTIVE | allow | allow | allow | allow regardless creator | no inherent admin grant |
| ACTIVE+ALUMNI; EXEC+unrelated role | ACTIVE row / EXEC row above | same ALL rule | allow | same | no inherent grant |
| Superuser lacking profile/roles | deny public routes except live | deny | allow | deny | normal Django superuser access in isolated admin setting |
| Staff with specific view/add/change/delete poll perms | role rules still apply | role rules still apply | allow | role rules still apply | only corresponding admin actions; demo boundary still denies |

Ownership: casts always address `request.user` OneToOne choice, ignoring forged user/poll/choice fields. Another creator's poll can be viewed, counted or closed by properly authorized actors; there is no creator-only guard in source. Confirm chapter-wide close policy rather than inventing ownership. Creating cannot spoof creator/start/end/counts through the form. No row ID route exposes individual historical choices. Helper callables themselves do not enforce all request permissions: direct close with EXEC-only profile can mutate, while missing profile raises; document domain-service authorization requirement during migration rather than treating helpers as trusted public APIs.

## Named cases (40 design cases)

Each entry specifies priority, classification, operation mapping, minimal fixtures and setup → action → response → fresh state assertions. Braced variants are distinct assertions within that named case, not unspecified exploratory tests. Dependencies `POL-*` and `DEF-*` refer to the registers below. Read-only cases assert the global unchanged-state rule above. `TestCase` is default unless stated.

**PP-01 creation form** — P1 P; PP-V01-FORM. Setup A=EXEC+ACTIVE, no polls → GET create → 200 `create_poll.html`, unbound form with only name and CSRF field, label/widget present → no rows changed. Assert escaped form redisplay for a name containing `<` on an invalid boundary submission, without whole-page snapshots.

**PP-02 valid create/actor/time** — P1 P; PP-V01-CREATE. A=EXEC+ACTIVE and B with a historic poll/choice; freeze T → POST name `  Motion A  ` plus forged created_by=B, counts=99, start/end and arbitrary ID → 302 reverse('poll') → exactly one new open poll with stripped name, A creator, start T, counts 0/0, end NULL; B's poll/choice and all existing votes unchanged. `auto_now_add` overwrites the view assignment, so control both clock uses; do not prove exact timestamp by mocking only `views.timezone.now`.

**PP-03 form validation/boundaries** — P1 P; PP-V01-CREATE. A allowed → separately POST missing name, empty, whitespace-only, 201-character name → 200 bound required/max-length errors, zero creates → all snapshots unchanged. Separately POST 1 and 200 characters and ordinary Unicode → each valid trimmed value persists once with correct actor. Malicious HTML is stored as text/escaped on reads; no custom sanitization is claimed.

**PP-04 create access ALL** — P0 P; PP-V01-FORM/CREATE, PP-SHARED-ROLE. For anonymous, missing-profile, empty roles, EXEC-only, ACTIVE-only, unrelated-only and EXEC+unrelated, separately GET and valid POST → denial redirect; anonymous login_required includes next, authenticated denial messages name missing roles/profile → no create/reset. EXEC+ACTIVE and that pair+unrelated pass. Superuser without profile must not bypass the public role boundary. Use safe same-origin Referer or no Referer; shared exact message contract depends on AUTHENTICATE.

**PP-05 CSRF action boundary** — P0 P; PP-V01-CREATE, PP-V02-DISPATCH/CAST, PP-V03-CLOSE, PP-V04-LIVE. A allowed, B existing choice/open poll; client with enforce_csrf_checks=True → POST create/cast/end_vote with missing token then bad token → 403 before writes; obtain real cookie+hidden token via GET and submit valid pair → intended success/state for each (reset fixtures between variants). POST live also goes through CSRF despite being read-only; GET live needs no token. Do not infer safety from ordinary Django client POST.

**PP-06 duplicate/replayed create** — P1 Q; PP-V01-CREATE. A allowed and one open poll with existing choices → submit valid create twice/retry same name → observed two additional open rows, old polls/choices untouched, each creator A and new start; 302 each. POL-01 must decide single-open/idempotency before this becomes approved migration behavior; no uniqueness or vote reset should be invented.

**PP-07 cast/change/repeat** — P1 P; PP-V02-CAST/DISPATCH. A ACTIVE, B Nay, open poll P → POST aye (also with empty/false-looking value) → 200 page, create one A choice Aye, B unchanged; repeat → same PK/count; POST nay → same PK now Nay; repeat → same PK. Separate fresh A starts Nay then switches Aye. Poll aggregates/end remain unmodified until close. Choice is driven by key presence, not value text.

**PP-08 actor targeting** — P0 P; PP-V02-CAST. A ACTIVE, B Aye with different creator poll → POST nay plus user/user_id=B, poll ID, user_vote_choice=Aye → 200 → only A's choice becomes Nay, B's PK/value unchanged; no poll/role fields change. Repeat with A's existing row. This ownership assertion is reusable independently of legacy 200 rendering.

**PP-09 both choice keys** — P1 Q; PP-V02-CAST/DISPATCH. A ACTIVE with no choice; open poll → POST both aye+nay (reverse input insertion order too) → observed 200 and final Aye (two save calls Nay then Aye), one row; other users/polls unchanged. POL-02 must select reject versus deterministic priority; do not silently approve Aye dominance.

**PP-10 unknown/empty payload** — P1 Q; PP-V02-DISPATCH. A ACTIVE, open poll → empty POST, unknown key, or only user_vote_choice=`Aye` → observed 200 and new No Vote row for fresh A, not supplied choice. For existing A=Nay → choice/PK unchanged. Missing aye/nay does not mean malformed by current dispatcher; POL-02 decides side-effect-free rejection/no-op. Check no other row changes.

**PP-11 hidden start action** — P1 D; PP-V02-DISPATCH. A ACTIVE, open poll, no own row → POST start_vote alone, then start_vote+end_vote+aye+nay → observed 200 current page, no Location, no creation/cast/reset/closure because redirect is discarded and branch wins. DEF-02: safe target either remove/reject obsolete action or return authorized create navigation (POL-02); ACTIVE must never gain create permission through this branch.

**PP-12 end action precedence** — P1 P/Q; PP-V02-DISPATCH, PP-V03-CLOSE. A EXEC+ACTIVE with existing Nay and B Aye, P open → POST end_vote+aye+nay → observed close aggregates 1/1, reset existing choices, no cast and no new choice if A previously absent. POL-02 decides whether mixed action keys should instead reject without changes; this observed priority is not authorization.

**PP-13 cast without open poll** — P1 Q; PP-V02-CAST/PAGE. A ACTIVE, no open polls (variants none/only closed), B choice → POST aye → observed 200 no-active template, A's global choice stored, closed history unchanged; live count includes it. POL-01 must decide rejecting such casts/clearing orphan choices; UI-hidden buttons provide no protection.

**PP-14 multiple opens and ties in start time** — P1 Q; PP-V02-CAST, PP-V04-PAGE. A ACTIVE, P1 start T-2, P2 start T-1, B choice → GET then cast Nay → newest P2 shown, one global A choice written, no poll FK or individual-poll allocation. With equal starts, do not assert a chosen PK: source provides no tiebreak. POL-01 defines admissible number of open polls and deterministic selection.

**PP-15 count helper literals/scope** — P1 P/Q; PP-V02-COUNT, PP-V04-LIVE. Seed Aye/Nay/No Vote/NULL/invalid raw string with synthetic users of different roles; include nullable-user row (model permits orphan rows) → call real helper with manager then a filtered queryset → assert exact `(aye,nay)` tuple for each supplied scope, nonchoices excluded, no writes; live endpoint uses global scope. Null/invalid rows are ORM corruption fixtures, not valid form inputs; POL-03 determines eligibility filtering for future behavior.

**PP-16 authorized close aggregate/reset** — P0 P; PP-V03-CLOSE, PP-V02-COUNT. A EXEC+ACTIVE, P by B open, historical H, choices Aye=2/Nay=1/No Vote=1 plus corrupt/null row → freeze T, POST end_vote → 200 legacy page → P end=T, counts 2/1, creator/name/start unchanged; every existing choice becomes No Vote preserving PK/user (even corrupt/null); H unchanged, no new choice. Assert result history and live zero afterward. Cross-creator close remains pending ownership confirmation POL-04, but never require actor to own each vote.

**PP-17 unauthorized close regression target** — P0 D; PP-V03-CLOSE, PP-SHARED-ROLE. A ACTIVE-only, P by B, choices and history → POST end_vote with valid CSRF → desired denied response with error and **no poll or choice changes**. Current helper emits error then closes/resets, so this safe target is expected to fail until DEF-01 fixed. Anonymous, EXEC-only, no-role, no-profile and unrelated-role variants are denied before helper and must also leave state unchanged. Direct-helper variant with EXEC-only or missing profile must not become an endorsed service bypass: enforce/define callable boundary in Wave 2 (POL-04).

**PP-18 no-open/repeated close** — P1 P; PP-V03-CLOSE. A allowed, zero open polls and nonzero residual choices, closed H → end_vote → 200, no reset or H overwrite; then fresh P close at T, repeat at T+1 with no opens → original stored counts/end unchanged and no extra poll/choice rows. Do not confuse this no-op with exactly-once behavior when multiple opens exist.

**PP-19 repeated close with multiple opens** — P0 Q; PP-V03-CLOSE. A allowed; P1 older, P2 newer; Aye/Nay choices → first close stores global counts on P2/reset, leaves P1 open; second close closes P1 with zeros; H unaffected. Document observed mechanics, then POL-01 must decide safe repeat semantics/target IDs. Equal-start newest selection is unspecified. Never present reassignment/data loss across simultaneous polls as an approved guarantee.

**PP-20 tie/zero close** — P1 P; PP-V03-CLOSE, PP-C03-ICON. A allowed, one open P, variants 1 Aye+1 Nay; no choices; all No Vote → close → end set at T, counts 1/1 or 0/0 respectively, choices reset; history shows no-votes for zero and numeric bars for tie, admin icon says Tied for both. Business pass/fail threshold or tie resolution is POL-05, not inferred from icon.

**PP-21 failure before poll persistence** — P0 D/Q; PP-V03-CLOSE. `TransactionTestCase`, A allowed, P open, choices → inject error at count query separately and at target poll save before DB write, invoke endpoint with client exception capture disabled or assert propagated exception → current unhandled error/500, P remains open with old counts, choices unchanged; no reset call persisted. Test real failure boundary without mocking counts themselves. Desired translated error contract POL-06. No passing contract that an incidental 500 is acceptable.

**PP-22 failure after save/before reset** — P0 D; PP-V03-CLOSE. `TransactionTestCase`, real autocommit, A allowed/P open, nonzero choices → let actual poll.save commit; inject reset queryset.update failure before update → current error and closed/count-saved P with old choices still present (record diagnostic state). Safe regression target DEF-03 is all-or-nothing closure/reset or approved recovery contract POL-06; after fix require rollback or documented recovery, not persistence of the partial state. Include a subsequent retry: current no-open branch cannot repair leftover choices; assert against approved repair policy, not invented compensation.

**PP-23 partial dual-choice save** — P1 D/Q; PP-V02-CAST/DISPATCH. `TransactionTestCase`, A existing No Vote, open P → both keys, real first Nay save succeeds, inject failure on second Aye save before write → current unhandled error leaves Nay, B/P unchanged. For fresh A, initial get_or_create may also persist No Vote before a first-save failure; inspect that variant with real creation. POL-02/06 select reject/atomic handling; no silent rollback guarantee. Avoid wrapping this characterization in TestCase's outer transaction as evidence of production atomicity.

**PP-24 vote/close race** — P0 D/Q; PP-V02-CAST, PP-V03-CLOSE. Real PostgreSQL `TransactionTestCase`, two worker threads with separate Django connections/clients (A ACTIVE caster, B EXEC+ACTIVE closer), bounded events/timeouts and joined workers; clean connections in finally. P open, baseline A No Vote. Run schedules (a) cast commits before count; (b) closer reads counts, cast commits before reset; (c) reset commits then cast arrives; also cast between Nay and Aye count queries. Instrument barriers around queries/writes without replacing ORM/business logic. Assert responses do not deadlock, counts/choices match approved linearization and no accepted vote disappears without an approved inclusion/rejection rule. Current (b) can reset an uncounted cast, (c) permits residual choice; separate count queries can observe different instants. POL-01/06 must define acceptance boundary before writing final oracle. SQLite cannot verify locking/isolation.

**PP-25 close/close race** — P0 D/Q; PP-V03-CLOSE. PostgreSQL independent connections/clients, two allowed actors and one open P with nonzero choices → bounded barriers so both select P before either save; vary second count before/after first reset, then save order → fresh P/history/choice snapshots and responses. Safe target: closed counts/end immutable under repeated concurrent close, exactly one approved effective transition, no later zero overwrite; response loser policy POL-06. Current stale selected object can overwrite first totals/time. Add two-open variant only after POL-01 defines identity; use timeouts and propagate worker exceptions, never rely on sleeps or SQLite passing.

**PP-26 current page/read presentation** — P1 P; PP-V04-PAGE. A ACTIVE, B creator, old closed H and one open P, Aye/Nay rows → GET 200 `poll_index.html`, context P and exact global counts; creator is not an ownership gate, escaped name and expected formatted Chicago time; no end/history writes. With no open poll → no-active message while context counts can remain nonzero; existing choices unchanged. Avoid HTML snapshots.

**PP-27 history ordering/empty/boundary** — P1 P/Q; PP-V04-HISTORY. A ACTIVE, B creator, two closed polls with distinct aware ends straddling Chicago DST conversion, one open P → GET 200, only closed PKs ordered end descending, names/creator/counts, correct local times, zero message vs positive bars; no live choices attributed as historical ballots. Empty history → no-polls text; equal ends → assert membership only pending POL-07 tiebreak. Nullable legacy aggregate handling requires decision alongside DEF-04; do not assume reconstructed ballots.

**PP-28 live login-only audience and payload** — P1 P/Q; PP-V04-LIVE, PP-V02-COUNT. For each authenticated no-profile/no-role/ALUMNI/ACTIVE/EXEC user with global choices and no open poll → GET 200 application/json exact integer keys/counts (including zero), no writes. Anonymous → login redirect with next and no counts disclosed. Counts remain unrelated to creator/open poll. POL-03 must approve current login-only audience; until then record current behavior without adding an ACTIVE restriction as fact.

**PP-29 page/history/cast access matrix** — P0 P; PP-V04-PAGE/HISTORY, PP-V02-CAST, PP-SHARED-ROLE. For each denied row in actor matrix → GET page/history and POST aye with safe Referer → denial redirect/message and complete poll/choice snapshot unchanged; ACTIVE-only and ACTIVE+extra → 200/read or own vote change; EXEC-only remains denied. GET paths with no Referer deny to named poll, potentially self-looping when followed; assert single response only and flag DEF-05. Shared role helper message/ALL tests remain AUTHENTICATE-owned.

**PP-30 resolver/HTTP methods** — P2 P/D/Q; PP-V04-ROUTES and all mounted reads. Resolve/reverse four named routes to correct view and `/poll/` prefix; count exactly two identical live definitions, both point to same callable (diagnostic defect, not requirement to retain duplicate). Valid-CSRF POST history/live is observed read-only; GET create has no writes; PUT/PATCH/DELETE page/create/history/live currently fall through read rendering/JSON, not mutation. POL-08 decides explicit method rejection in API migration; no unguarded method should gain writes.

**PP-31 admin icon/sorting** — P2 P; PP-C03-ICON/READ. `SimpleTestCase` for unsaved poll instances counts (2,1),(1,2),(1,1),(0,0) → call actual icon → safe HTML with green Passed/red Failed/gold Tied; short_description Result and admin_order_field Yes. Integration staff+view permission changelist ordering column → sorted by Yes, not margin/ratio/result category. DB unchanged; test visible text/attributes rather than full HTML.

**PP-32 admin nullable aggregates** — P1 D/Q; PP-C03-ICON/READ. ORM poll with yes NULL/no 1, reverse, both NULL (schema permits) → icon/changelist currently raises TypeError → safe target DEF-04: no 500 and an approved unknown/zero display policy, preserving persisted NULL unless explicitly migrated. Do not claim incidental crash or implicit zero coercion as preserved behavior.

**PP-33 admin permission matrix** — P0 P; PP-C03-READ/WRITE. Isolated admin-enabled test settings/URL configuration, synthetic anonymous, nonstaff, staff no perms, staff view-only, each granular add/change/delete, superuser; profiles/roles independent. GET changelist/add/change/delete and valid CSRF POST change/delete → assert Django login/permission boundaries and only permitted operation writes; view-only cannot POST edit/delete, EXEC+ACTIVE nonstaff cannot access. Separately existing public-demo middleware must still return admin 403 (AUTHENTICATE ownership). Coordinate setting isolation rather than disabling a production safeguard globally.

**PP-34 admin CRUD and validation** — P1 P/Q; PP-C03-WRITE. Staff with all poll perms, A/B creators and choices, isolated admin → add valid poll with supplied creator B; GET/change name/counts/end; reject missing name/creator, overlong name, malformed integer/date; successful saves redirect, invalid form redisplays without writes; no choice reset from admin edits. Delete one poll then selected bulk-delete confirmation flow → only selected polls removed, other polls/choices/users/profiles unchanged. POL-04/09 must approve editable ownership/aggregate fields and retention before treating destructive behavior as approved business contract.

**PP-35 admin lifecycle bypass** — P0 Q/D; PP-C03-WRITE, PP-V03-CLOSE. Open P with choices → admin set end/counts directly, then public close → observed P already closed and choices remain, no helper reset. Clear end on a previously closed poll then public close → can overwrite aggregates/reset all choices. Negative aggregate counts are model/form integers without minimum; characterize whether accepted. POL-01/09 decide validation, lifecycle permissions and audit requirements; safe migration tests should reject or implement approved coordinated transition, not endorse history corruption.

**PP-36 model ownership/retention boundaries** — P1 P/Q; PP-V01-CREATE, PP-V02-CAST, PP-C03-WRITE. Real ORM fixture A/B, A-created polls and A current choice → uniqueness prevents second choice for same nonnull user; accepted choices tested via full_clean, while raw save can bypass model choice validation. No poll FK exists to populate; do not invent one. In isolated transaction delete synthetic A → observed CASCADE removes A polls/current choice, B records survive; POL-09 decides historical retention before preserving cascade data loss. Nullable orphan-user rows are possible under model definition, not a supported ballot-history feature.

**PP-37 post-close stale current context** — P2 D/Q; PP-V03-CLOSE, PP-V04-PAGE. A allowed/P open → end_vote → current response still includes preselected poll object, potentially old counts/end and vote buttons; fresh GET excludes P and history includes it. Diagnose DEF-06; approved target recomputes context or PRG after state change, without asserting old HTML as contract. Other poll metadata/choice PKs preserved. Refresh/replay implications handled by PP-18/19.

**PP-38 role denial redirect integration** — P0 D/P; PP-SHARED-ROLE, PP-V01-FORM/CREATE, PP-V04-PAGE/HISTORY. A no-role, P/choices snapshot → denied route with same-origin Referer, no Referer, external `https://example.invalid/` and scheme-relative Referer (no network/follow) → same-origin denial usable; current raw external Location is defect DEF-05. Safe target constrained same-origin fallback and no infinite poll redirect loop; shared primitive tests/decision belong to AUTHENTICATE. Assert no writes on each route; do not duplicate decorators' full callable test suite locally.

**PP-39 create save failure/time boundary** — P1 D/Q; PP-V01-CREATE. `TransactionTestCase`, A allowed, existing P/choices, freeze T → inject new poll.save failure before write → no new poll, existing metadata/choices unchanged; current exception is unhandled. Separately freeze view-assigned time T and model auto-add T+delta using controlled clock sequence → saved start is model time, not caller-supplied time; no assertion that both clock calls are inherently simultaneous. POL-06 chooses error translation/retry behavior without claiming automatic idempotency.

**PP-40 live template DOM boundary** — P2 D; PP-V04-PAGE/LIVE. A ACTIVE, zero initial counts or no poll → render page; live fetch payload later becomes nonzero or stays zero → current script dereferences missing aye-bar/nay-bar nodes (initial zero template creates only no-votes); safe target DEF-07 creates/guards nodes and renders updates/zero without exception. Proposed small browser component case in migration suite; Django template assertions verify conditional nodes now, not JavaScript execution. Preference key `liveUpdateEnabled` toggles browser localStorage and enables fetch, not server session writes; interval is 1500ms despite comment saying five seconds. Requires approved frontend harness; no browser/network executed Wave 1.

## Inventory completeness and current coverage

| Operation | Named cases | Existing assertions inspected |
| --- | --- | --- |
| PP-V01-FORM | 01,04,30,38 | demo executive GET 200 only |
| PP-V01-CREATE | 02-06,36,39 | none |
| PP-V02-DISPATCH | 05,07,09-12,23 | demo Aye branch only |
| PP-V02-CAST | 05,07-10,13-14,23-24,29,36 | demo response 200 and own Aye value |
| PP-V02-COUNT | 15-16,28 | no direct count assertions |
| PP-V03-CLOSE | 05,12,16-25,35,37 | none |
| PP-V04-PAGE | 13-14,26,29-30,37-38,40 | demo executive 200/current name |
| PP-V04-HISTORY | 27,29-30,38 | demo executive 200 only |
| PP-V04-LIVE | 05,15,28,30,40 | demo executive 200 only |
| PP-V04-ROUTES | 30 | implicit four-route demo requests |
| PP-C03-READ | 31-33 | no domain admin assertions |
| PP-C03-WRITE | 33-36 | none |
| PP-C03-ICON | 20,31-32 | none |
| PP-SHARED-ROLE | 04,17,29,38 plus AUTHENTICATE shared suite | privileged page GETs do not prove ALL or denial policy |

40 named designs cover all 14 operations; variants are not counted as separate executed tests. There is no line/branch coverage measurement. Source inspection and document review are the only checks performed by this agent; coordinator owns the single shared application baseline.

## Defects, policy decisions and shared dependencies

| Register | Finding / required resolution |
| --- | --- |
| DEF-01 P0 | Non-EXEC ACTIVE closes/reset despite error (`functions:27-41`). Add real authorization stop at action/service boundary before any writes; do not retain bug as passing contract. |
| DEF-02 P1 | start_vote dispatcher discards redirect (`functions:52-53`); obsolete path policy needed. |
| DEF-03 P0 | Closure save/reset nonatomic; no row locks, count snapshot or open constraint (`functions:24-41`). Partial failure and two races can lose/misattribute votes/overwrite history. Repair strategy must precede asserted transactional guarantee. |
| DEF-04 P1 | Nullable aggregate comparison crashes admin (`models:15-16`, `admin:21-25`). Unknown/zero policy needed. |
| DEF-05 P0/P1 | Shared decorator trusts Referer and fallback can redirect denied poll to itself (`decorators:26-48`). AUTHENTICATE owns shared fix/tests; route integration here. |
| DEF-06 P2 | Current poll selected before mutation remains stale after close (`views:22-25,32`). |
| DEF-07 P2 | JS assumes bars exist when zero/no-poll template omits them (`poll_index.html:49-64,114-147`). |
| DEF-08 P2 | Duplicate identical live route (`urls:8,11`); resolve once, cleanup decision without inventing alias. |
| POL-01 | Exactly one open poll? What target identity governs casts/close/retry? Reject casts when none? Handle residual choices and existing simultaneous polls without inventing per-poll ballot schema. |
| POL-02 | Reject mixed/unknown keys or preserve priority? Remove hidden start action? Are repeated creates idempotent? |
| POL-03 | Confirm login-only live audience vs ACTIVE pages/history; which users/roles/orphan rows count? No voter eligibility filtering exists today. |
| POL-04 | Is close chapter-wide for EXEC+ACTIVE regardless creator? Must helpers enforce actor/profile/roles independently of HTTP? |
| POL-05 | Tie/zero result meaning beyond admin display; quorum or majority rules are not implemented. |
| POL-06 | Atomic close/reset or recoverable workflow; accepted vote linearization point; concurrent loser response; repeat close immutability; error translation and repair after partial failure. |
| POL-07 | Equal start/end ordering requires deterministic tie-break if business relies on order; current queries specify only one datetime column. |
| POL-08 | Allowed methods and future API response contracts; legacy 200/302/JSON assertions must remain adapters around reusable state invariants. |
| POL-09 | Admin field editing/lifecycle controls, nullable/negative counts, creator changes, delete/bulk delete and user-cascade historical retention; audit requirement absent today. |

Shared prerequisites: AUTHENTICATE factories with explicit profiles/role sets, shared requires_role contract and safe redirect policy; coordinator-owned test settings and discovery reconciliation (existing `tests.py` plus new singular `test/`); controlled clock; isolated admin URL configuration with granular Django permissions/LogEntry snapshots; PostgreSQL ephemeral test database and bounded synchronization; optional frontend runner for PP-40. Admin writes may produce standard Django LogEntry rows (framework-owned) even though public poll flows have no audit writes; assert expected action/change message and no unrelated logs in admin CRUD cases. Do not bypass demo boundary accidentally or globally. No media fixture is required for this domain.

## Ordered Wave 2 checklist

1. Coordinator verify source citations, baseline and shared test infrastructure; reconcile AUTHENTICATE decorator ownership and all POL decisions. Fix authorization/redirect safety first; unresolved cases remain documented blockers, not passing assertions or unexplained skips.
2. Introduce singular `test/__init__.py` and scoped modules; verify actual discovery using `manage.py test PARLEYPRO.test` and app label. Keep shared fixtures external to domain implementation; no dependency installation assumed.
3. Implement reusable fresh-state assertions and minimal synthetic factories; creation/access/ownership/CSRF cases first (01-08,17,29,38), preserving only approved behavior.
4. Implement dispatch/count/read cases, explicitly resolving malformed keys/no-open/multiple-open policies before freezing assertions; maintain business-vs-legacy adapters.
5. Implement corrected close flow and injected failure cases (16-23,37,39); use TransactionTestCase/autocommit for partial write evidence and safe rollback/recovery expectations.
6. Provision approved PostgreSQL test settings and separate-connection workers; implement bounded races 24-25 against approved linearization/immutability rules. SQLite runs stay separate and cannot satisfy this checkpoint.
7. Implement C03 isolated admin permissions/CRUD/icon and retention policy tests (31-36), preserving public-demo admin-block coverage under AUTHENTICATE. Add browser/component case 40 only with approved harness.
8. Run scoped then shared integration checks once changes justify them; record exact commands/results/backend and measured coverage only if collected. Update this inventory from proposed to implemented case references and report unresolved defects without claiming approval.
