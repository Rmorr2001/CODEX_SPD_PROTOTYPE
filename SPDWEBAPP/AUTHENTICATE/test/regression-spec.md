# AUTHENTICATE regression specification — Wave 1

## Evidence and status

Inspected local branch `prototype/railway`, commit
`7e25ac2f06b2d88a0220526771585f30df10c57a` in
`/workspace/CODEX-SPD-PROTOTYPE` (repository `Rmorr2001/CODEX_SPD_PROTOTYPE`).
Read the complete [shared contract](../../../docs/testing/wave-1-agent-prompt.md)
and root [AGENTS.md](../../../AGENTS.md); a filename search found no nested
AGENTS.md in this checkout. This is inspection evidence, not execution evidence.
No app tests, network, dependency installation, Git mutations or application
changes were performed. Shared baseline execution belongs to the coordinator.

All source citations below are repository-relative. `V` means
`SPDWEBAPP/AUTHENTICATE/views.py`, `M` means
`SPDWEBAPP/AUTHENTICATE/models.py`, `U` means
`SPDWEBAPP/AUTHENTICATE/utils.py`, and `AD` means
`SPDWEBAPP/AUTHENTICATE/admin.py`. These abbreviations apply only to citations.

Inspected sources:

| Source | Relevant evidence |
| --- | --- |
| `SPDWEBAPP/AUTHENTICATE/urls.py:4–17`; `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:23–40` | Twelve mounted auth routes under `/auth/`; configured admin prefix; media served by core URLconf. |
| `V:26–305` | Every mounted view, request parsing, response and write ordering. |
| `M:8–138` | PClass enum, unique Role names, nonunique Major names, nullable one-to-one user, image save hook, ordered links. |
| `SPDWEBAPP/AUTHENTICATE/forms.py:6–10` | CreateUserForm includes email, username and two password fields; imported but never invoked by mounted views. No registration route. |
| `U:4–84`; `SPDWEBAPP/AUTHENTICATE/management/commands/clean_majors.py:4–13` | Substring filter/whitelist, broken unused helper, destructive cleanup and command. |
| `AD:8–85` | Custom user/profile admin, role/major/link registration; unused profile form. |
| `SPDWEBAPP/PARLEYPRO/pp_decorators.py:7–52` | Shared ALL-role gate and unchecked referrer redirect. Imported into auth views but not applied there. |
| `SPDWEBAPP/NEWMEMBER/views_functions.py:190–192` | Dashboard role lookup dereferences a required profile. |
| `SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/login.html:276–290` | Form-encoded credentials and CSRF token. |
| `SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/profile.html:14–67,126–143,180–263,369–418,468–543` | Multipart upload, hidden pclass, JSON password/major requests, form-data profile edits; UI-only two-major restriction; duplicate major request listeners and custom-major HTML interpolation. |
| `SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45,65–85,188–209`; `SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/dashboard.html:9–34` | Visible profile attributes, client sorting, links and active-announcement include. |
| `SPDWEBAPP/HOME/templates/HOME/navbar.html:74` | Logout is a GET link. |
| `SPDWEBAPP/SPDWEBAPP_CORE/settings.py:70,93–100,136`; `SPDWEBAPP/railway_demo/settings.py:16–37` | Core/login URL differs by trailing slash from demo; session/auth/CSRF middleware, password validator configuration; demo URLconf, boundary middleware, secure cookies, isolated storage references. No secret config read. |
| `SPDWEBAPP/railway_demo/views.py:8–23`, `urls.py:4`, `middleware.py:4–12` | Persona mapping/default/group query, POST-only entry, public admin denial. |
| `SPDWEBAPP/AUTHENTICATE/tests.py:1–3`; `SPDWEBAPP/railway_demo/tests.py:13–109` | Empty domain scaffold versus existing integration assertions below. |

## Classification and test conventions

**P (preserve)** means a candidate ordinary business contract grounded in source,
subject to coordinator approval. **F (defect)** means unsafe or broken behavior
requiring a regression that exposes the issue, never a passing assertion that
requires the issue. **Q (decision)** means business/error/transport policy is
unresolved. Classifications can coexist: preserve successful behavior while
rejecting an unsafe failure path. Priorities P0/P1/P2 are independent of these
classification letters. No F/Q case is completed coverage, an unexplained skip,
or a silently passing characterization of a vulnerability.

Every case below is pseudocode with `setup → action → response → state` order.
`unchanged` always means refresh A/B Users and profiles, role/major relations,
relevant catalog rows, files and session identity from fresh state. Unless a case
explicitly lists writes, those records/fields must remain unchanged, including
password hash, staff/superuser flags, User first_name/last_name, other profile
fields and target B. Record file paths/bytes before requests. No domain audit
model/write appears in these views; admin LogEntry is a separate Django effect.
Transport assertions belong to legacy adapters; reusable assertions describe
identity/ownership, selected majors and image/state invariants. Malformed-input
F/Q cases require a controlled non-success response and preserved state after a
fix; exact status/error schema waits for the named policy decision. Do not assert
500/exception leakage as an acceptable contract.

## Verified operation inventory

Fourteen operation groups cover twelve mounted auth routes plus model/helper,
admin and demo boundaries; A09 contains three mounted routes and A05 includes
the model hook. Inventory counts are groups, not a numerical coverage claim.

