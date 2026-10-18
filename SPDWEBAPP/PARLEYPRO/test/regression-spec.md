# PARLEYPRO regression specification

Wave 1.5 design only; coordinator source verification and policy resolution precede Wave 2.
Repository: `Rmorr2001/CODEX_SPD_PROTOTYPE`; branch: `prototype/railway`.
Source baseline: `7e25ac2f06b2d88a0220526771585f30df10c57a`.
Documentation-refinement baseline: `c8bbc4e`, confirmed as current HEAD during refinement.

[Case index, status counts and complete old-to-new mapping](case-index.md) replaces the
40 dense original groups with 114 independent designs: 58 READY, 5 NEEDS_FIX,
48 POLICY_BLOCKED and 3 INFRA_BLOCKED. None have been executed or declared approved.

## Reading and fixture contract

Use the coordinator-owned [shared fixture contract](../../../docs/testing/fixture-contract.md).
Identity factories are `make_user(*, username, roles=(), with_profile=True, ...)`
and `make_profile(user, *, roles=(), **profile_fields)` with the exact full signatures
in that contract. Use `login_actor`, `csrf_client`, `at_time`, `snapshot_scope` and
`assert_unchanged`; no parallel shared helper interface is proposed here.

Domain setup is thin real ORM construction with explicit creator, start/end/counts and
current choice. No implicit demo personas, role hierarchy, media or historical ballots.
Refresh named rows after actions and compare PKs/ownership and unchanged fields, not only
HTTP flags. Keep state assertions reusable outside legacy 200/302/template/JSON adapters.
Denied requests can add messages or rotate CSRF metadata; preserve session identity rather
than requiring identical session bytes. Public polling has no file or audit writes;
permitted admin CRUD has framework LogEntry effects specified in the admin cases.

READY means an unambiguous design expected to pass source after the ordinary shared
harness exists. NEEDS_FIX specifies a concrete safety defect. POLICY_BLOCKED means the
expected contract still needs a named decision, even if infrastructure/fixes are also
missing. INFRA_BLOCKED means clear expectations need a case-specific facility.
Preserve/defect/decision classifications below remain separate from readiness labels.

## Source evidence

All paths are repository-relative. `P/` abbreviates `SPDWEBAPP/PARLEYPRO/`.
Root `AGENTS.md`, Wave 1/1.5 prompts and fixture contract were read; no nested guidance
was found. Source inspection and Markdown validation are the only checks run by this agent.

| Source | Verified evidence |
| --- | --- |
| `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:23–34` | Configured admin prefix and `/poll/` mount. |
| `P/urls.py:4–13` | Four mounted views; duplicate identical live path/name at 8 and 11. |
| `P/views.py:15–34` | ACTIVE page, current poll selected before POST, post-action global counts. |
| `P/views.py:35–50` | Login then ALL EXEC+ACTIVE; form validation, creator binding, save, redirect. |
| `P/views.py:51–68` | ACTIVE closed history sorted by end; login-only global JSON counts. |
| `P/pp_functions.py:11–14` | Exact literal counts on supplied manager/queryset, tuple Aye/Nay. |
| `P/pp_functions.py:16–41` | EXEC error does not return; newest-open save then global reset. |
| `P/pp_functions.py:45–72` | Start-first, then end, else own row; Nay save before Aye save. |
| `P/pp_decorators.py:7–52` | ALL roles, profile requirement, raw Referer/fallback redirects. |
| `P/models.py:12–24` | Nullable aggregates/end; creator CASCADE; auto-add start; OneToOne choice. |
| `P/forms.py:5–14` | Name-only ModelForm, required/max 200, standard stripping/widget. |
| `P/admin.py:8–35` | Only Vote_Poll registered; default CRUD, icon and Yes-count sort metadata. |
| `P/migrations/0005_vote_poll.py:16–25` | Poll migration agrees with current model definition. |
| `SPDWEBAPP/AUTHENTICATE/models.py:58–79,88–95` | Unique named roles, profile/user and roles M2M. |
| `P/templates/create_poll.html:11–24` | Name POST, CSRF hidden token and field errors. |
| `P/templates/poll_index.html:9–10,22–42` | Create link, open-poll buttons, no EXEC close hiding. |
| `P/templates/poll_index.html:49–64,85–155` | Conditional bars; localStorage and 1500ms live timer. |
| `P/templates/past_polls.html:14–54` | Stored aggregates, creator, Chicago dates, zero/empty states. |
| `SPDWEBAPP/railway_demo/middleware.py:9–12` | Public demo blocks /admin/ separately from domain permissions. |

Both inspected settings modules use SQLite; core settings include CSRF/auth/messages
middleware (`SPDWEBAPP/SPDWEBAPP_CORE/settings.py:95–100,126–131`). Demo settings use
its separate SQLite DB and login URL (`SPDWEBAPP/railway_demo/settings.py:24,28–32`).
No ATOMIC_REQUESTS occurrence was found there. No helper transaction/lock/open-poll
constraint exists. Neither source inspection nor SQLite establishes concurrency safety.

