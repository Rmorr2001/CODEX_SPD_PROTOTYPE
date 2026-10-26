# Marks REST adapters

Mounted by CORE under `/api/v1/new-members/`; legacy HTML stays under
`/newmember/`. `dashboard.py` keeps the existing GET-only dashboard contract.
`submissions/` POST creates/replays a validated batch; `options/` GET supplies
eligible recipients/classes; `review/` GET supplies the board queue; `history/:id/`
GET returns authorized approved history; `export/` GET returns the shared workbook.
`:id/` GET/PATCH is board detail/edit; `:id/decision/` POST decides a pending mark;
`:id/revoke/` POST is the explicit board+educator override.

Session auth/CSRF applies to writes. Serializers describe transport contracts;
shared operations own all role, eligibility, atomicity, revision and audit rules.
No client-provided requester/status/audit is trusted. Expected validation errors
are400, permissions403, missing records404, stale/conflicting state409; database
availability failures are503 with safe messages. Reads are no-store. There are no
new configuration keys, credentials or external integrations.

See the parent README and behavior document for policy and testing commands.
