# HOME regression design — Wave 1.5

Historical design record; see [Wave 2 execution](README.md) and
[approved clarification](wave-2-findings.md#approved-semantic-clarification).

Source baseline: branch `prototype/railway`, commit
`7e25ac2f06b2d88a0220526771585f30df10c57a`.
Refinement baseline: `c8bbc4e94fdd135485c034981c0a25e09e902679`.
Repository: `Rmorr2001/CODEX_SPD_PROTOTYPE`, checkout `/workspace/CODEX-SPD-PROTOTYPE`.

Read root AGENTS.md, the [refinement prompt](../../../docs/testing/wave-1-5-agent-prompt.md)
and [shared fixture contract](../../../docs/testing/fixture-contract.md).
Only Markdown under HOME/test is changed. No application code, tests, configuration,
private data, credentials, network or Git state changed; no application tests ran.

Source citations are repository-relative; line numbers refer to the source baseline:

| Reference | Inspected source and relevant symbols |
| --- | --- |
| H1 | `SPDWEBAPP/HOME/urls.py:4–10`, five mounted paths; `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:23–45`, mounts and unconditional media serve |
| H2 | `SPDWEBAPP/HOME/views.py:8–61`, `home`, `ourHistory`, `codeOfEthics`, `rush`, `executive_board` |
| H3 | `SPDWEBAPP/HOME/models.py:3–32`, `BannerImage.save`, `RushFormLink.save`, `RushSlide.Meta` and strings |
| H4 | `SPDWEBAPP/HOME/admin.py:5–11`, default singleton registrations and `RushSlideAdmin(SortableAdminMixin)` |
| H5 | `SPDWEBAPP/HOME/templates/HOME/home.html:6–33,133–164`; `rush.html:14–36,78–131`; conditional assets, links, slide caption and client-only slideshow |
| H6 | `SPDWEBAPP/HOME/templates/HOME/ourHistory.html:12–17,27–55`; `codeOfEthics.html:5–30`; `executive_board.html:80–120`, board fields/fallback |
| H7 | `SPDWEBAPP/HOME/templates/HOME/main.html:8–20,27–44,54–70`, shared assets/demo include/escaped errors/messages; `navbar.html:13–30,43–76`, links and missing-profile-sensitive display |
| H8 | `SPDWEBAPP/AUTHENTICATE/models.py:58–95,129–138`, unique role names, nullable user/profile image, majors and ordered dashboard links |
| D1 | `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:16–29,35–70`, member list, atomic command and account checks |
| D2 | Same seed source `:73–91`, file copies and content upserts; `:94–114`, workflow samples |
| D3 | `SPDWEBAPP/railway_demo/urls.py:4`; `settings.py:8–18,24–40`, explicit config-path binding, isolated DB/media, WhiteNoise and context composition; `context.py:1–2`; `static_headers.py:4–7` |
| D4 | `SPDWEBAPP/railway_demo/README.md:31–58,64–89`, documented refresh/storage/source-tree contract; `tests.py:13–109`, existing assertions |
| T1 | `SPDWEBAPP/HOME/tests.py:1–3`, empty scaffold; `HOME/migrations/0001_initial.py:13–20`, `0004_rushformlink.py:12–19`, `0005_rushslide.py:13–24`, no singleton constraint |
| T2 | `requirements.txt:2,8`, Django and admin-sortable pins; `tools/file_tree/README.md:8–20,28–44`, separate tooling gate |

Supplementary read-only dependency inspection: installed `adminsortable2/admin.py` under the coordinator environment, `get_urls:166–174`, `update_order:242–258`, `_update_order:260–267`, `save_model:269–276`; no application execution. Installed behavior must be checked against the pinned dependency in Wave 2. It exposes `adminsortable2_update/`, accepts JSON `updatedItems: [[pk, order], ...]`, checks change permission, bulk-updates after looking up all rows, returns `Updated N items`, and converts caught errors to 400. The repository itself delegates these details; do not claim dependency internals as repository code.

No HOME forms, server-side JS actions, exports, custom sessions, custom audit models, standalone helpers or unmounted HOME views were found. The unused `requires_role`/`AnnouncementAlert` imports in H2 do not impose access checks. HOME template JS toggles content/slides without a backend write. Source explorer generation is separate tooling, not a new business-test family.

## Verified operation inventory

P = preserve observed non-harmful behavior; F = defect characterization plus proposed safety acceptance requiring an authorized fix; Q = business decision needed. P is a proposed contract pending coordinator verification, not automatic approval of all incidental source behavior. Routes have no explicit method decorator; POST/other methods currently render just as GET. Public read-side no-write behavior is preserved, while supported method policy is Q.

| ID | Route/action or callable | Actor and inputs | Observed response and effects | Class |
| --- | --- | --- | --- | --- |
| HOME-O01 | `/`, name `home`, `views.home` (H1/H2) | Anyone; optional query error | 200 HTML, first banner/link and profile queryset; no explicit writes/session changes | P/Q |
| HOME-O02 | `/ourHistory/`, `ourHistory` | Anyone | 200; distinct count of profiles with ACTIVE, including nullable-user profiles; no writes | P/Q |
| HOME-O03 | `/codeOfEthics/`, `codeOfEthics` | Anyone | 200 static ethics content/dashboard link; no writes | P |
| HOME-O04 | `/rush/`, `rush` | Anyone | 200 ordered slides/link; two inconsistent absent-link fallbacks; no writes | P/F/Q |
| HOME-O05 | `/executive-board/`, `executive_board` | Anyone | 200 cards in fixed nine-office order; each holder/office pair, no ACTIVE/EXEC filter; transient `position` attribute only | P/Q |
| HOME-O06 | `BannerImage.save` create/replace/update and delete (H3) | ORM caller; image, save options | Deletes every banner before base save; string is Banner Image; ordinary deletes have no custom storage cleanup | P/F/Q |
| HOME-O07 | `RushFormLink.save` create/replace/update and delete (H3) | ORM caller; URL, save options | Deletes every link before base save; string is link; no explicit validation/transaction | P/F/Q |
| HOME-O08 | `RushSlide` create/update/delete/order/string (H3) | ORM caller; image/caption/order | Standard persistence, indexed integer ordering only; caption string; no custom file lifecycle | P/Q |
| HOME-O09 | Django admin list/detail/add/change/delete for all three HOME models (H4) | Staff + model permissions; form/image/action/CSRF | Django admin responses, model save hooks and admin log entries; no HOME-specific auth logic | P/F |
| HOME-O10 | RushSlide admin sortable JSON and multi-page reorder actions (H4/T2) | Staff + change permission; `updatedItems`, action/selection/destination | Dependency reorder/bulk writes; normal admin add assigns max order + 1; no HOME audit override | P/F/Q |
| HOME-O11 | `call_command('seed_railway_demo')`, `Command.handle` (D1) | Local operator, DEMO_MODE; no custom options | Atomic DB transaction runs members→home→workflows; success text; refusal raises CommandError; files outside DB transaction | P/F |
| HOME-O12 | `seed_members()` (D1) | Internal callable, static MEMBERS | 12 users/profiles, role/major/group relations; stable group first user else username; refuses usable password/staff/superuser; no own atomic decorator or DEMO_MODE check | P/F/Q |
| HOME-O13 | `seed_home()` (D2) | Internal callable, media Path, source asset, domain | Copies two files unconditionally; only creates missing banner/link/slide; refreshes announcement/dashboard links, preserves existing daylight alert; no own transaction/guard | P/F/Q |
| HOME-O14 | `seed_workflows(users)` (D2) | Internal callable; ordered users, current clock | 9 hour records + votes; 4 marks; open/closed polls; matching rows refreshed; no own transaction/guard | P/Q |
| HOME-O15 | `/media/<path>` core serve + static composition (H1/D3) | Anyone; encoded/normalized path; local asset requests | Unconditional media routing even DEBUG=False, WhiteNoise static; absent files expected 404; no custom media auth | P/F/Q |
| HOME-O16 | Demo/public shell and explorer cache callback (H7/D3) | Anyone; context/query/messages, headers/path/url | Shared links/assets, demo banner include; callback sets no-cache only for explorer URL suffix | P/F |

Direct singleton model saves are not constrained at DB level; bulk_create/queryset.update can bypass hooks. Admin default transaction behavior must not be assumed for non-admin callers. Inventory includes callables because they are alternate entry points, not mounted public endpoints.

## Actor, role and ownership matrix

| Actor fixture | O01–05/15–16 public reads | O06–08 direct model calls | O09–10 admin | O11–14 seed |
| --- | --- | --- | --- | --- |
| Anonymous | Allowed; same public content | No route; internal callers have no user checks | Login redirect on isolated admin; demo blocking owned by AUTHENTICATE | No route; operator/internal entry only |
| Authenticated, roles=(), profile exists | Allowed | Same internal behavior | Nonstaff denied even with model permissions | Same |
| ACTIVE only; NEW_MEMBER only; ALUMNI only; EXEC only | Allowed for each separately | Same | Business roles confer no Django admin access | Same |
| PRESIDENT only; PHIL_CHAIR only; other single office | Allowed; office card membership requires that office only | Same | No implicit staff/model grants | Same |
| ACTIVE+EXEC; PRESIDENT+PHIL_CHAIR; ACTIVE+ALUMNI | Allowed; ACTIVE counts once; multiple office cards | Same | No implicit grants | Same |
| Authenticated without Brother_Profile | Allowed by view; shell fallback must be verified | Same | Independent Django permission rules | Seeding may create profile for allowed demo user |
| Owner/other actor viewing same target profile | Identical public board fields, no ownership filter | Global singleton operations, no owner concept | Model permissions apply globally; no object-owner gate | Only known sample lookup keys intended; unrelated rows must survive |
| Staff, no HOME permissions | Public same | Same | Site may admit; HOME view/add/change/delete and reorder denied as applicable | Staff collision must be refused |
| Staff with only view/add/change/delete permission (one each) | Public same | Same | Test each permission separately; view cannot reorder; add cannot change/delete; change cannot add/delete | Privileged collision refused |
| Synthetic superuser | Public same | Same | Allowed in isolated non-demo admin only | Collision refused; never create privileged demo fixture as a seed success case |

ALL/ANY role semantics do not apply to HOME: no role decorator wraps these public views. Do not infer HOME access from navbar visibility. Board role membership uses each named office independently; policy must decide whether ACTIVE or EXEC should additionally be required. Public disclosure of names, majors and user emails is current behavior and requires explicit privacy approval. Null-user profiles are supported by H8; compare empty/null email and missing majors. No audit/session mutations are authored by public views; CSRF token middleware and message consumption may alter request/session infrastructure, so compare business state and persona identity rather than insisting all session keys are byte-identical.

## Cases and readiness

[Case/status index and complete original-to-new mapping](case-index.md) contains
97 atomic cases from all 21 original groups: 63 READY, 6 NEEDS_FIX, 26 POLICY_BLOCKED, 2 INFRA_BLOCKED.

Detailed designs are grouped under [case files](case-index.md#cases).

## Fixture and status rules

Use the [shared contract](../../../docs/testing/fixture-contract.md) unchanged:
`make_user(username=..., roles=...)`, `make_profile`, `login_actor`, `csrf_client`,
`temporary_media`, `at_time`, `snapshot_scope` and `assert_unchanged`.
`password=None` is explicit for seed-eligible accounts. Use `business` settings for
HOME/admin tests and `demo` settings for composition; neither imports runtime secrets.
No local alternative harness is proposed. Synthetic images/static roots are local
fixture data; source-canary files never contain real secrets.

Each case names response and refreshed row/relation/file assertions. Session checks
compare actor identity, allowing message consumption and CSRF metadata changes.
Use TestCase normally, SimpleTestCase for pure headers, and TransactionTestCase for
commit/failure boundaries. Mock only injected storage/DB failures, never business logic.
Independent connections and bounded barriers on PostgreSQL are required for races.

READY means an unambiguous design expected to pass source, not execution or approval.
NEEDS_FIX names a concrete failing safety assertion. POLICY_BLOCKED takes precedence
when the outcome is undefined. INFRA_BLOCKED names a specific missing facility.
The shared harness prerequisite alone does not make a case INFRA_BLOCKED.

## Decisions

| Key | Classification / decision | Required resolution |
| --- | --- | --- |
| Q1 | Public board disclosure of names/majors/email (Q) | Approve fields and public audience; names are intentionally synthetic in fixtures |
| Q2 | Count null-user and mixed ACTIVE+ALUMNI profiles; office without ACTIVE/EXEC; same-office tie order (Q) | Confirm eligibility and deterministic ordering requirements |
| Q3 | Missing-link inconsistent placeholders and unsafe directly saved URL schemes (F/Q) | Choose disabled/hidden/fallback link and allowed schemes; retain escaping separately |
| Q4 | Empty file field rendering crash risk / missing image fallback (F/Q) | Specify safe page and fallback behavior for banner/slide/profile |
| Q5 | Read views accept unsafe methods absent decorator (Q) | Decide GET/HEAD-only behavior; no mutation permitted regardless |
| Q6 | Public media route even production DEBUG=False; symlink containment (Q/F) | Approve public upload visibility; reject containment escape if reproduced |
| Q7 | No storage cleanup/compensation; delete-before-save data loss (F/Q) | Approve retention and rollback-safe replacement/delete design; DB transaction alone is insufficient |
| Q8 | Hook bypass, save options, aliases and unguarded direct seed helpers (F/Q) | Define supported APIs and invariant enforcement boundary |
| Q9 | No singleton DB constraint and concurrent replacement policy (F/Q) | Choose serialization/conflict semantics plus PostgreSQL validation |
| Q10 | Arbitrary/duplicate/tied reorder values and audit behavior (Q) | Confirm accepted payload invariants, stable order and logging; verify dependency action payloads |
| Q11 | Seed refresh resets roles, photos, votes, dates and matching keys (Q) | Approve disposable demo reset contract, define ownership of reserved seed keys |
| Q12 | Media overwritten despite failed atomic command (F/Q) | Choose filesystem compensation and repeatability guarantees |
| Q13 | Group-first selection and ambiguous identity/caption/title matching (F/Q) | Define collision refusal and unique identity binding; avoid collateral writes |
| Q14 | Domain/media Path input assumptions (Q) | Define supported deployment config inputs without reading real values |


Q1–Q14 references in cases refer to the table above. Candidate outcomes must be resolved
before implementing blocked expectations. No crash, bypass, lost row or leaked file is
accepted as preservation behavior. Code fixes remain a separate authorized wave.

## Existing assertions and gaps

`HOME/tests.py:1–3` has no assertions. `railway_demo/tests.py:31–47` checks repeated
seed counts (12 profiles, 2 polls, 9 hours, 4 marks), unusable/nonprivileged users,
DEMO_MODE=False refusal and one staff refusal. It does not prove exact roles, stable
PKs, refresh semantics, storage compensation, late rollback or collision safety.
`railway_demo/tests.py:49–52` checks seeded public status codes and one home phrase;
it does not prove empty states, ordering, escaping, missing assets or disclosure policy.
No existing HOME admin/model/reorder/media-containment assertions were found.

Existing demo `tests.py:54–109` additionally checks login redirects, privileged-persona browsing, some role redirects, entry method/persona/CSRF/non-demo/staff denial, profile update, one vote and philanthropy request. These remain useful integration assertions, not proof of narrowly assigned role policy or comprehensive workflow correctness. D01 entry/admin-blocking expansion belongs to AUTHENTICATE; C02/C03 non-HOME business rules stay with owners.


## Wave 2 order and verification limits

1. Verify source evidence and resolve Q1–Q14, beginning with data loss and disclosure.
2. Implement shared fixtures/settings centrally; create singular test package and
   verify targeted/app-label discovery without losing existing railway_demo tests.
3. Implement READY cases with fresh ORM/file assertions and narrow role fixtures.
4. Resolve POLICY_BLOCKED cases; authorize fixes separately for NEEDS_FIX cases.
5. Supply browser/static integration and PostgreSQL facilities before infra cases.
6. Run targeted HOME and existing demo suites; report actual results separately.
7. Keep file-tree generator checks as a separate tooling gate, not business coverage.

Documentation validation only: case IDs/names, parent/operation completeness, metadata,
status counts, local links and whitespace. No app tests or proposed cases were run.