| ID | Callable / route / actors and inputs | Observed response and state effects; classification |
| --- | --- | --- |
| AUTH-A01 | `loginPage`, `/auth/login/`, public GET and POST username/password plus query `next` (`V:72–91`) | GET login; successful authenticate/login rotates session identity and redirects raw next or named home; invalid credentials message then login redirect. No profile requirement. P success; F unchecked next. |
| AUTH-A02 | `logoutUser`, `/auth/logout/`, any actor/method (`V:94–96`) | Django logout flushes session, renders HOME/home.html 200; no method restriction. P logout; Q GET mutation/CSRF policy. |
| AUTH-A03 | `change_password`, `/auth/change-password/`, authenticated JSON POST (`V:99–123`) | Current mismatch/new mismatch JSON false 200; matching values set hash, save User, update current session hash; non-POST JSON false. F missing JSON/type/strength validation. |
| AUTH-A04 | `update_profile`, `/auth/update_profile/`, authenticated form POST (`V:126–164`) | Checks username/firstName/lastName/hometown/pclass profanity; saves own User username/email before own profile fields; success JSON true, non-POST false. Email not filtered; no form/full_clean/transaction. P own editing; F partial writes and malformed input; Q validation. |
| AUTH-A05 | `update_photo`, `/auth/update_photo/`, authenticated multipart `profile_photo`; `Brother_Profile.save` (`V:188–235`, `M:101–127`) | Deletes old local-path image first, saves new; AJAX true/image_url else profile redirect, caught errors JSON false with exception text; missing upload/non-POST redirects. Model thumbnails to at most 300×300, retains format, rewraps image on every save, swallows processing errors. P valid images; F destructive failure/invalid image acceptance; Q storage/format limits. |
| AUTH-A06 | `reset_photo`, `/auth/reset-photo/`, authenticated POST (`V:238–253`) | Deletes image with implicit model save then sets None and saves again; true/message or caught false/message, non-POST false. P reset; F partial file/database failure. |
| AUTH-A07 | `update_majors`, `/auth/update_majors/`, authenticated JSON `majors` (`V:256–276`) | Missing key defaults empty; clears own links then exact-name get_or_create/add per item; no normalization, profanity or count validation; true/message or caught false, JSON parsing outside try. P explicit replacement/empty; F partial writes; Q input/maximum/catalog rules. |
| AUTH-A08 | `add_custom_major`, `/auth/add-custom-major/`, authenticated JSON `major_name` (`V:279–305`) | Strip/filter, split whitespace/title each word via capitalize, get_or_create; true id/name; no own link added; error/non-POST false. Empty accepted; duplicates possible since M:83 nonunique. P normal normalization; F races/invalid input; Q uniqueness/acronyms/filter policy. |
| AUTH-A09 | `dashboard`, `roster`, `alumni_roster`, authenticated GET under `/auth/` (`V:26–69`) | NEW_MEMBER dashboard redirects `/newmember/` even with other roles; others render links ordered by model order and active announcements. Roster excludes any ALUMNI; alumni roster includes ALUMNI; both distinct/lastName ordering and PClass map. No role gate beyond login. P normal rendering; Q visibility/mixed roles/ties; F missing-profile dashboard exception. |
| AUTH-A10 | `profile`, `/auth/profile/`, authenticated (`V:167–185`) | Own profile and sorted available majors. Accessing image URL exception sets None and saves profile during GET; no file-existence check if URL accessor succeeds. P own view; F destructive read; Q missing-profile response. |
| AUTH-A11 | `contains_profanity`, `clean_profanity_from_user_fields`, `clean_existing_majors`, `clean_majors` command (`U:4–84`) | Substring blacklist with any whitelist substring suppressing rejection; text.lower requires string. Unused cleaner references undefined inappropriate_words. Cleanup deletes catalog majors and their all-profile M2M links; count and command output, no transaction. P ordinary clean/count; F broken helper/bypass; Q collateral deletion/filter policy. |
| AUTH-C03 | Role/User/Profile/Major/DashboardLink and custom admin/forms (`M:58–138`, `AD:8–85`), shared `requires_role` | Real Django staff/model permissions differ from app roles. Role unique choices; Major nonunique. Custom user admin omits editable privilege fields, read-only profile image may crash without profile; profile admin can edit roles/image. ALL-role decorator denies missing profile/roles to raw referrer or poll. CreateUserForm and Brother_ProfileForm are unmounted/unused; latter is not assigned as ProfileAdmin.form and mutates M2M even with commit=False. P normal identity/admin; F escalation/redirect/form failure; Q policy. |
| AUTH-D01 | `railway_demo.views.enter`, `/demo/enter/`, public POST (`railway_demo/views.py:8–23`) | DEMO_MODE false 404; unknown persona 400; default executive; active nonstaff nonsuperuser group member with unusable password required else 503; login explicit ModelBackend; alumni redirect roster else dashboard. Group, not username, is query identity; no profile/role validation. P seeded entry; Q spoofed/duplicate group members and missing profiles. |
| AUTH-D03 | Admin blocking portion only, middleware (`railway_demo/middleware.py:9–12`, core URLs:25) | `/admin/` prefix always JSON error 403 in demo, regardless actor/method; only exact hardcoded prefix protected, whereas core admin mount uses ADMIN_URL. P public demo exclusion; F/Q configured-prefix mismatch. Other D03 work belongs to coordinator. |

No registration, password-reset/email workflow or arbitrary-profile detail/update
route is mounted. A06 is photo reset. App roles do not imply Django is_staff or
is_superuser; no profile-creation signal was found among inspected domain files.

## Role and ownership matrix

Use explicit independent fixtures; never infer access from visible buttons or a
privileged executive persona. `R` below is direct HTTP access, not downstream
permissions at the link destination. All own mutation endpoints select by
request.user and ignore posted target IDs.

