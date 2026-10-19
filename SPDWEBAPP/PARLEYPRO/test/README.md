# PARLEYPRO regression testing

58 named unittest methods implement all 58 frozen READY designs. The remaining 56 designs
stay blocked: 5 NEEDS_FIX, 48 POLICY_BLOCKED and 3 INFRA_BLOCKED. No unsafe close or other
blocked behavior is treated as a passing contract. No coverage percentage is claimed.

- [Executable case mapping](case-map.json)
- [Implementation findings and approved format clarifications](implementation-findings.md)
- [Design inventory, roles and decisions](regression-spec.md)
- [Frozen case index and all 40 original-to-new mappings](case-index.md)
- [Shared fixture contract](../../../docs/testing/fixture-contract.md)
- [Wave 2 goals](../../../docs/testing/wave-2-goals.md)

Run from the repository root with the coordinator's isolated interpreter/settings:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test PARLEYPRO.test --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test PARLEYPRO --noinput
```

The interpreter path is the actual execution environment, not a portable prerequisite.
An equivalent configured virtual environment can use the same standalone settings and
labels. No runtime secret configuration, real database, network or demo seed is required.
Both discovery modes passed with zero skips or expected failures:

| Scope | Discovered/executed | Result |
| --- | ---: | --- |
| PARLEYPRO.test | 58 | PASS (5.177s) |
| PARLEYPRO | 58 | PASS (8.282s) |

System checks reported no issues. Frozen-ID/method mapping checks and scoped diff checks
passed. These are suite counts, not a statement/branch coverage measurement.

Executable layout: `test_creation.py`, `test_access.py`, `test_votes.py`,
`test_closure.py`, `test_reads.py`, `test_admin.py`; `support.py` holds thin ORM poll/choice
fixtures and domain state assertions. The obsolete empty `../tests.py` has been removed.
`test/__init__.py` enables singular-package discovery. Shared identity, clock, CSRF,
snapshot and temporary-media facilities come from `SPDWEBAPP_CORE.testing`.

Tests use explicit narrow role sets, real requests/forms/decorators/templates/ORM/admin,
fresh state comparisons, unchanged actor/target metadata and enforced-CSRF clients.
The only patches isolate actual clock imports; no business behavior is mocked.
Pure icon formatting uses SimpleTestCase; ORM cases use RegressionTestCase.

The `cases/` workflow files remain design specifications. PostgreSQL races and browser
work need their named facilities and policy/fix decisions. No runnable race/browser test
or skip/expected-failure placeholder is counted. AUTHENTICATE owns shared decorator
unit contracts and public-demo admin blocking; these tests own poll-route integration
and real business-mode admin permissions. Future blocked implementations must resolve
POL-01–09 and DEF-01–08 before passing-test credit.

Source design baseline: `7e25ac2`; refinement: `c8bbc4e`; implementation freeze: `4b103f6`.
Coordinator owns combined/demo-suite runs, mapping audit and mutation effectiveness.

## Part 1 hardening

[The hardening results](../../../docs/testing/part-1-hardening.md) record the
stronger preservation assertions, clean-suite results and required mutation kills.
The historical Wave 2 findings above retain their original counts and evidence.
