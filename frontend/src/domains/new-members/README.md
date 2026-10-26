# New-member marks

Owns `/app/new-members`, `/new`, `/review`, `/history/:userId`,
`/marks/:id/edit` and `/export` beneath that prefix. The source-cited
[behavior/acceptance document](../../../../SPDWEBAPP/NEWMEMBER/docs/react-behavior.md)
is authoritative for legacy rules, integrity fixes and unresolved policy.

`NewMemberMarks`/`MarksPanels` present approved personal/active summaries and own
pending/recent-denied submissions. Board-only overview directs to the review
queue. `MarkForm` handles validated multi-recipient signed submission and board
edit/single-recipient retarget; `MarkReview` decides pending requests;
`MarkHistory` presents approved details/audit; `MarkExport` downloads actual
Current/historical workbooks. `MarksFrame` owns labeled icon navigation and a
contextual Legacy comparison URL for every workflow. There are no fake save,
review, totals or initiation/progress controls.

`contracts.ts` validates response shapes; field drafts stay independent of
background reads. Forms guard dirty/back/reload and busy states. A form-local
operation UUID survives timeout/retry; the backend atomically returns the same
batch for replay. The client never automatically retries or fabricates success.
Stale edit conflicts preserve fields and offer an explicit confirmed reload.
Review and read pages refresh while visible and on successful same-origin writes;
legacy changes reconcile from the same database. Existing API/HTML operations
remain server-authoritative for roles, recipients, audits and signed arithmetic.
No browser-stored identity, credentials or external integration is introduced.

Run `npm run build --prefix frontend`, `npm run format:check --prefix frontend`
and `npm run test:e2e --prefix frontend` from repository root. `test/marks.spec.ts`
covers real read/role/error/mobile behavior. `test/transactions.spec.ts` drives
actual cross-interface creation/decision/totals, board auto-approval/edit/revoke,
stale form recovery, Current/historical downloads and interrupted acknowledgement
replay at390px. The wrapper runs after seeded read contracts, like existing poll/
service mutation scenarios. Backend tests additionally cover invalid batches,
forged identity/CSRF, direct role conjunctions and workbook cell types/identities.
No new production configuration keys are required.