| Actor | Dashboard | Rosters | Own profile/mutations | Shared requires_role('EXEC','ACTIVE') | Admin |
| --- | --- | --- | --- | --- | --- |
| Anonymous | login redirect with next | same | same | login redirect/message, no next preservation in decorator | core Django admin login; demo 403 |
| Authenticated, no profile | source raises on role lookup | R; no requester profile lookup | profile/update_profile raise; photo/reset/majors catch missing profile; password and custom major do not need profile | denies missing profile | staff/perms independent; custom user image display risk |
| Profile, roles=() | R | R | own R | denied both roles | no staff privilege |
| ACTIVE only | R | R | own R | denied EXEC | no staff privilege |
| EXEC only | R | R | own R | denied ACTIVE | no staff privilege |
| PHIL_CHAIR only / NM_BOARD only / NME only | R | R | own R | denied both | no staff privilege |
| EXEC+ACTIVE | R | R | own R | allowed | still no staff privilege |
| PHIL_CHAIR+ACTIVE | R | R | own R | denied EXEC | still no staff privilege |
| NEW_MEMBER only; NEW_MEMBER+ACTIVE; NEW_MEMBER+EXEC+ACTIVE | `/newmember/` redirect | R | own R | only last combination allowed | no staff privilege |
| ALUMNI only; ALUMNI+ACTIVE | R | R | own R | denied EXEC | no staff privilege |
| staff with no app roles | profile-dependent | R | own R | denied | requires model permissions; demo 403 |
| superuser with no app roles | profile-dependent | R | own R | denied (no implicit bypass) | core allowed; demo 403 |

For each authenticated row test actor A and distinct B profile, including B
ALUMNI/no-role: submitted user/user_id/profile_id/roles/is_staff/is_superuser must
not switch target or elevate privileges. Roster reads deliberately show other
profiles' name/photo/class/majors/hometown/roles (`roster.html:30–45`); approval of
which members may see those attributes is Q-VIS. No email column is rendered.
Do not turn current broad visibility into an approved authorization policy.

Shared decorator is **ALL**, computed as every missing role at pp_decorators:36;
there is no ANY implementation. Real usages include poll start
`PARLEYPRO/views.py:36` (EXEC+ACTIVE) and philanthropy approve
`PHILANTHROPY/views.py:83` (PHIL_CHAIR+ACTIVE), with single-role routes too.
A shared adapter can test a sentinel wrapped view without mocking business
behavior, then sibling domains verify mounted endpoints. Empty role list admits
an authenticated user with a profile but still denies a missing profile. If a
future API permission helper uses ANY, migration changes behavior unless policy
is explicitly changed. Untrusted HTTP_REFERER denial redirects are F-REDIR.

## Proposed shared interface and isolation

Coordinator-owned safe settings should use synthetic secret key, in-memory or
throwaway DB, temp MEDIA_ROOT, local filesystem storage, no external services,
real auth/session/messages/CSRF middleware, deterministic templates, fast test
password hasher and explicit root URLconf. Name remains unchosen; do not create
another independent harness. Keep two modes: business core admin route with demo
middleware absent and demo URLconf/middleware enabled; preserve secure-cookie
behavior through HTTPS test requests when testing demo CSRF/session flow.

Propose shared `make_user(roles=(), with_profile=True, **fields)` and
`make_profile(user, **fields)`: get/create Role names explicitly, set a synthetic
usable password unless unusable requested, never infer ACTIVE from EXEC, never
set staff automatically, return User and access profile through the ORM. Allow
`is_staff`, `is_superuser`, `is_active`, username and profile field overrides;
reject contradictory preexisting profiles. Factory defaults should not attach
images or majors. No-profile users must be possible without creating/deleting
signals. Add `make_major(name)`, fixture-only persona group helper,
`temporary_media()` plus synthetic Pillow PNG/JPEG/GIF bytes and controlled
clock; keep small domain-only helpers local if no sibling needs them.

Fixtures: A and B each have a User/profile, separate majors and image bytes;
no-profile user N; roleless Z; each narrow combination in matrix; inactive user;
staff without permissions, staff with relevant view/add/change/delete perms and
superuser; orphan Brother_Profile(user=None). Use fixed synthetic names and
reserved `.invalid` email domains. Cross-domain MISC announcement fixture supplies
active/inactive rows; use explicit dates/clock for template daylight alert.
Storage spies/fakes may inject open/save/delete/url/path failures at boundaries,
never mock profile/business operations. ORM writes and file bytes are real by
default. Failure and race tests need transaction isolation; PostgreSQL duplicate
creation tests require two independent connections and bounded synchronization,
not a SQLite conclusion. No existing uniqueness constraint prevents Major races.

## Named implementation cases

The following 55 named cases include parameterized variants. Each row is a
setup/action/response/state specification, not an implemented test. The common
unchanged-state rule above applies to every row. P0 security/failure gates take
precedence over legacy response details. `JSON false/true` denotes HTTP 200 and
`success` boolean for ordinary implemented legacy branches only. For F/Q cases,
choose safe statuses and response schemas through decisions below before approval.

### Login, logout and password

