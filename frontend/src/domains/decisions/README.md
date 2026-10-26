# Chapter decisions

Owns `/app/polls` and `/app/polls/:id`: same-model current/historical results,
caller choice, Aye/Nay writes, executive creation/closure and explicit legacy links.
`content.ts` validates snapshots; `useLiveDecisions.ts` refreshes every five
seconds while visible, without clearing active controls. `PollActions.tsx` owns
pending/error states and never automatically retries a mutation.

The global legacy ballot store supports one open motion. Both interfaces share
PARLEYPRO operations; no per-poll ballot model or independent concurrent polls
are introduced. Closed results use saved totals; voter identities stay private.
See [PARLEYPRO](../../../../SPDWEBAPP/PARLEYPRO/README.md) for authorization,
atomic transitions, conflicts and server tests. No new configuration keys.

`test/decisions.spec.ts` retains read/access/error coverage. Cross-interface
transaction coverage is in `frontend/test/zz-transactions.spec.ts`: React votes,
legacy vote change, live result refresh, closure and saved-result navigation.
Run the production build and Playwright per root frontend README.
