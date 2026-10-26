# React experience: live data, less copy and UI migration

This is local work after fedf8e9; it is not a published redesign. The user selected
A's quiet utility structure and C's service quick-entry drawer. Existing real
Django models, domain operations, session/CSRF boundaries and legacy routes remain
shared. Parent coordination owns the image concepts and release.

## Current architecture and implemented local changes

Before this pass: React19/Vite8/TypeScript7 with hand-written CSS; no Zustand,
Tailwind or shadcn. Polls fetched every5seconds; service reads only loaded on
mount. Most successful mutations refetched whole views, producing loading gaps.

- Both motion-detail links and the explanatory poll rail are removed. Polls keep
  the motion, choices, selected vote, counts and authorized create/close controls.
- Ornamental eyebrows, repeated slogans and explanatory paragraphs are trimmed
  across member/public pages. Essential labels, errors, data, dates, roles and
  mobile table/accessibility hints stay. Legacy navigation is discreet.
- One shared read hook owns bounded request timeout/cancellation, live refresh
  and invalidation. Visible poll/service views refresh at most every3seconds and
  on focus/visibility return. Hidden views do not poll. Requests do not overlap.
- Successful writes notify mounted views and same-origin tabs without sending
  member data. Confirmed poll responses update choice/tallies immediately; chair
  decisions remove confirmed queue items immediately. Other sessions reconcile
  through server reads. This is bounded polling, not push/SSE/WebSocket realtime.
- Background transport failure retains the last confirmed data with a short
  paused status. Authentication/permission denial clears protected data. Changing
  query/year clears the old query's values. Mutations are never auto-retried.

## State recommendation

Zustand is not installed. It can coordinate transient drawer/navigation state if
multiple distant controls need it, but it cannot synchronize independent users or
replace Django's authorization/data source. Current route-local state plus the
shared query lifecycle is proportionate. Avoid duplicating server responses in
both a store and separate hooks. Consider a dedicated query cache if concurrent
consumers/deduplication become a demonstrated need; this pass has no global
persistent member-data cache or optimistic unconfirmed success.

## Tailwind/shadcn foundation

Installed exact Tailwind4.3.3 and its Vite plugin; registry peer metadata supports
Vite8. Added standard @ aliases, components.json scaffold destinations, clsx2.1.1,
tailwind-merge3.7.0 and the cn helper. No generated shadcn primitives are installed
yet, and the existing pages have not been restyled as those components.

Tailwind scans only components/ui; Preflight is omitted so existing CSS does not
reset. Semantic red/black/neutral variables are opt-in beneath .spd-ui, avoiding
collisions with existing domain tokens. The starter components.json is scaffold
configuration, not a selected visual preset applied to the app. Before generation,
review generated styles/dependencies and the chosen references.

Sources: [Tailwind Preflight and selective imports](https://tailwindcss.com/docs/preflight),
[shadcn existing Vite setup](https://ui.shadcn.com/docs/installation/vite),
[components configuration](https://ui.shadcn.com/docs/components-json).

## Selected implementation increments

1. Finish verification of the cleanup, state lifecycle and foundation. Add tests
   for confirmed updates before refetch, cross-session service/poll updates,
   background-error retention and denied-data clearing.
2. Inspect the actual A/C image pixels in this consumer, then implement the compact
   crimson/dark sidebar and a single poll card with tally and ballot. Keep past
   results restrained and one discreet contextual Legacy entry. Preserve mobile
   navigation, contrast, focus visibility and role-authorized actions.
3. Add a shadcn/Radix Sheet for service quick entry, with existing Event, Date and Hours fields,
   Submit/Cancel. Reuse the shared service form and API. Trap/return focus, support
   Escape/Cancel, confirm dirty dismissal, protect pending submission, and retain
   input on errors. Keep the direct full-page URL working as a fallback.
4. Notes were an image-concept suggestion, not an approved business-field addition.
   Do not render or persist Notes in this iteration. Any later user-requested
   expansion must define storage/validation/privacy and legacy/API round trips.
5. Verify selected visual structure against reference pixels and local screenshots,
   run transactions/mobile/drawer tests and a built-image check, then return the
   bounded diff for parent-managed publication. Do not change polling eligibility,
   self-review/reversal policy, account/marks business scope or real databases.

## Reference-materialization boundary

Requested A: libfile_2a284e52d2408191ac5ab3e1ffc7982b (A-quiet-utility.png).
Requested C: libfile_43a3c6c0dc28819197c213498e5c0e48 (C-action-workspace.png).
This consumer's available skill catalog has no Library skill, and its tool catalog
has no standalone Library resolve/materialize operation. Page file reads require
an accessible Page ID plus an observed Page reference, neither supplied for these
files. download_file accepts Sediment file IDs only, not Library IDs. Parent paths
are not assumed accessible. Exact pixel matching is not claimed and dependent
visual implementation waits for a supported authorized transfer/read route.


## Bounded release evidence

The completed cleanup/refresh/foundation is independently releasable while A/C
reference transfer is resolved. Production TypeScript/Vite, formatting, diff and
source sizes passed. All50Playwright checks passed once against the synthetic
server and once against the locally built Docker image. The first concurrent
server run had an artifact ENOENT because both runners shared the output folder;
a separate-output full rerun passed. See [verification](react-experience-next-verification.json).
No backend/schema/permission changes were made; the prior497-test backend audit
is applicable and is not claimed as rerun. No drawer, Notes field, Zustand store
or generated shadcn primitive is claimed by this bounded release.

Supported consumer inputs are a genuine Sediment upload ID for download_file,
or actual authorized bytes/files/ref materialized locally then inspected with
view_image. An explicitly supplied authorized Git ref containing the images can
be fetched and its blobs written to consumer-local paths before inspection.
Library IDs cannot be converted into Sediment IDs; no guessed URLs, unrelated
Page reads, or assumed parent filesystem paths are used.