| Case / operation | Priority / classification | Setup → action → response assertions → state assertions / dependency |
| --- | --- | --- |
| AUTH-A01-01 | P1 P | A active with usable password, anonymous session marker → GET login then form POST valid credentials without next; repeat with local `/auth/roster/?x=1` next → 200 login/form CSRF token, then redirect home/local path respectively → session `_auth_user_id` is A, anonymous key changes; password/profile/B unchanged. Also authenticate N without profile; login itself must succeed. |
| AUTH-A01-02 | P1 P | A known username → POST wrong, empty, missing username/password and inactive A variants → redirect login, error message without credential echo → no authenticated identity, no User/profile changes; existing authenticated A GET login renders rather than silently switching user. |
| AUTH-A01-03 | P0 F/Q-REDIR | A and synthetic credentials → POST valid login with absolute external next, `//other.invalid/`, encoded variants and harmless local path → external destination must not be emitted after approved safe redirect policy; local next preserved → A may authenticate but no external navigation; DB unchanged. Source currently redirects unchecked; this must expose defect, not bless it. |
| AUTH-A01-04 | P1 Q | Authenticated A, separate B credentials → POST valid B login and unknown credential attempts; GET/PUT login with next → define identity-switch/non-POST policy, assert no unexpected redirect to next without authentication → session identity changes only on accepted B auth; all profile/role data unchanged. Dependency Q-METHOD. |
| AUTH-A02-01 | P1 P/Q | A authenticated with session marker → request logout twice via current GET link, separately POST valid token → legacy 200 HOME/home.html on ordinary logout; method acceptance awaits Q-METHOD → identity/session marker removed, later protected request redirects login; User/password/B unchanged. |
| AUTH-A02-02 | P0 Q | Anonymous and A with CSRF-enforced clients → POST no/invalid/valid token; GET from external navigation → invalid POST 403, valid accepted response; decide GET logout safety and accepted methods → rejected operations preserve session; accepted logout flushes only caller session. Q-METHOD; source GET currently changes state. |
| AUTH-A03-01 | P0 P | A authenticated in clients C1/C2 using old password, B independent → C1 JSON POST current password and matching new password → JSON true → fresh A hash validates new, rejects old; C1 remains authenticated through next protected request; C2 with old session hash becomes anonymous on next protected request; B/session and all profile fields unchanged. |
| AUTH-A03-02 | P1 P | A → JSON wrong current password, then mismatched new passwords with correct current, then GET → false with exact respective error strings in V:111/115/123 → original hash and current session retained; no profile writes. |
| AUTH-A03-03 | P0 F/Q-PARSE | A → malformed JSON, JSON list/null, missing current, missing both new fields, numeric/list/null new values, empty/whitespace strings and oversized body variants → controlled non-success for invalid input; approved password policy decides acceptable boundaries → no unusable/empty password or partial hash write from malformed request; session retained. Source can set unusable password when both new fields absent and current is correct; no password validators called. |
| AUTH-A03-04 | P1 F/Q-PASSWORD | A → reuse current password; weak/new common password; exact leading/trailing whitespace payload; inject User.save failure before hash update → validation/status chosen explicitly, never treat UI `.trim()` as backend rule → accepted password uses exact approved input; rejected/save-failure keeps persisted hash and session consistent; no B/profile mutation. Decide validator/reuse/whitespace policy and controlled failure response. |

### Own profile writes and images

| Case / operation | Priority / classification | Setup → action → response assertions → state assertions / dependency |
| --- | --- | --- |
| AUTH-A04-01 | P1 P | A/B, A image absent → form POST all six fields with valid pclass, plus hostile `user_id=B`, `roles=EXEC`, `is_staff=true` → JSON true → A User username/email and profile firstName/lastName/hometown/pclass updated; User first_name/last_name/password/privileges, A role/major links, B entirely unchanged. Repeat same request; same values, no added records. |
| AUTH-A04-02 | P1 P/F | A → POST each filtered field with an independently rejected blacklist term, other fields clean; GET → false inappropriate-language/invalid-request messages → no User/profile writes. Include clean whitelisted biological engineering to exercise accepted helper branch separately; whitelist-plus-profanity bypass is F under A11-02, not a success contract. |
| AUTH-A04-03 | P0 F/Q-VALID | A/B unique usernames → duplicate B username; omitted each field; null-like multipart strings; empty username/email; invalid email/pclass; lengths just at and above User/profile limits; Unicode/control text → controlled validation error as approved → no clobbering other fields or database errors; original A/B state intact. Source missing filtered fields can call None.lower; choices/email are not validated by direct save. Database backend length enforcement differs; do not approve SQLite acceptance. |
| AUTH-A04-04 | P0 F | A with valid new username/email and profile values → inject profile.save failure after User.save; separately stored A image makes model storage fail during profile save → controlled non-success → target invariant is all requested identity/profile fields retained together or not written, with old file retained; demonstrate current partial User writes. Atomicity/storage compensation requires implementation, not presumed TestCase rollback. Q-ATOMIC. |
| AUTH-A04-05 | P0 F/Q | N no profile; A image exists → submit valid profile request as N; as A edit only text while observing image name/storage writes → missing profile handled safely; ordinary edit JSON true → N receives no unintended User write (lookup currently precedes User.save); A unrelated image bytes/path should not be replaced or orphaned without approved policy. M:101 reprocesses image on every save; Q-IMAGE and Q-PROFILE. |
| AUTH-A05-01 | P1 P | A/B, temporary media, A no image → multipart valid 900×450 PNG and 80×40 JPEG separately, AJAX header on/off → AJAX JSON true/url, ordinary redirect profile → actual stored image readable, dimensions 300×150 / 80×40 (no upscale), format retained, belongs to A; roles/majors/User/B unchanged; assert path exists under temp media, no real upload access. |
| AUTH-A05-02 | P1 P/F | A old synthetic photo → upload new valid image, then repeat same filename; separately call profile.save after text edit → correct response and valid latest image → proposed invariant one current valid image, no deletion of B, identify old-file deletion on successful replacement; enumerate extra orphan paths from unconditional model rewrap/collision. Old retention/orphan cleanup on repeated model saves needs Q-IMAGE, not byte-for-byte encoding assertions. |
| AUTH-A05-03 | P0 F/Q-IMAGE | A old image → upload text bytes named .png, truncated image, zero bytes, unsupported format/content-type mismatch; boundary size/dimension files defined by approved limits → non-success safe response; no exception path leakage → old valid image/pointer retained, invalid bytes not accepted. Source catches image-processing error and still saves original upload, so current success is a defect. No invented upload limit. |
| AUTH-A05-04 | P0 F | A old image → inject old delete error, new storage save error, DB save error after file save, url/path exception after DB save as separate subcases → controlled failure; no internal path/exception leakage → record fresh DB pointer and old/new bytes at each phase, assert approved compensation invariant: previous usable image survives unsuccessful replacement, no untracked orphan. Source old delete occurs first and exceptions after successful save can return false despite changed state. Q-ATOMIC/Q-STORAGE. |
| AUTH-A05-05 | P1 P/F/Q | A and N → GET, POST missing/wrong file key, no-profile upload, and storage lacking .path → GET/missing-key redirect profile; caught missing-profile branch currently false; approve portable storage/non-profile behavior → no changes for no-upload requests/N; supported storage saves readable A image safely without local path requirement. Direct model save invalid/animated/transparency inputs requires Q-IMAGE; verify image decode/format/frame policy through real bytes. |
| AUTH-A06-01 | P1 P | A image and B image → POST reset twice → true/reset-success message both times → A image null/empty, old A file gone, B file/pointer and all identity/role/major fields unchanged. No image initially yields same ordinary success. |
| AUTH-A06-02 | P1 P/Q | A and N → GET reset, then N POST → false invalid-request on GET; missing-profile controlled false without raw exception detail after approved error policy → no DB/file/User changes, no profile auto-created. Q-PROFILE/Q-ERROR. |
| AUTH-A06-03 | P0 F | A image → inject storage.delete failure; separately DB save failure during FieldFile.delete's save and final explicit save → non-success safe response → inspect DB and bytes after each phase; prevent DB pointing at deleted image, preserve/compensate old file under approved Q-ATOMIC policy. Source delete(save=True) plus second save is not atomic. |