All four views are mounted. Commented logout routes/old model comments are unsupported.
The hidden `start_vote` POST branch is reachable but unused by UI navigation and discards
its redirect. Brother_votes is one current per-user choice without a poll FK: no individual
historical ballots exist. Raw ORM save can bypass full_clean; corruption fixtures say so.
No session writes beyond messages, upload, export, file storage or domain audit model exists.
Browser localStorage is independent of server session state.

## Operation inventory and completeness

P = preserve; D = defect; Q = decision needed. P0 security/integrity, P1 core, P2 presentation.
Inputs, outputs and effects are detailed in linked cases, which map each ID in metadata.

| Operation | Route/callable and actor | Response / state effect | Class | Case workflow |
| --- | --- | --- | --- | --- |
| PP-V01-FORM | GET /poll/start_vote/; EXEC+ACTIVE | 200 unbound name form; no writes | P | [Creation](cases/creation.md), [access](cases/access.md) |
| PP-V01-CREATE | POST same; name; EXEC+ACTIVE | 302 new actor-owned open poll; invalid 200/no write | P/Q | [Creation](cases/creation.md), [access](cases/access.md) |
| PP-V02-DISPATCH | POST /poll/; action keys; ACTIVE | Start/end/choice branch; 200 render; mixed keys ambiguous | D/Q | [Voting](cases/voting.md) |
| PP-V02-CAST | aye/nay branch; ACTIVE | Own current row create/change; no poll association | P/Q | [Voting](cases/voting.md), [failures](cases/failures-and-races.md), [model](cases/model-boundaries.md) |
| PP-V02-COUNT | count_all_current_votes(scope) | (Aye,Nay), exact literals, no writes | P/Q | [Voting](cases/voting.md), [races](cases/failures-and-races.md) |
| PP-V03-CLOSE | end_vote/helper; intended EXEC+ACTIVE | Save totals/end then reset current rows; not atomic | P/D/Q | [Closure](cases/closure.md), [failures/races](cases/failures-and-races.md), [access](cases/access.md) |
| PP-V04-PAGE | GET /poll/; ACTIVE | Latest open poll and live counts; stale post-close context | P/D/Q | [Reads](cases/reads-and-routes.md), [closure](cases/closure.md) |
| PP-V04-HISTORY | GET /poll/past_polls/; ACTIVE | Closed polls, descending end, all creators; no writes | P/Q | [Reads](cases/reads-and-routes.md), [access](cases/access.md) |
| PP-V04-LIVE | /poll/poll-results/; logged in | Integer global JSON; audience/scope decision; no writes | P/Q | [Reads](cases/reads-and-routes.md), [browser](cases/browser.md) |
| PP-V04-ROUTES | Four named routes; resolver/methods | Duplicate live entry; unsupported methods fall through | P/D/Q | [Routes](cases/reads-and-routes.md) |
| PP-C03-READ | Poll admin; staff/model permissions | Changelist/detail, result sorting; no writes | P | [Admin](cases/admin.md) |
| PP-C03-WRITE | Admin CRUD; staff/action permissions | Default edit/delete and LogEntry, no close/reset hooks | P/Q | [Admin](cases/admin.md), [retention](cases/model-boundaries.md) |
| PP-C03-ICON | poll_result_icon(obj) | Safe Passed/Failed/Tied HTML; NULL comparisons crash | P/D/Q | [Admin](cases/admin.md), [tie policy](cases/closure.md) |
| PP-SHARED-ROLE | requires_role(*names); consumers | ALL roles/profile/messages; unsafe raw Referer/fallback | P/D | [Route access](cases/access.md); shared suite AUTHENTICATE-owned |

Shared callable behavior and fixtures remain
[AUTHENTICATE-owned](../../AUTHENTICATE/test/regression-spec.md). PARLEYPRO owns only
route-level role integration and poll helper contracts, not another shared decorator suite.

## Role and ownership matrix

Successful unsafe actions additionally require CSRF. Extra unrelated roles do not revoke
access; EXEC never implies ACTIVE. Staff/model permissions are independent of domain roles.

| Actor | Page/cast/history | Create | Live observed | Close desired / observed | Business admin |
| --- | --- | --- | --- | --- | --- |
| Anonymous | Login redirect | Login + next | Login + next | Deny / denied | Login boundary |
| Authenticated, no profile | Profile denial | Profile denial | Allow, POL-03 | Deny / denied | Staff/perms only |
| Roles (); ALUMNI; NEW_MEMBER; PHIL_CHAIR | Deny | Deny | Allow, POL-03 | Deny / denied | Staff/perms only |
| EXEC only; EXEC+ALUMNI | Deny | Deny: ACTIVE missing | Allow, POL-03 | Deny / denied | No implied grant |
| ACTIVE only; ACTIVE+ALUMNI | Allow | Deny: EXEC missing | Allow | Deny / **currently closes** | No implied grant |
| EXEC+ACTIVE; pair+ALUMNI | Allow | Allow | Allow | Allow; creator policy POL-04 | No implied grant |
| Superuser, no profile/roles | Deny | Deny | Allow, POL-03 | Deny / denied | Django superuser |
| Active staff with poll permissions | Domain rules | Domain rules | Login rule | Domain rules | Corresponding permission |
| Inactive staff | Login/session boundary | Login/session boundary | Login boundary | Deny | Deny |

