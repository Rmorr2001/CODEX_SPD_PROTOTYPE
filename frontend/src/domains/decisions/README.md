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

Interaction follow-up: unchanged validated JSON snapshots keep the same read
state; automatic retries retain failed states until recovery. Ballot feedback
uses reserved space and preserves the confirmed selection while a write is pending
or fails. A synchronous in-flight guard prevents repeated clicks from sending
concurrent votes. Tally widths transition briefly with reduced-motion support.
`test/interaction.spec.ts` observes DOM/focus/layout across held/unchanged reads,
failed background retries and duplicate held writes. These are concrete local
regressions; they do not establish every reported live flashing symptom reproduced.