### Major selection/catalog and cleanup

| Case / operation | Priority / classification | Setup → action → response assertions → state assertions / dependency |
| --- | --- | --- |
| AUTH-A07-01 | P1 P/Q | A owns Old, B owns Other, catalog New exists → JSON `majors:[New,New]` then explicit `majors:[]`, repeat → JSON true/message → A links exactly unique New then empty; B links and Old/New catalog rows remain; no roles/User changes. Empty explicit selection preserves intentional clear; omitted key clearing awaits Q-MAJORS. |
| AUTH-A07-02 | P0 F/Q-MAJORS | A/B → missing key, malformed JSON/list/null body; `majors` null/string/dict; list with nonstrings/blank/overlength/profanity/case variants; three distinct majors bypassing UI → controlled validation error or approved accepted cardinality, no partial clearing on invalid requests → A/B old links/catalog unchanged for rejected payloads; no new bad catalog rows. Source iterates strings and trusts names; max 2 is UI-only and not yet a server policy. |
| AUTH-A07-03 | P0 F | A owns Old → inject failure on second exact-name get_or_create/add after first succeeds → JSON false branch, approved safe error body → all old A links retained and no partial new links/catalog under approved atomicity rule; B unchanged. Demonstrate current clear/partial-write ordering; use transaction-aware failure test, not outer TestCase rollback as evidence. Q-ATOMIC. |
| AUTH-A07-04 | P1 P/F/Q | A, N and preexisting duplicate-name Major rows → GET; N valid POST; A request duplicate exact-name catalog then two repeated valid replacement requests → GET false invalid-method; N controlled false; duplicate catalog non-success without destructive clearing → no profile creation/N writes, B unchanged; deterministic exact-name resolution/duplicate remediation requires Q-UNIQUE. Concurrent replacements require Q-MAJORS final-state policy and PostgreSQL independent connections if claimed. |
| AUTH-A08-01 | P1 P/Q | A/B, no matching catalog → JSON `major_name:'  mechanical   ENGINEERING  '` twice → true stable id/name `Mechanical Engineering` → single sequential new catalog row, no profile major link added for either actor; relation changes occur only A07. Repeat acronym/Unicode normalization under Q-NORMALIZE before approving examples beyond source capitalization. |
| AUTH-A08-02 | P1 P | A → independently rejected blacklist term, then GET → false with major-profanity/invalid-method message → no catalog/profile writes. Test exact whitelist accepted branch without embedding banned term; mixed bypass belongs A11-02. |
| AUTH-A08-03 | P0 F/Q-VALID | A/N → missing/blank/whitespace major_name, numeric/null/list field, malformed/list/null JSON, >255 characters, markup/quotes → controlled non-success and escaped transport/rendering under approved policy → no empty/invalid catalog entries or profile changes. Source missing name creates empty Major, typed values can crash before try; no-profile actor currently can create catalog because only login is checked (Q-MAJORS). Template uses returned name in innerHTML at profile.html:249–256; add browser/render assertion if retained. |
| AUTH-A08-04 | P0 F/Q-UNIQUE | Catalog has two exact normalized-name rows; separately two PostgreSQL connections synchronized before creation → POST normalized same name → deterministic safe duplicate handling/non-success, never exception leakage → approved unique normalized name invariant and stable result for repeated actors; B relations unchanged. Source Major.name not unique, get_or_create race can create duplicates; sequential idempotency cannot prove concurrency. |
| AUTH-A11-01 | P2 P | Pure inputs clean engineering, uppercase exact whitelist, repeated whitespace whitelist, rejected independent blacklist substring and empty string → call contains_profanity → False/False/False/True/False respectively per source → no DB effects; exercise case-insensitive substring semantics without asserting full blacklist contents. False positives remain Q-FILTER. |
| AUTH-A11-02 | P0 F/Q-FILTER | Pure mixed whitelist-plus-rejected text and benign substring collision; None/int input → call filter and unused clean_profanity_from_user_fields → propose safe documented type/allowlist behavior and no runtime NameError; current whole-input whitelist bypass and undefined inappropriate_words expose defects → no database effects. Do not invent replacement moderation policy; caller validation must prevent malformed type crashes. |
| AUTH-A11-03 | P1 P/Q-FILTER | Good and independently bad Major rows, A/B both linked to bad; whitelisted good → call clean_existing_majors twice → first returns bad row count, second zero → bad majors and their A/B M2M links deleted, good/catalog/User/role fields unchanged. This destructive global-link effect is observed but must be approved before treating as P; denial/soft-delete alternative awaits owner. |
| AUTH-A11-04 | P1 F/Q-ATOMIC | Same cleanup fixtures → call command with captured stdout, then inject failure on second deletion in direct helper → ordinary command output includes accurate removed count; failure controlled/reported per approved policy → after ordinary run deletions match count, repeated command zero; failure must not silently claim completion, inspect earlier deletions and choose transaction/partial report policy. No command auth boundary, operator-only invocation. |

### Visibility and profile reads

