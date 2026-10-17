# New-member marks regression design

Wave 1 is source inspection and test pseudocode only, pending coordinator source
verification. No executable tests were added and no application tests were run.
Scope: public landing, mark requests/approval/editing, dashboards/helpers, history,
XLSX exports, the local template filter, and marks admin. See the
[regression specification](regression-spec.md), [shared testing map](../../../docs/testing/README.md),
and [mandatory Wave 1 contract](../../../docs/testing/wave-1-agent-prompt.md).

`NEWMEMBER/tests.py` is an assertion-free placeholder. Existing demo assertions
in `railway_demo/tests.py:31–38,58–72` check seed count and privileged/new-member
page rendering; they do not verify marks writes, totals, exports or narrow roles.

Current documented commands, from repository root after the environment is set
up per [root guidance](../../../AGENTS.md) and [demo setup](../../railway_demo/README.md):

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test NEWMEMBER
```

The latter currently targets a placeholder, not meaningful marks coverage.
Coordinator alone runs the shared baseline in Wave 1. Do not assume the local
coordinator environment path is portable or install dependencies in this wave.

Proposed Wave 2 layout (singular `test/`; none of these Python files exist yet):

```text
test/
  __init__.py
  assertions.py             # reusable marks/audit/unchanged-record assertions
  test_requests.py          # N01, helper boundary
  test_decisions.py         # N02–N04, transitions and atomicity
  test_read_models.py        # N00, N05–N06, N08
  test_exports.py            # N07, parsed XLSX cells/types
  test_admin.py              # C03
  test_postgres_races.py     # independent connections; conditional infrastructure
```

Proposed discovery commands, to verify in Wave 2:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test NEWMEMBER.test
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test NEWMEMBER.test.test_requests
```

Use isolated synthetic users with explicit roles, real ORM rows and a controlled
clock. Coordinate shared factories/settings rather than creating a second
fixture framework. Demo middleware intentionally blocks admin; C03 needs a
coordinator-approved isolated admin test configuration. PostgreSQL race checks
need a separate test database and connections. Policy questions and current
security/validation defects are gates, not passing legacy contracts.
