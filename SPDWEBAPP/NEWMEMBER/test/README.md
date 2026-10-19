# New-member marks regression tests

The current suite implements all **50 frozen READY designs** from baseline
`4b103f6` with **51 discoverable test methods**. [case-map.json](case-map.json)
maps each READY ID to its fully qualified unittest IDs; `NM-05-01b` includes
a separate fractional-average method. The [regression specification](regression-spec.md)
and [workflow case designs](cases/) retain the source inventory, role matrix and
38 blocked designs: 14 NEEDS_FIX and 24 POLICY_BLOCKED. Those blocked cases are
not passing coverage, skips or expected failures.

Tests cover public navigation, login/role/CSRF boundaries, signed multi-target
requests, board auto-approval, review/edit audit fields, unchanged records,
analytics/date windows, history queries, parsed XLSX cells and Django admin.
[Wave 2 findings](wave-2-findings.md) records the coordinator-approved admin
redirect clarification and the resolved shared template setup issue.

Run from the repository root in the installed isolated environment:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test NEWMEMBER.test --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test NEWMEMBER --noinput
```

At the original Wave 2 baseline, explicit-package and app-label discovery ran
**50 tests successfully**, with
no skips or expected failures and no system-check issues. The obsolete empty
`NEWMEMBER/tests.py` was removed after package discovery was established. For
other environments, use a Python executable with the project's installed test
dependencies; the `/workspace/work/` environment path is local to this session.
The commands use [safe shared settings](../../SPDWEBAPP_CORE/testing/settings.py),
real middleware/admin/templates and a synthetic test database; they import no
runtime secret configuration and use no external services.

Implementation:

- [support.py](support.py): thin real-ORM mark fixtures and domain state assertions.
- [test_boundaries.py](test_boundaries.py): public/login/role boundaries and real CSRF.
- [test_requests.py](test_requests.py): signed batches and auto-approval.
- [test_decisions.py](test_decisions.py): pending review, decisions, edits and failure containment.
- [test_read_models.py](test_read_models.py): totals, date windows, history and filter arithmetic.
- [test_exports.py](test_exports.py): parsed XLSX values/types, totals and empty output.
- [test_admin.py](test_admin.py): real model permissions, forms, display and deletion.

Fixtures follow the [shared contract](../../../docs/testing/fixture-contract.md).
Each test uses explicit synthetic actors; named rows and role/major/permission/group
relations are compared against fresh database state, and unexpected media writes
are checked. Allowed mark changes are compared against every persisted field.
Only the clock and a deliberate pre-SQL save failure are patched; roles, queries,
aggregations and request handlers execute normally. No eligibility, repeated-review,
visibility or retention policy has been selected, and no application behavior was fixed.

The coordinator owns combined-suite validation, the existing demo suite, mapping
acceptance and bounded mutation probes under [Wave 2 goals](../../../docs/testing/wave-2-goals.md).

## Part 1 hardening

[The hardening results](../../../docs/testing/part-1-hardening.md) record the
stronger preservation assertions, clean-suite results and required mutation kills.
The historical Wave 2 findings above retain their original counts and evidence.