| Case / operation | Priority / classification | Setup → action → response assertions → state assertions / dependency |
| --- | --- | --- |
| AUTH-A09-01 | P1 P/Q | Explicit matrix roles including NEW_MEMBER mixed with EXEC/ACTIVE and N → GET dashboard → NEW_MEMBER combinations redirect `/newmember/`, others profile-bearing users 200 dashboard; N controlled missing-profile response after decision → no writes; retain NEW_MEMBER precedence only if Q-VIS approved; do not follow redirect and mistake destination failure for dashboard failure. |
| AUTH-A09-02 | P1 P | Z/A with links order 2/1 and active/inactive announcements under fixed clock → GET dashboard → context/query includes ordered links 1/2 and active only; rendered labels/hrefs/active text, not inactive text; empty fixtures render 200 → no identity/catalog/file mutation. Equal order tie unspecified; no invented secondary ordering. MISC owns announcement CRUD, HOME/MISC own daylight/banner helpers. |
| AUTH-A09-03 | P1 P/Q-VIS | Z, ACTIVE, ALUMNI, ALUMNI+ACTIVE, NEW_MEMBER, orphan profile; distinct last names and multiple roles → GET both rosters as each authenticated matrix actor, including N → 200 and exact queryset partition: any ALUMNI only alumni roster, all others active roster, no duplicate rows, lastName ordering, correct enum pclass map → no writes; assert visible name/photo/class/major/hometown/role fields and no email column. Missing/null last name and equal names require deterministic ordering decision before stronger assertions. |
| AUTH-A09-04 | P0 Q-VIS | A/B with sensitive synthetic profile strings, authenticated roleless/NEW_MEMBER/ALUMNI requesters → direct GET rosters/dashboard even if no UI link → approve access policy and exact field visibility; denied requests after policy must expose neither B attributes nor image links → all B data unchanged; verify template escaping of synthetic `<tag>` names, without full HTML snapshot. Core public media URL exposure is a shared security question, not proven private by logged-in roster gate. |
| AUTH-A10-01 | P1 P | A/B different profiles/majors, catalog names ordered, A no image → GET profile with hostile `user_id=B` → 200 AUTHENTICATE/profile.html, context own A only, available_majors sorted, csrf form inputs correctly named → no record/file writes or B leak; repeat stable. |
| AUTH-A10-02 | P0 F | A image with storage.url raising transient error; separate missing physical file with working URL accessor → GET profile → safe view/error policy, no destructive DB write merely for URL failure; distinguish URL generation from file existence → A pointer/bytes retained on transient failure; missing file handling explicit rather than claiming source checks existence. Source sets None and saves on any URL exception. Q-STORAGE/Q-PROFILE. |
| AUTH-A10-03 | P1 F/Q-PROFILE | N authenticated; A valid image whose storage activity is observed → GET profile as N then repeatedly as A → controlled missing-profile response for N, normal A render → no N profile auto-create unless approved, no A image rewrite on ordinary reads; ensure broad except in A10-02 cannot cause unrelated save/file side effects. |

### Shared identity, roles, admin and demo

| Case / operation | Priority / classification | Setup → action → response assertions → state assertions / dependency |
| --- | --- | --- |
| AUTH-C03-01 | P0 P/Q | Real ORM A/B, Role uniqueness, profile one-to-one, nullable orphan; CreateUserForm valid/invalid email/duplicate username/mismatched passwords → validate/save only in direct form tests → valid form User hash works, errors keyed appropriately → role duplicate and second profile/user constraint rejected, user deletion cascades profile and M2M not shared Role/Major; no automatic roles/staff/profile creation by CreateUserForm. Form is unmounted; do not invent registration HTTP API. Null-user uniqueness depends DB; filesystem cascade cleanup not established. |
| AUTH-C03-02 | P0 P/F/Q-REDIR | Wrap sentinel in requires_role EXEC+ACTIVE; real requests/messages middleware for anon, N, Z, EXEC only, ACTIVE only, both, superuser no roles, and empty required roles → call wrapper with absent/local/external HTTP_REFERER → only complete required set reaches sentinel; missing-role message identifies exact missing names, missing-profile message distinct, absent referrer falls back named poll; external referrer must follow approved safe redirect policy → denied sentinel makes no writes; auth/session/roles unchanged. Empty required set behavior needs explicit policy; no implied superuser bypass. |
| AUTH-C03-03 | P0 P/F | Core admin mode, A nonstaff EXEC+ACTIVE, staff no model perms, permitted staff, superuser; N no profile → GET/change User, Brother_Profile, Role, Major, DashboardLink admin pages and POST forged privilege/role fields with CSRF → nonstaff denied; permitted actions governed by Django model perms; valid admin writes produce appropriate LogEntry; omitted readonly/privilege fields cannot be forged into editable privilege changes → B only changes under explicit authorized admin action. Test no-profile user display safely; current CustomUserAdmin.brother_profile dereferences profile. Q-ADMIN role management policy. |
| AUTH-C03-04 | P1 P/F | Authorized profile admin changes B image/roles through standard form → submit valid image/role choice, then injected image save failure → ordinary redirect/change log and expected B image/model resizing, roles persisted through admin M2M; failure non-success without partial unauthorized privilege state → A unchanged, inspect B image compensation. Direct Brother_ProfileForm tests with existing versus unsaved profile and commit=False/new_major → deferred-save semantics must avoid premature catalog/M2M writes; current form calls majors.add before save and is not wired into admin. Q-ADMIN/Q-ATOMIC. |
| AUTH-C03-05 | P1 P/Q | Core admin, permitted staff edits major/link/order; Role choice invalid; direct model display with no names/profile fields → accepted admin redirects versus invalid form errors → saved link order controls A09, roles remain valid form choices/unique; preserve shared Major links unless explicit delete; readable __str__/get_majors/get_roles and display labels, no assumption unspecified M2M ordering. Direct model save skips choices validation; decide invalid legacy role repair, not passing invalid role contract. |
| AUTH-D01-01 | P0 P | Minimal four synthetic demo persona groups, active users with unusable passwords/nonstaff/nonsuperuser and explicit profiles; CSRF-valid HTTPS client → POST each persona and missing persona; repeat after username change → redirect alumni to alumni_roster, all others dashboard; newmember dashboard then `/newmember/` → correct group-selected session identity, no elevated flags/password/profile mutation. Missing persona defaults executive; changing username does not break group lookup. No shared executive seed needed. |
| AUTH-D01-02 | P0 P | Demo client anonymous or already A → GET, unknown/empty persona POST, DEMO_MODE false POST → 405/400/404 respectively → session identity and all ORM state unchanged; require_POST 405 precedes mode check on GET. Include valid JSON body instead of form: source ignores JSON and defaults executive; approve/reject alternate content-type in Q-DEMO rather than blessing surprise login. |
| AUTH-D01-03 | P0 P/Q-DEMO | Each persona group contains none, inactive, staff, superuser, or usable-password user separately → valid-token POST → 503 for no eligible usable account; no session switch. Then eligible no-profile user and multiple eligible group members → approve deterministic trusted account selection; no accidental access to privileged/other member identity → no roles/profile auto-create or DB writes. Source selects .first by group and checks password only after selection, without username/profile/roles validation. |
| AUTH-D01-04 | P0 P | CSRF-enforced secure client; synthetic active persona → POST absent/invalid token then valid cookie+form token acquired through public page; switch already-authenticated A to persona → 403/403/302 respectively → rejected identity stays A/anonymous, accepted identity is only selected unprivileged persona; A/B Users, groups and profile data unchanged; session key rotates. Existing demo test covers missing token only. |
| AUTH-D03-01 | P0 P | Demo middleware enabled, anonymous/nonstaff/staff/superuser → GET and CSRF-valid POST `/admin/` and nested `/admin/auth/user/` → 403 JSON error for all requests reaching boundary middleware, no admin template, redirects or LogEntry → no identity/ORM changes. An unsafe request rejected earlier by CSRF may also be 403 with different body; test middleware directly separately for unconditional branch. |
| AUTH-D03-02 | P0 F/Q-ADMIN | Core ADMIN_URL set to non-`admin` synthetic prefix while demo middleware enabled → request actual configured admin path, `/admin/`, `/admin` and prefix-like `/administrator/` → actual demo admin mount must be unavailable under approved boundary policy; unrelated paths not accidentally blocked → no admin reads/writes/LogEntry/session privilege change. Source checks only '/admin/'; configured mount mismatch is a defect candidate, not a passing allowed-admin contract. |

