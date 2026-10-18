# Philanthropy regression design

Wave 1.5 refines 33 parent groups into 118 atomic designs:
66 READY, 41 POLICY_BLOCKED, 11 NEEDS_FIX and 0 INFRA_BLOCKED.
No application tests or proposed cases were implemented or run in this refinement.

- [Inventory, roles, decisions and Wave 2 checklist](regression-spec.md)
- [Case index, status counts and complete parent mapping](case-index.md)
- [Shared fixture contract](../../../docs/testing/fixture-contract.md)
- [Wave 1.5 format/readiness contract](../../../docs/testing/wave-1-5-agent-prompt.md)
- [Shared testing map](../../../docs/testing/README.md)

The domain covers requests, approvals, edits, academic-year statistics, individual
history, XLSX exports, the remaining-hours tag and C03 domain admin.
Source baseline is `7e25ac2`; documentation refinement baseline is `c8bbc4e`.

Current scaffold [tests.py](../tests.py) has no assertions. Existing demo tests
check page statuses and integer-submission existence; see the spec for gaps.
Current documented commands from repository root, not run during this refinement:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py check
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY
```

The domain command currently targets the empty scaffold. Follow
[root setup](../../../AGENTS.md) and [demo setup](../../railway_demo/README.md).
The shared fixture contract supplies business/demo safe settings, real synthetic
users/profiles, explicit roles, real CSRF, controlled clocks and scoped snapshots.
No runtime secrets, demo personas, actual uploads or network are needed.

Proposed commands after the coordinator supplies safe business settings through
DJANGO_SETTINGS_MODULE and verifies discovery:

```sh
.venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY.test
.venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY.test.test_exports
```

Proposed Wave 2 singular-package layout (not created in this wave):

```text
test/
  __init__.py
  assertions.py
  test_requests.py
  test_approvals.py
  test_edits.py
  test_statistics.py
  test_history.py
  test_tags.py
  test_exports.py
  test_admin.py
  test_integration.py
```

Keep reusable owner/hour/audit/total/workbook assertions separate from legacy
HTTP/template/message adapters. Use TestCase for ORM requests, SimpleTestCase
for pure helpers, and TransactionTestCase for post-write failures/races.
PostgreSQL races need independent connections and bounded synchronization;
passing SQLite checks cannot establish those guarantees. Resolve placeholder
`tests.py` coexistence without dropping demo tests; a zero-discovery run is not success.
