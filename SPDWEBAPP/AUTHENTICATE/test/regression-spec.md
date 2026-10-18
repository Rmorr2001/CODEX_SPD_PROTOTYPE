# AUTHENTICATE regression specification — Wave 1.5

## Evidence and status

Inspected local branch `prototype/railway`, commit
`7e25ac2f06b2d88a0220526771585f30df10c57a` in
`/workspace/CODEX-SPD-PROTOTYPE` (repository `Rmorr2001/CODEX_SPD_PROTOTYPE`).
Read the complete [shared contract](../../../docs/testing/wave-1-agent-prompt.md)
and root [AGENTS.md](../../../AGENTS.md); a filename search found no nested
AGENTS.md in this checkout. This is inspection evidence, not execution evidence.
Behavior source baseline remains the commit above; documentation refinement
baseline is `c8bbc4e`. No app tests, network, installs, Git mutations or code
changes were performed by this agent. Shared execution belongs to the coordinator.

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

## Reading and readiness

Inventory shorthand: P means preserve candidate, F means source defect, and Q
means unresolved policy. These are source classifications, not case statuses.
Case statuses below separate preservation from defects and policy explicitly.

Detailed atomic cases are in the [case index](case-index.md), with all 55 original
parents mapped to suffixed IDs. Index counts describe designs, not passing tests.
Each case has one primary status: READY, NEEDS_FIX, POLICY_BLOCKED or INFRA_BLOCKED.
READY excludes unresolved policy/defect dependencies. Ordinary shared-harness
availability is common to READY; extra PostgreSQL/browser facilities are listed
on the relevant blocked cases. Policy takes precedence when outcomes are undefined.

Use real ORM TestCase, SimpleTestCase for pure helpers and TransactionTestCase for
commit/rollback behavior. Mock only deliberate storage/DB faults, never business
operations. Keep business invariants separate from legacy response adapters.
No HTTP exception/crash, authorization bypass or data loss is a passing contract.

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

## Fixture contract and isolation

Adopt the [coordinator fixture contract](../../../docs/testing/fixture-contract.md)
without independent factory/settings proposals. The [workflow legend](fixture-notes.md)
defines fresh named A/B/N actors and synthetic files. The contract defines make_user with explicit
username, make_profile with roles, login_actor, csrf_client, temporary_media,
at_time and scoped snapshots. Infrastructure does not exist yet.

Use business mode for real admin and demo mode for persona/boundary checks.
Identity fixtures explicitly include A/B targets, no-profile N, roleless Z,
all narrow role combinations above, inactive users, nonstaff domain executives,
permission-bearing staff and superusers without app roles. Orphan/invalid-role
setup intentionally uses direct ORM, bypassing fixture validation. Default fixtures
have no images or majors. Thin domain-local constructors create explicit majors,
synthetic Pillow bytes, persona groups and MISC announcement fixtures.

[Decisions and defects](decisions.md) retain policies and source references.
AUTHENTICATE owns the shared ALL-role sentinel contract;
[PARLEYPRO](../../PARLEYPRO/test/regression-spec.md) owns mounted-route integration.
PHILANTHROPY owns its own multi-role endpoints; NEWMEMBER owns redirect destinations;
MISC/HOME own announcement/daylight behavior. No numerical coverage claim is made.

## Existing assertion evidence

| Operation | Original groups (mapped in case index) | Existing source assertions (not executed here) |
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

See [case index](case-index.md) for complete old-to-new mapping and new status counts.

## Actual checks and ordered Wave 2 checklist

Actual read-only checks: inspected `git rev-parse HEAD`, `git branch --show-current`,
AGENTS filename search, `rg` route/callsite/template/assertion searches and
line-numbered source reads. Reviewed only owned documentation edits. No app tests,
Django system checks, migrations, lint/type/coverage runs or PostgreSQL/storage
experiments were performed. Therefore all behavioral findings are source-derived;
no runtime crash, security exploit or transactional guarantee is claimed measured.

1. Coordinator verifies citations, inventory and case classifications; approves
   ordinary preserve candidates and assigns every F/Q decision an owner.
2. Implement the agreed fixture contract and business/demo settings modes;
   verify isolation, role vocabulary, temporary media and actual consumed clocks.
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