### Cross-cutting HTTP/security cases

| Case | Priority / classification | Setup → action → response assertions → state assertions / dependency |
| --- | --- | --- |
| AUTH-S01 | P0 P/Q | Anonymous clients and all authenticated matrix actors with A/B snapshots → invoke all ten login-protected routes (dashboard/roster/alumni_roster/profile plus change-password/update_profile/update_photo/reset-photo/update_majors/add-custom-major), using real respective content types and hostile B targeting → anonymous redirect login with encoded next and no writes; authenticated direct access follows operation matrix, own-only mutation regardless posted target. Login/logout/demo have separate public contracts → no anonymous writes; no role/staff escalation or B mutation. Resolve no-profile responses and Q-VIS. |
| AUTH-S02 | P0 P/Q | enforce_csrf_checks=True, HTTPS when demo cookies secure; A with real token from profile/login and anonymous login → POST login/change-password/update_profile/update_photo/reset-photo/update_majors/add-custom-major/logout with absent, invalid and valid tokens → missing/invalid 403, valid reaches ordinary business response; JSON uses header, multipart/form token accepted → rejected request snapshots unchanged including password/session/files/catalog; accepted request changes only its operation fields. Enumerate GET/PUT/PATCH/DELETE methods too: decisions determine 405/error/redirect; read methods must not accidentally write except documented unresolved logout/profile defects. D01 handles demo separately. |

## Completeness and existing assertions

| Operation | Proposed named cases | Existing source assertions (not executed here) |
| --- | --- | --- |
| A01 | A01-01…04; S02 | demo tests:49–52 login GET 200 only; no credential/session/next tests. |
| A02 | A02-01…02; S02 | None found. |
| A03 | A03-01…04; S01/S02 | None found. |
| A04 | A04-01…05; S01/S02 | demo tests:88–97 checks 200/success and subsequent demo entry 302; no refreshed profile/User field assertions, ownership, validation, partial failure or CSRF. |
| A05 | A05-01…05; S01/S02 | None found; seed/media fixture does not verify upload behavior. |
| A06 | A06-01…03; S01/S02 | None found. |
| A07 | A07-01…04; S01/S02 | None found. |
| A08 | A08-01…04; S01/S02 | None found. |
| A09 | A09-01…04; S01 | demo tests:54–56 anonymous dashboard/roster/profile 302; 58–66 executive renders both rosters/dashboard; 69–77 newmember dashboard redirect and alumni roster 200; no exact role partition/field/state checks. |
| A10 | A10-01…03; S01 | demo tests:60–65 executive profile 200 only. |
| A11 | A11-01…04 | None found. |
| C03 | C03-01…05 | demo tests:37–40 seeded Users unusable/nonstaff/nonsuperuser; 42–47 seed rejects staff/mode; 75–77 active cannot access philanthropy approve. These do not establish narrow ALL-role semantics or core admin permissions. |
| D01 | D01-01…04 | demo tests:69–76 persona navigation; 79–86 GET405/unknown400/missingCSRF403/mode404/staff503; 88–96 post-rename entry still302. No session identity, valid-token, inactive/superuser/password/group multiplicity assertions. |
| D03 admin | D03-01…02 | demo tests:97 `/admin/` 403 after default entry only. No nested/custom prefix/method/anonymous/core permission matrix. |

