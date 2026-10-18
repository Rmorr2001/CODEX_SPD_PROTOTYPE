# Philanthropy regression tests

Wave 2 implements all 66 frozen READY cases from baseline `4b103f6`.
Both explicit-package and app-wide runs pass: **66 tests, zero failures/errors,
zero skips/expected failures**. The 52 non-READY designs remain documented and
are not counted as implemented coverage.

- [READY case-to-unittest mapping](case-map.json)
- [Execution results and transaction rationale](wave-2-findings.md)
- [Design inventory, roles and decisions](regression-spec.md)
- [All 118 designs and their 33-parent mapping](case-index.md)
- [Shared fixture contract](../../../docs/testing/fixture-contract.md)
- [Wave 2 goals](../../../docs/testing/wave-2-goals.md)

Scope includes role/ownership denials, real CSRF, exact integer submissions,
initial approval/denial audit, edit reads, approved statistics/history, July–June
boundaries, goals/empty cases, parsed XLSX cells/types/totals, domain admin C03 and
remaining-hours tags. Fractional-hour storage, repeated/self decisions, export
scope/authorization changes and other non-READY policy/fix designs are excluded.

From repository root, the commands actually run in this cloud checkout were:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY.test --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY --noinput
```

The interpreter path above is coordinator-provided and not portable. Follow
[root setup](../../../AGENTS.md) to prepare a local isolated environment; use
`.venv/bin/python` with the same standalone settings and test labels. These test
settings use synthetic credentials, a test-only database, temporary media and
real middleware/templates/admin; they do not import runtime secret configuration.
No deployed service, network, demo persona or private/member data is needed.

Executable singular-package layout:

```text
test/
  __init__.py
  support.py             # thin event factory and domain assertions
  test_access.py
  test_requests.py
  test_approvals.py
  test_edits.py
  test_statistics.py
  test_history.py
  test_exports.py
  test_admin.py
  test_integration.py
  case-map.json
```

The obsolete empty `PHILANTHROPY/tests.py` was removed. Discovery audits establish
that both labels find the identical 66 unittest IDs and each frozen READY case
maps to one of those executed IDs. No additional framework smoke tests are
counted toward the domain's 66 contracts.

Shared factories, scoped row/relation snapshots, clocks and temporary-media
isolation come from `SPDWEBAPP_CORE.testing`. Ordinary ORM tests extend
RegressionTestCase; pure date/tag tests use SimpleTestCase. C06b/C07a use
TransactionTestCase with shared temporary_media because their caught save errors
must exercise request autocommit rather than TestCase's artificial outer atomic
block. This coordinator-approved boundary change preserves their assertions.
See the findings document for evidence and the initial failed-run history.

No application/schema/dependency/configuration/deployment changes or business
policy decisions were made. PostgreSQL races and other non-READY designs remain
future work; this SQLite suite does not establish concurrency guarantees.
