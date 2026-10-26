# Service hours

Owns `/app/service`, `/new`, `/review`, `/history`, `/history/:userId`, `/chapter`
and `/events/:id/edit` beneath that service prefix. `ServiceHours.tsx` shows own
academic-year status/approved totals. `ServiceForm.tsx` submits or chair-edits
validated events; `ServiceReview.tsx` handles pending decisions;
`ServiceReports.tsx` presents approved lifetime history and chapter statistics.
`transactions.ts` validates record contracts. XLSX downloads use the authenticated
API directly; legacy comparison links remain explicit.

Both interfaces share PHILANTHROPY operations and exact two-decimal storage;
pending status is labeled Pending. The server owns identity, review and edit
audit fields. UI controls reflect roles, with server authorization authoritative.
Mutations use the shared CSRF client and do not retry automatically. Form errors
retain user input; timeout/conflict messages instruct checking current state.
No notes field, invented requirement or placeholder submission is used.

See [PHILANTHROPY](../../../../SPDWEBAPP/PHILANTHROPY/README.md) for rules,
permissions, migration impacts and unresolved self-review/reversal policy.
`test/service.spec.ts` covers read/year/mobile/error behavior; root frontend
`test/zz-transactions.spec.ts` exercises actual submissions and decisions through
both interfaces. Build and run per frontend README. No new production keys.

`ServiceEntryForm` and `useServiceDraft` share fields/validation/submission between
full-page routes and `ServiceQuickEntry`, mounted in the member toolbar. The Sheet
uses Event, Date and Hours only. Its local draft survives background reads;
Escape/Cancel/Back ask before discarding edits, pending writes block dismissal,
and confirmed success closes/reset the form. Navigation uses React Router's data
router for `useBlocker`. The direct create/edit URLs still work.

Visible service views reconcile every three seconds and on focus/successful
writes. Confirmed decisions update the queue immediately; independent sessions
receive authoritative changes without navigation. `test/quick-entry.spec.ts`
covers desktop/390px submission, focus, cancellation, back/forward, refresh/API
failure retention and busy/duplicate-write protection. No new storage or policy.
