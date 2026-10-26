# PHILANTHROPY — service hours

Owns service submissions, chair decisions/edits, approved history, chapter
statistics and XLSX reporting. HTML and React share the same models and operations.

- `urls.py` / `views.py`: legacy `/philanthropy/` routes.
- `operations.py`: shared `ServiceForm`, role checks and atomic writes.
- `views_functions.py`: shared July1–June30 reads, approved-only arithmetic and
  HTML decision messages. `exports.py` is the authoritative workbook implementation.
- `api/`: separate REST URLs, serializers, commands, read snapshots and reports.
- `test/`: regression designs, case mappings and executable checks.

Hours use `DecimalField(10,2)`, minimum0.5 in both submission/edit adapters,
maximum99,999,999.99 and at most two decimal places. Non-finite inputs, excess
precision, missing/overlong titles and invalid dates are rejected before writes.
Migration0005 preserves existing integer values; already truncated historic
fractions cannot be recovered. Reversal refuses to run while fractional rows
exist, preventing silent data loss. XLSX hours remain numeric, with exact totals.

## Routes and permissions

All REST routes below are beneath `/api/v1/service/`, use session authentication,
no-store responses and CSRF protection for writes:

| Route | Behavior / boundary |
| --- | --- |
| GET/POST collection | ACTIVE own academic-year events / create pending request |
| GET `review/` | ACTIVE+PHIL_CHAIR pending chapter queue |
| GET/PATCH `<id>/` | Owner/chair detail; PHIL_CHAIR edits all three event fields |
| POST `<id>/decision/` | ACTIVE+PHIL_CHAIR approve/deny a pending request |
| GET `chapter/?year=YYYY` | ACTIVE approved chapter statistics/member totals |
| GET `history/` or `history/<user_id>/` | ACTIVE approved own/member lifetime history |
| GET `export/` | Authenticated approved ACTIVE-member workbook, matching legacy scope |

`year` must be four ASCII digits in1900..current calendar year+1; own reads
include pending/denied entries but totals count approved events only. The
existing10-hour statistic remains a display calculation, not a new requirement.
Chair edits retain approval status/audit and record editor/time, matching the
existing edit workflow; ordinary members cannot edit submitted entries.

Self-review and approval/denial reversal are **unresolved policy**, explicitly
blocked with409 in both interfaces pending the user's answer. The compare-and-set
pending transition prevents another review from silently overwriting a decision.
Existing ACTIVE cross-member approved history and authenticated export scope
are retained; no private pending requests are included in reports. These access
policies should be reviewed before production use. Error responses never expose
raw database failures. No real records or external integrations are used.

`test/test_transactions_api.py` verifies both interface directions, exact
fractional totals/exports, ownership, role/CSRF denial and failed writes.
`test/test_decimal_migration.py` verifies upgrade preservation/downgrade safety.
Frontend `test/` and `frontend/test/zz-transactions.spec.ts` cover forms and role
switches. Use root verification commands; see the
[milestone document](../../docs/migration/functional-milestone-1.md).
