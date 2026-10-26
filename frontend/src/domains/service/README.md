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
full-page routes and `ServiceQuickEntry`, mounted in the main service summary. The Sheet
uses Event, Date and Hours only. Its local draft survives background reads;
Escape/Cancel/Back ask before discarding edits, pending writes block dismissal,
and confirmed success closes/reset the form. Navigation uses React Router's data
router for `useBlocker`. The direct create/edit URLs still work.

Visible service views reconcile every three seconds and on focus/successful
writes. Confirmed decisions update the queue immediately; independent sessions
receive authoritative changes without navigation. `test/quick-entry.spec.ts`
covers desktop/390px submission, focus, cancellation, back/forward, refresh/API
failure retention and busy/duplicate-write protection. No new storage or policy.

Service entry belongs only to the service page, below personal approved/pending
figures. Academic-year selection is in its header; activity precedes secondary
tools. Success feedback can dismiss and expires after six seconds; leaving the
page removes it. The drawer stays mounted through query refresh/year changes.

`ServiceNavigation` supplies consistent labeled icon buttons (native navigation
links) for Your hours, Chapter totals, Requests, History and Export, with active
route state and chair-only request visibility. It stays inside service content.
The form now identifies Recipient using the authenticated member for creation
and stored owner for edits. That field is read-only: both original and current
HTML workflows create only for the submitting member; chair edits preserve owner.
Assigning to another member needs a chapter decision on authority/single-vs-batch
recipients and a separate submitter audit before enabling it. No broader assignment
permission or silent recipient payload is invented by this presentation pass.