Case count: 4+2+4+5+5+3+4+4+4+3+4+5+4+2 = 53 domain/shared/demo
cases; S01 and S02 add 2, totaling **55**. Parameter variants are intentionally not
counted as separately implemented cases. S01 covers ten protected mounted auth
routes; login/logout are the remaining two of twelve. Every inventory group has
named cases. Current domain tests.py is only an import/comment. Existing demo
suite has concrete assertions but cannot establish full domain correctness.

## Defects, policy questions and dependencies

| Topic | Evidence / blocker | Required resolution |
| --- | --- | --- |
| F-REDIR / Q-REDIR | V:80–84 raw next; pp_decorators:26,44,48 raw HTTP_REFERER | Agree allowed local/host/scheme behavior and fallback; security regression must reject external redirects rather than codify current behavior. Shared decorator cases are owned here; [PARLEYPRO](../../PARLEYPRO/test/regression-spec.md) owns endpoint applications. |
| Q-PARSE / Q-VALID / Q-ERROR | V:102/259/282 JSON parsing unguarded; None.lower in profile; no profile form validation; detailed exception strings returned | Agree typed request schemas, field presence/length/email/PClass errors and status/schema. Avoid current crashes/raw internals as passing contract. |
| Q-PASSWORD | V:103–120 only current/equality checks; template trims passwords | Agree validator use, empty/unusable handling, reuse and exact whitespace; preserve own session and invalidate other stale sessions. |
| Q-ATOMIC | V:154 before160; 204–211 delete before save; 245 before247; 264 before267; U:81 per-row delete | Agree all-or-nothing field/M2M writes and storage compensation. Database atomic blocks alone cannot restore removed files. Deliberate failure tests must verify fresh state and true transaction boundaries. |
| Q-IMAGE / Q-STORAGE | M:101–127 every save rewrites image, catches decode failures; V:174–177 destructive read; `.path` assumptions | Decide accepted formats/animation/size limits, invalid-image response, metadata/filename rules, old-file cleanup, transient URL behavior and remote storage support; keep real temp bytes in tests. |
| Q-MAJORS / Q-NORMALIZE / Q-UNIQUE | UI max 2 versus unbounded endpoint, two conflicting normalization paths, M:83 no unique key | Decide max count, omitted key versus explicit empty, catalog creation by all authenticated including no-profile, exact/case-normalized uniqueness/acronyms and concurrency final state. Requires PostgreSQL bounded races if guarantees claimed. |
| Q-FILTER | U:35–39 any whitelist substring bypass; U:60 undefined name; cleanup deletes linked records | Decide moderation/whitelist/false-positive policy and destructive cleanup semantics; unused helper repair/removal decision. Do not approve current bypass. |
| Q-VIS / Q-PROFILE | Rosters login-only; dashboard profile dereference; profile read side effects; public `/media/` core route | Approve roster fields/audience/mixed-role precedence, missing-profile lifecycle/response and media access; auth-only UI is not private-file enforcement. |
| Q-ADMIN | AD custom fields/permissions; unused form; hardcoded demo `/admin/` prefix versus configured ADMIN_URL | Verify Django admin ownership/role edit policy, missing-profile display, form commit behavior and demo prefix invariant. Core admin tests need demo boundary disabled; demo tests need it enabled. |
| Q-DEMO | demo/views:19 group query .first, no matching username/profile/roles check | Decide group trust/multiplicity/inconsistent seeded data behavior and content-type handling without allowing privilege escalation. Demo seeding itself is coordinator-owned; this domain supplies identity assertions only. |

Dependencies: coordinator chooses safe shared test settings and minimal factory
location; PARLEYPRO consumes shared ALL-role contract; PHILANTHROPY verifies its
own multi-role endpoint; NEWMEMBER owns redirect destination and check_user_role
policy integration; MISC supplies active announcement data; HOME owns navigation
and daylight helper behavior. Keep reusable business assertions in
`test/assertions.py`, with legacy HTTP assertions in test modules; future DRF
adapters reuse invariants rather than importing old response-specific assertions.
Proposed layout and commands are in [README.md](README.md). Do not implement
another shared harness locally.

## Actual checks and ordered Wave 2 checklist

Actual read-only checks: inspected `git rev-parse HEAD`, `git branch --show-current`,
AGENTS filename search, `rg` route/callsite/template/assertion searches and
line-numbered source reads. Reviewed only owned documentation edits. No app tests,
Django system checks, migrations, lint/type/coverage runs or PostgreSQL/storage
experiments were performed. Therefore all behavioral findings are source-derived;
no runtime crash, security exploit or transactional guarantee is claimed measured.

1. Coordinator verifies citations, inventory and case classifications; approves
   ordinary preserve candidates and assigns every F/Q decision an owner.
2. Agree safe shared settings/factories, role vocabulary, URLs/middleware modes,
   temporary media/clock helpers and reusable business assertion interface.
3. Add singular `test/__init__.py` and test modules in Wave 2; verify explicit
   `AUTHENTICATE.test` and app/default discovery; avoid conflicts with placeholder
   `tests.py` and do not silently remove existing assertions.
4. Implement P0 role/owner/CSRF/login redirect/password tests first, including
   no-profile/no-role/each narrow-role combination and two-user requests.
5. Implement ordinary profile/session/photo/major/roster cases with fresh ORM,
   session and file checks; separately specify legacy response adapters.
6. Implement fault injection at each User/profile/M2M/file boundary and true
   transaction tests after atomicity/compensation policies are chosen. Fix defects
   in separately authorized application changes, never make vulnerabilities pass.
7. Add isolated core admin, demo entry and demo prefix-blocking cases; sibling
   domains apply shared ALL-role checks to actual endpoints.
8. Run targeted new suites and coordinator baseline under approved isolated
   settings; run bounded PostgreSQL races only in suitable environment. Record
   actual commands/results and unresolved blocked cases, no coverage percentage
   without instrumentation.
