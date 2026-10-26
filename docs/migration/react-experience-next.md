# React experience: live data and quiet utility UI

The user selected A's quiet utility structure with C's service quick-entry drawer.
This iteration follows the parent's inspected visual specification. The original
A/C Library PNGs were not materialized in this executor, so exact pixel fidelity
is not claimed. Local rendered screenshots were inspected; parent compares the
live result with the authoritative concepts. No image assets, accounts or services
were provisioned to work around the transfer boundary.

## Implemented scope

- Shared member shell: 260px charcoal sidebar, crimson identity/active row,
  off-white canvas, compact navigation, discreet Legacy view. Mobile uses a
  modal navigation Sheet. Public marketing retains its layout.
- Polls: one white bordered Card holds title/status, Aye/Nay counts/percent/bars,
  selected vote, ballot choices and authorized Close poll. Past results stay below;
  no motion-detail links, slogans or explanatory rail. Direct detail routes work.
- Service: Log service opens a right-side Sheet with existing Event/Date/Hours,
  Submit/Cancel. No Notes field or schema expansion. Shared fields and submission
  hook serve both Sheet and direct full-page create/edit URLs.
- Real Radix Dialog owns focus trap/return and modal semantics. Dirty dismissal
  and Back require confirmation; pending writes block dismissal/duplicate submit.
  Errors retain fields; success closes and resets the form. Narrow screens use
  full-width Sheet. The draft survives background resource refreshes.
- Shared Django models, operations, permissions, API/HTML route separation,
  fractional storage and audit history are unchanged. Marks/profile mutations
  remain explicit legacy handoffs; this UI release does not migrate them.

## State and synchronization

No Zustand: local draft/menu state and shared query lifecycle are proportionate.
A store would not synchronize users. Confirmed poll responses update choice/tallies
immediately and chair decisions remove confirmed queue items. Successful writes
invalidate mounted/same-origin-tab reads without broadcasting member data.
Visible poll/service views reconcile every three seconds and on focus; hidden
views pause. Background transport failures retain confirmed data; denied access
clears protected data. Queries cancel obsolete requests and do not overlap.
Mutations never auto-retry. This is bounded polling, not push realtime.

## Tailwind/shadcn migration

Tailwind4.3.3/Vite plugin, aliases, components.json, clsx and tailwind-merge are
installed. This increment adds reviewed local shadcn-style Button/CVA+Slot, Input,
Card, MemberShell and Radix Sheet primitives. Exact new dependencies:
@radix-ui/react-dialog 1.3.1, @radix-ui/react-slot 1.5.0,
class-variance-authority 0.7.1. The canonical Dockerfile/Railway config is unchanged.
Preflight is omitted; scanning is limited to UI and migrated domain sources.
Semantic tokens live under .spd-ui, including portal content. Generic anchor and
button defaults use the base layer so utilities can override them.

React Router now uses createBrowserRouter/RouterProvider to support useBlocker;
existing App route declarations, basename, deep links, authentication and native
POST logout remain. Subsequent domain CSS migrations can proceed separately;
this is not a claim that every page now uses shadcn primitives.

## Verification and preview

See [this iteration's evidence](quiet-utility-verification.json). Domain-local
service/test/quick-entry.spec.ts covers desktop1536px/390px, focus trap/return,
dirty cancellation, Back/Forward/reopen, failed refresh preservation, validation
errors, busy dismissal and duplicate-write protection. Existing suites continue
cross-interface voting/close/results, fractional service/approval/history/export,
role denial, self-review affordances and all member/public reads.

To preview a production bundle with an isolated fictional database:

```sh
npm ci --prefix frontend
npm run build --prefix frontend
FRONTEND_TEST_PORT=8000 .venv/bin/python tools/testing/serve_frontend.py
```

Open http://127.0.0.1:8000/app/login in the runtime browser, enter a fictional
persona, visit Polls, then Log service. The loopback URL is runtime-local, not a
public preview. The runner migrates/seeds synthetic SQLite/media and removes them
on exit. Browser commands and Docker checks are documented in frontend/README.md.
The previously published cleanup evidence remains in
[its historical report](react-experience-next-verification.json).
