# Backend regression suite

Wave 2 implements all **393 READY designs** frozen at `4b103f6`. The audited
combined Part 2 baseline ran 419 tests: 394 domain methods, 11 shared-harness tests
and 14 API/frontend delivery tests.
The original nine demo tests run separately. [Part 2](../migration/part-2-foundation.md)
also added nine Playwright checks against the built React application. Subsequent
screen slices add domain-local API/browser tests and bounded demo-entry checks;
the [screen delivery log](../design/delivery-log.md) records current full-run results.
There were no skipped or expected failures in the baseline passing counts.
See [hardening results](part-1-hardening.md),
[original Wave 2 results](wave-2-results.md) and
[the goals declared before dispatch](wave-2-goals.md).

| Domain | Tests and documentation | Verified READY | Blocked designs |
| --- | --- | ---: | ---: |
| AUTHENTICATE | [Identity and members](../../SPDWEBAPP/AUTHENTICATE/test/README.md) | 76 | 81 |
| PARLEYPRO | [Polling](../../SPDWEBAPP/PARLEYPRO/test/README.md) | 58 | 56 |
| PHILANTHROPY | [Service hours](../../SPDWEBAPP/PHILANTHROPY/test/README.md) | 66 | 52 |
| NEWMEMBER | [New-member marks](../../SPDWEBAPP/NEWMEMBER/test/README.md) | 50 | 38 |
| HOME | [Public content and demo integration](../../SPDWEBAPP/HOME/test/README.md) | 63 | 34 |
| MISC | [Announcements and alerts](../../SPDWEBAPP/MISC/test/README.md) | 80 | 23 |
| Total | | 393 | 284 |

The subsequent [independent adversarial review](adversarial-review.md) found
four READY fixture/assertion gaps and three preservation-design extensions.
[Part 1 hardening](part-1-hardening.md) closes those seven demonstrated gaps.
Passing mapped methods establish execution; the assertion-kill checks supply
separate evidence that the strengthened tests reject the reviewed defects.

## Setup and commands

From the repository root, Python 3.12:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python -m coverage run tools/testing/run_regressions.py
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.demo_settings .venv/bin/python -m coverage run --append SPDWEBAPP/manage.py test railway_demo --noinput
.venv/bin/python -m coverage report
.venv/bin/python -m coverage xml
.venv/bin/python tools/testing/probe_regressions.py
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py check
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py makemigrations --check --dry-run
.venv/bin/python -m unittest discover -s tools/file_tree -p 'test_*.py'
```

For a scoped run, use the business settings above with
`SPDWEBAPP/manage.py test PARLEYPRO.test --noinput` or app label `PARLEYPRO`.
Both discovery forms were verified for every domain. Run the mapping audit for
completion; plain Django discovery alone does not check the frozen inventory.
No Python formatter, lint or static type-check command is configured.

`run_regressions.py` rejects missing, invalid and undiscovered READY mappings,
then requires every mapped method to finish successfully. Skips, expected
failures and unexpected successes fail the audit. It writes
`work/test-results.json`, including all 284 blocked designs and their reasons.
`probe_regressions.py` requires 13 bounded in-memory behavior mutations to be
caught: the original six mapped-case probes and seven adversarial defects tested
against complete affected-domain suites. Clean/restored runs must pass; mutants
must fail by assertion with zero errors, skips or expected/unexpected outcomes.
It never edits source files and writes `work/mutation-results.json`.
`NM-05-01b` now maps to its original signed-total method and a new fractional-mean
method. All 393 frozen READY IDs remain required; no blocked design is promoted.

The combined audit also discovers `SPDWEBAPP_CORE.api.test` and
`SPDWEBAPP_CORE.frontend.test`; their tests exercise framework delivery, not
additional frozen business-case IDs. Frontend build/type/format/browser commands
are in [its README](../../frontend/README.md). Python lint/type tooling is absent.

GitHub Actions runs these checks on pull requests and pushes to
`prototype/railway`, uploading both JSON reports and `coverage.xml`. Reports and
coverage files are ignored locally. Coverage includes the six domains and demo
code plus the new API/frontend Python packages, excluding migrations and test
code; there is no percentage floor yet.

## Isolation and limits

[The shared fixture contract](fixture-contract.md) describes the implemented
`SPDWEBAPP_CORE/testing/` settings, real-ORM factories, clock, CSRF, media and
state assertions. Tests use a fresh in-memory SQLite database, synthetic users,
local hosts and temporary files; they do not import runtime secret configuration
or require deployed services. Business/admin and demo settings are distinct.
Application roles grant neither inferred roles nor staff/model permissions.

The [677-design inventory](wave-2-inventory.json) preserves every original status:
393 READY, 41 NEEDS_FIX, 237 POLICY_BLOCKED and 6 INFRA_BLOCKED. The last three
categories receive no passing-test credit. PostgreSQL concurrency, browser
behavior, deployment and unresolved business rules remain unverified. SQLite
success and code coverage percentages do not settle these boundaries.

## Where to work

The user-selected singular directory keeps tests recognizable beside their docs:

```text
SPDWEBAPP/<DOMAIN>/test/
  README.md                 commands, purpose and boundaries
  regression-spec.md        inventory and decisions
  cases/*.md                named GIVEN / WHEN / THEN designs
  case-map.json             READY ID -> fully qualified unittest methods
  test_*.py                 executable regression tests
  support.py or helpers.py  domain-specific synthetic fixtures, when needed
```

Maintain one authoritative explanation and link to it. Update specifications,
case mappings and meaningful assertions with behavior changes. Do not make
unsafe behavior contractual just to convert a blocker into a green test.
Admin cases remain with their domains; demo entry belongs to AUTHENTICATE and
cross-domain fictional seeding/media composition belongs to HOME. These testing
assignments do not move runtime code out of `railway_demo`.

History: [Wave 1 review](wave-1-review.md), [Wave 1.5 review](wave-1-5-review.md),
[design readiness](case-readiness.md), [original agent prompt](wave-1-agent-prompt.md)
and [refinement prompt](wave-1-5-agent-prompt.md). The original 217 groups became
677 named designs; those historical design counts are not passing-test counts.