Casting binds request.user and ignores forged user/poll/choice fields. Creator/start/end/
counts cannot be spoofed through the create form. Current/history pages have no creator-only
filter. Properly authorized cross-creator close is observed but awaits POL-04 approval.
Direct close helper lacks the request role boundary and crashes without a profile; its
supported callable authorization contract is unresolved, not an approved bypass.

## Defects and open decisions

| ID | Source-backed finding / required resolution |
| --- | --- |
| DEF-01 P0 | `pp_functions.py:27–41`: ACTIVE non-EXEC error then save/reset. Stop before writes. |
| DEF-02 P1 | `pp_functions.py:52–53`: discarded start redirect; reject/remove or navigate safely. |
| DEF-03 P0 | `pp_functions.py:24–41`: nonatomic totals/end/reset, stale-close races, no locks. |
| DEF-04 P1 | `admin.py:21–25`: NULL aggregate comparisons crash; display/repair policy needed. |
| DEF-05 P0/P1 | `pp_decorators.py:26–48`: raw Referer and denied-poll loop; AUTHENTICATE dependency. |
| DEF-06 P2 | `views.py:22–34`: preselected poll remains current in post-close response. |
| DEF-07 P2 | `poll_index.html:49–64,114–147`: missing bars dereferenced by live updates. |
| DEF-08 P2 | `urls.py:8,11`: duplicate identical live route; retain supported path once. |
| POL-01 | Single-open invariant, target identity, no-open casts, residual choices and retry targets. |
| POL-02 | Mixed/unknown action rejection or priority, default No Vote side effect, create replay. |
| POL-03 | Login-only live audience; eligibility of roles/orphans; count/reset/no-open scope. |
| POL-04 | Chapter-wide versus creator-only close; direct-helper and admin creator boundaries. |
| POL-05 | Tie/zero business result, quorum/majority; icon alone is not adjudication. |
| POL-06 | Atomicity/recovery, late-vote acceptance, coherent snapshot, loser response, retry/errors. |
| POL-07 | Equal start/end ordering: explicit tie-break or intentionally unordered equivalent items. |
| POL-08 | Allowed methods and future transport; do not infer write semantics from fallthrough. |
| POL-09 | Admin edits/reopen/negative or NULL counts, poll/user deletion retention, audit requirements. |

READY cases do not bless known unsafe behavior. Policy cases state candidate outcomes and
safety invariants without pretending an exact transport/retention rule is already settled.
Partial failures use real autocommit transactions and named injected boundaries. PostgreSQL
races use distinct connections/clients and bounded synchronization, never SQLite claims.
Browser cases name the missing runner/timer/fetch interception facility explicitly.

## Existing coverage and proposed implementation

`P/tests.py:1–3` contains no test methods. `SPDWEBAPP/railway_demo/tests.py:58–67` checks
executive polling GET 200/current name; `:99–104` checks ACTIVE Aye response and own row;
`:31–40` checks seeded poll count. No close, fine-grained denial, count, admin or race
assertions were found there. Existing tests were inspected, not run by this agent.
The coordinator owns baseline execution. No numerical coverage percentage is claimed.

Proposed Wave 2 files under singular `test/`: `__init__.py`, `assertions.py`,
`test_creation.py`, `test_access.py`, `test_votes.py`, `test_closure.py`,
`test_reads.py`, `test_admin.py`, `test_models.py`, `test_transactions.py`.
`assertions.py` holds domain state assertions; shared helpers remain in the coordinator's
`SPDWEBAPP_CORE/testing/`. Ordinary cases use TestCase, pure icon formatting SimpleTestCase,
and failure/race schedules TransactionTestCase. Browser implementation awaits its runner.

1. Verify citations, shared fixture contract, readiness and all 40 parent mappings.
2. Add singular package/discovery; verify explicit-package and app-label discovery.
3. Implement READY creation, role, CSRF, own-choice and read designs with shared fixtures.
4. Fix unauthorized close and shared redirects separately; then implement NEEDS_FIX targets.
5. Resolve dispatch/open-poll/eligibility/ownership/transport policy before blocked assertions.
6. Define close recovery/linearization; implement transaction faults and PostgreSQL races.
7. Resolve admin lifecycle/retention; implement C03 without disabling demo boundary globally.
8. Add browser runner, fix live DOM behavior, and implement browser cases.
9. Run scoped and integration checks when implementation is authorized; record exact backend,
   commands and results, and update readiness without claiming unexecuted designs passed.
