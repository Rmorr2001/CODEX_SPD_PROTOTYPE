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

The stateful ServiceForm component exceeds the usual80-line review threshold.
Its one loading/validation/submission lifecycle and tightly related accessible
fields are kept together after review; the file is110 physical lines, below the
400-line maximum. Reporting and chair decisions are separate responsibilities.
