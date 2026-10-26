# Chapter decisions

Owns `/app/polls` and `/app/polls/:id`: same-model current/historical results,
caller choice, Aye/Nay writes, executive creation/closure and discreet legacy access through the member shell.
`content.ts` validates snapshots; `useLiveDecisions.ts` refreshes every three
seconds while visible, without clearing active controls. `PollActions.tsx` owns
pending/error states and never automatically retries a mutation.

The global legacy ballot store supports one open motion. Both interfaces share
PARLEYPRO operations; no per-poll ballot model or independent concurrent polls
are introduced. Closed results use saved totals; voter identities stay private.
See [PARLEYPRO](../../../../SPDWEBAPP/PARLEYPRO/README.md) for authorization,
atomic transitions, conflicts and server tests. No new configuration keys.

`test/decisions.spec.ts` retains read/access/error coverage. Cross-interface
transaction coverage is in `frontend/test/zz-transactions.spec.ts`: confirmed React votes before refetch,
legacy vote change, live result refresh, closure and saved-result navigation.
Run the production build and Playwright per root frontend README.

The quiet utility layout places results and voting in one Card; past results
remain below it. There are no motion-detail links or explanatory side rails.
Button/Card primitives use Tailwind; the superseded decisions stylesheet is
removed. The shared lifecycle refreshes without unmounting active controls and
immediately merges confirmed ballot snapshots. Direct detail URLs still work.
See the root experience plan for state tradeoffs and selected visual work.

Votes select and preview this caller's tally immediately; Saving remains visible
until the matching database-backed response. `useOptimisticBallot` serializes
writes and coalesces rapid changes to the latest choice, preventing out-of-order
server writes. Only the latest acknowledged intent gets Saved. Failures roll back
the preview, show Not synced and offer explicit retry when safe; denied/closed
polls reconcile without an unsafe retry. No mutation auto-retry is introduced.

Confirmed data stays separate from the pending display. Read revisions prevent
responses started before an acknowledgement from overwriting it. Unchanged JSON
snapshots keep state, controls and focus stable; tally transitions respect reduced
motion. `test/interaction.spec.ts` covers layout/refresh and
`test/optimistic.spec.ts` holds real writes to observe pre-ack selection, queued
intent, persistence, failed rollback/retry, stale reads and closed/session denial.
One write round trip is still required for database confirmation; this is not
instant networking or independent concurrent polls.

A transport timeout can leave persistence uncertain; the client reports Not synced,
reconciles current records and never fabricates a database failure or auto-retries.
