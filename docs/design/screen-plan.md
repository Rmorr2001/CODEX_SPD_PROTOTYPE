# SPD React screen plan

## Scope and current state

Baseline `dd4ac6d`: React has only a workspace and connection screen; the full
Django application still owns every business transaction. Implement the nine
concept screens below as working React read experiences under `/app/`, retaining
all original Django routes and mutations. Real APIs read the seeded database and
session. This increment may link explicitly to existing Django forms for writes;
it must not present a nonfunctional React form or simulated success as migrated.
No model/schema, domain-rule or permissions redesign is implied by generated art.

The [foundation](../migration/part-2-foundation.md),
[domain regression map](../testing/README.md) and
[demo lifecycle](../../SPDWEBAPP/railway_demo/README.md) remain authoritative.
Unresolved regression-policy cases stay unresolved; do not convert them into
new product promises. Railway/browser access is a separate verification concern.

## Screen, image and specification map

Each image is one three-panel board. Compare against the named panel only;
the board headings/captions outside the simulated browser are not page content.
Routes below are delivery contracts; the [delivery log](delivery-log.md) records
which have passed implementation and both reviews. Keep `/app/connection` and
the useful unknown-route screen.

| Order / screen | Proposed React route | Existing source / route | Image reference | Specification |
| --- | --- | --- | --- | --- |
| S01 Home | `/app/` | `HOME/views.py:home`, `HOME/home.html`; `/` | [Public board](references/public-pages.png), left “1. HOME” | [S01](screen-specs.md#s01-home) |
| S02 About & Brotherhood | `/app/about` | `HOME/views.py:ourHistory,executive_board`; `/ourHistory/`, `/executive-board/`, `/codeOfEthics/` | [Public board](references/public-pages.png), middle “2. ABOUT & BROTHERHOOD” | [S02](screen-specs.md#s02-about-and-brotherhood) |
| S03 Join / Recruitment | `/app/join` | `HOME/views.py:rush`; `/rush/` | [Public board](references/public-pages.png), right “3. JOIN / RECRUITMENT” | [S03](screen-specs.md#s03-join-and-recruitment) |
| S04 Member Dashboard | `/app/dashboard` | `AUTHENTICATE/views.py:dashboard`; `/auth/dashboard/` | [Member board](references/member-pages.png), left “1. DASHBOARD” | [S04](screen-specs.md#s04-member-dashboard) |
| S05 Member Directory | `/app/members` | `AUTHENTICATE/views.py:roster,alumni_roster`; `/auth/roster/`, `/auth/alumni_roster/` | [Member board](references/member-pages.png), middle “2. MEMBERS DIRECTORY” | [S05](screen-specs.md#s05-member-directory) |
| S06 My Profile | `/app/profile` | `AUTHENTICATE/views.py:profile` and its update endpoints; `/auth/profile/` | [Member board](references/member-pages.png), right “3. PROFILE” | [S06](screen-specs.md#s06-my-profile) |
| S07 Chapter Decisions | `/app/polls` | `PARLEYPRO/views.py`; `/poll/`, `/poll/past_polls/` | [Tools board](references/chapter-tools.png), left poll panel | [S07](screen-specs.md#s07-chapter-decisions) |
| S08 Service Hours | `/app/service` | `PHILANTHROPY/views.py,views_functions.py`; `/philanthropy/`, `/philanthropy/request/` | [Tools board](references/chapter-tools.png), middle service panel | [S08](screen-specs.md#s08-service-hours) |
| S09 New-member Marks | `/app/new-members` | `NEWMEMBER/views.py,views_functions.py`; `/newmember/marks/`, `/newmember/history/<user_id>/` | [Tools board](references/chapter-tools.png), right progress panel, adapted to marks | [S09](screen-specs.md#s09-new-member-marks) |
| A01 Sign-in / session boundary | `/app/login` or shared signed-out panel | `/auth/login/`, `/demo/enter/` | No supplied concept; derive from public shell | [A01](screen-specs.md#a01-session-and-access-states) |
| A02 Loading / empty / errors / missing page | Shared states and `/app/*` fallback | Existing foundation client and missing page | No supplied concept; use same design tokens | [A02](screen-specs.md#a02-shared-feedback-states) |

## Shared design and structure

- Deep red `#C51F32`, near-black `#111114`, white and pale neutrals. Use black
  public navigation, editorial serif headings, clean sans-serif body and controls.
  Member pages use a black navigation rail, red active item and white workspace.
- Use `ΣΦΔ` wordmark, chapter identity and repository-owned imagery. Do not copy
  generated faces, fabricated contact details, awards, schedules or statistics
  into authoritative content. Provide honest empty states when data is absent.
- Public header: Home, About, Join, Member workspace and original site. No dead
  philanthropy/calendar links; link a real destination or omit unsupported items.
  Member rail: Dashboard, Members, Profile, Polls, Service hours, New members;
  capability checks control visibility, with API enforcement behind them.
- Mobile stacks content at 390px with an accessible collapsible navigation or
  wrapping navigation; desktop target 1440px. No horizontal page overflow.
- Group frontend implementation by public site, identity, decisions, service
  and new-members, with README and singular `test/` where meaningful. Keep
  routing/shared composition in `src/app/`; backend adapters with their domain.
  Do not create nine artificial domains or one oversized “everything” service.

## API and permission boundaries

Delivered names below track the accepted screen implementations; remaining
contracts are proposed until their delivery-log gates pass. Add typed read-only
DRF adapters incrementally;
explicit serializers whitelist fields, JSON failures never turn into HTML or a
successful empty payload, personal/member responses use `Cache-Control: no-store`.
Existing `/api/v1/status/` remains unchanged. Preserve fail-closed API defaults.

| GET contract | Screen / owner | Permission and boundary |
| --- | --- | --- |
| `/api/v1/public/home/`, `/api/v1/public/about/`, `/api/v1/public/recruitment/` | S01–S03 / HOME | Public, only public banner/rush material, safe external links and public chapter/board fields; never serialize all profiles |
| `/api/v1/session/` | A01 / AUTHENTICATE | Minimal authenticated flag and, only for signed-in caller, own display name/roles and supported navigation capabilities; no session identifier or password |
| `/api/v1/dashboard/` | S04 / AUTHENTICATE + MISC | Authenticated; active announcements and configured DashboardLink entries; preserve new-member landing rule |
| `/api/v1/members/` | S05 / AUTHENTICATE | Authenticated; existing non-alumni/alumni sets, last-name order and distinct profiles; minimal name/roles/majors/image/pclass, no email/hometown by default |
| `/api/v1/profile/` | S06 / AUTHENTICATE | Authenticated, current user's profile only; no arbitrary target-user selector or hidden privileges |
| `/api/v1/polls/` | S07 / PARLEYPRO | Authenticated + ACTIVE; current poll, aggregate Aye/Nay and closed results; never individual voting identities |
| `/api/v1/member/service/` | S08 / PHILANTHROPY | Authenticated + ACTIVE; own events and approved academic-year total, validated year input; approval links require PHIL_CHAIR + ACTIVE |
| `/api/v1/member/new-members/` | S09 / NEWMEMBER | Authenticated; adapt existing role-specific read model without widening data. Personal new-member stats; ACTIVE analytics/submissions; NM_BOARD review capability. Unclassified roles get explicit unavailable state rather than invented privileges |

API wrappers must not invoke rendering views for their side effects or weaken
security to duplicate legacy accidents. Reuse read helpers when appropriate;
document narrower serialized fields. If a permission ambiguity prevents a safe
adapter, link the existing Django workflow and record the exact blocked contract.
`requires_role('A','B')` means **both** roles, not either. Roles such as
`PHIL_CHAIR` must use their real identifiers. No new auth mechanism is required:
reuse same-origin session cookies and legacy CSRF-protected sign-in/demo entry.
Logout must not be simulated by only clearing React state.

## Sequential agent loop and acceptance gates

1. Parent selects the next screen and hands builder the screen ID, spec anchor,
   image/panel, current source contracts, scoped files and explicit acceptance
   checks. First screen may establish shared tokens and public read model.
2. Builder implements real data/loading/empty/error behavior, tests meaningful
   behavior, and supplies changed files, commands/results and desktop/mobile
   screenshot paths. Every mutation retained in Django is visibly labeled as
   opening the existing form; no pretend React submit controls.
3. Reviewer independently reads diff and source rules, exercises positive and
   denied/failure cases, and returns `PASS` or `FAIL` with reproducible evidence.
   Reviewer checks inputs, output fields, role conjunctions and unchanged legacy
   workflows, rather than judging only happy screenshots.
4. Comparison agent opens the actual screenshot **and** referenced image panel.
   Returns `YEAH` or `NAH` with evidence against layout, red/black hierarchy,
   typography, contrast, responsive behavior and necessary rule-based deviations.
   It must not claim pixel similarity to generated content that was intentionally
   corrected. Screenshot provenance must state local fixture or live deployment.
5. On `FAIL`/`NAH`, builder fixes the concrete findings; re-run affected checks
   and both relevant reviews. Allow up to two correction cycles per screen.
   If a real blocker remains, record it and leave the screen unaccepted; do not
   silently move it to “done.” Parent may continue independent screens only.
6. Parent records each verdict, test evidence, screenshots and deviations in a
   delivery log, then commits the accepted increment. One screen at a time:
   S01, S02, S03, A01/S04, S05, S06, S07, S08, S09. Shared access states arrive
   before the first member screen, not as an afterthought.

For each accepted screen: deep link/refresh works; essential navigation/action
links work; real seeded data reaches the UI; no-data and denied/error states are
honest; keyboard focus and labels work; desktop/mobile screenshots are reviewed.
Record the distinction between **React read UI delivered**, **legacy write linked**
and **full transaction migrated**. This plan initially targets the first two.

Run TypeScript/build/format checks for frontend changes, owning-domain tests for
adapters and relevant Playwright checks against actual Django. Before completing
the sequence run the full regression audit, demo suite, required mutation gates,
schema validation and migration-drift checks from the existing testing docs.
Use synthetic fixture accounts and public assets only. Credentials never belong
in source, screenshots, docs or logs. Deployment is separate from local acceptance;
never claim live verification while the hostname is blocked by the cloud proxy.
