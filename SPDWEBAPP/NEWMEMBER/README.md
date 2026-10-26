# New-member marks

Owns signed mark submission, review, editing/revocation, approved totals/history
and Current/historical-class export. The detailed, source-cited
[behavior and acceptance contract](docs/react-behavior.md) distinguishes supported
legacy rules, hardened defects and unresolved policy. Keep it authoritative.

`operations.py` is the public business boundary: `submit_marks`, `decide_mark`,
`edit_mark`, `revoke_mark`, `history_target`, validation, eligibility and revisions.
`views.py`/`urls.py` retain `/newmember/...` HTML composition;
`views_functions.py` preserves supported calculations and compatibility wrappers.
`api/urls.py`, `api/commands.py`, `api/reads.py` and `api/serializers.py` own distinct
REST routes under `/api/v1/new-members/`. React lives in root frontend's
new-members domain. Both adapters call the same operations and export builder.

- ACTIVE submits to current NEW_MEMBER recipients. NM_BOARD also auto-approves
  its own creations, matching legacy behavior. Zero/negative/positive whole
  marks are valid; there are no mark categories or initiation thresholds.
- NM_BOARD reviews pending requests and edits existing records; explicit edit-time
  denial additionally requires NME. Expected revisions reject stale edits and
  opposite repeated decisions; repeating the same decision preserves audit.
- NEW_MEMBER personal reads take precedence over ACTIVE, with own approved
  history. ACTIVE/board may inspect current-recipient histories. ALUMNI or
  roleless profiles alone are denied. Current class export for NEW_MEMBER is
  preserved; historical export remains unavailable even for dual NEW_MEMBER roles.
- Only approved rows affect totals/standing. Own submissions contain pending and
  denied events from the actual 14-day event-date window, excluding approved rows.
- `MarkSubmission` and nullable event `submission` in migration0004 hold a scoped
  operation UUID/fingerprint. Same-payload retries return the original atomic
  batch; conflicting reuse cannot create extra records. Existing records remain
  unchanged with null submission; no credential or new environment key is needed.
- `exports.py` separates recipients by ID, quotes valid filenames and writes
  spreadsheet text literally. Approved numeric marks remain numeric.

Run from the repository root using standalone synthetic settings:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py test NEWMEMBER --noinput
.venv/bin/python tools/testing/run_regressions.py
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py spectacular --validate --fail-on-warn
```

[test/README.md](test/README.md) retains historical frozen-case provenance.
`test_transactions_api.py` covers the new shared/API integrity contracts and real
parsed workbook behavior; frontend domain test/ owns cross-interface browser flows.
Django admin permissions remain unchanged. Broader visibility, general reversals
or new eligibility/point policy require an explicit chapter decision.
