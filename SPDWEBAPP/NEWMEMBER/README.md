# New-member marks

Owns new-member mark requests, approval, editing, history and class summaries.
The original `models.py`, `views.py` and `views_functions.py` remain authoritative
for writes and business calculations; `urls.py` retains the original routes.
The framework API composition exposes `api.NewMemberMarksView` at
`GET /api/v1/new-members/` without moving transactions or changing schema.

The read adapter uses AUTHENTICATE's supported profile boundary before domain
queries. It whitelists role-specific fields, returns `Cache-Control: no-store`,
and rejects writes. Query parameters cannot select another caller's identity.

- NEW_MEMBER gets its own approved signed total, standing, latest/history and
  the actual class average. Approved total >=0 means Good Standing; a negative
  total means Needs Improvement. This personal view takes precedence for dual
  NEW_MEMBER/ACTIVE roles and does not disclose others' reasons.
- ACTIVE gets current NEW_MEMBER class totals ordered by approved total, existing
  aggregate analytics, and its own submissions. The existing helper includes
  requested and denied submissions but excludes denied events older than **14
  days**, using event date (its old “month” comment is inaccurate). Approved
  submissions are excluded. Class rows contain names, totals and history links,
  never other members' individual disciplinary reasons.
- NM_BOARD gets the review capability without requiring ACTIVE, matching the
  original review permission. A board-only caller gets a limited review handoff
  and no class/personal/submission data. ALUMNI or unclassified profiles alone
  are denied. ACTIVE can request; NM_BOARD approves/edits; denying an edited
  record additionally requires NME. The read adapter does not rewrite these
  legacy mutations or grant new write access.

There is no milestone, initiation eligibility, attendance or positive-progress
engine. No new configuration keys or secret values are required. Existing
[regression designs and evidence](test/README.md) document legacy transactions.
`test/test_read_api.py` covers signed arithmetic, approved-only scope, own record
isolation, role conjunction/precedence, 14-day filtering, ordering, empty data,
whitelisted payloads and read-only behavior. From repository root:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py test NEWMEMBER.test.test_read_api --noinput
```
