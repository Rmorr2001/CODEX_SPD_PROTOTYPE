# PARLEYPRO regression testing

Wave 1.5 is documentation only: 40 original groups now map to 114 named designs.
58 are READY, 5 NEEDS_FIX, 48 POLICY_BLOCKED and 3 INFRA_BLOCKED.
No application tests or case designs were executed by this agent.

- [Inventory, roles, sources, decisions and Wave 2 order](regression-spec.md)
- [Case index, status counts and complete old-to-new mapping](case-index.md)
- [Creation](cases/creation.md), [access/CSRF](cases/access.md), [voting](cases/voting.md)
- [Close/reset](cases/closure.md), [failures/races](cases/failures-and-races.md)
- [Reads/routes](cases/reads-and-routes.md), [admin C03](cases/admin.md)
- [Model/retention](cases/model-boundaries.md), [browser](cases/browser.md)
- [Shared fixture contract](../../../docs/testing/fixture-contract.md)
- [Refinement contract](../../../docs/testing/wave-1-5-agent-prompt.md)
- [Shared testing map](../../../docs/testing/README.md)
- [Environment/setup](../../railway_demo/README.md)

Source baseline is `7e25ac2`; refinement baseline is `c8bbc4e`.
Existing `../tests.py` is an empty placeholder. Demo tests check executive polling
page renders and one ACTIVE Aye write; they do not establish close safety or races.
No measured coverage percentage is available. READY means ready design, not approval.

Current documented commands from repository root, for coordinator/later execution:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py check
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test PARLEYPRO
```

The app label currently finds the placeholder. Proposed Wave 2 package command:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test PARLEYPRO.test
```

Wave 2 must verify both discovery modes and use the shared contract's safe business/demo
settings rather than assume the current runtime-secret-loading settings are isolated tests.
No final settings-module name is invented here. No helper or executable package exists yet.

Proposed layout is `test/__init__.py`, `assertions.py`, and workflow `test_*.py` modules
listed in the specification. Use shared identity/request/clock/snapshot helpers, real ORM
rows and explicit roles. Use real PostgreSQL separate connections for races; a browser
runner with fake timers/intercepted fetch is required for browser designs. Business-mode
admin uses actual permissions while demo admin blocking remains separately covered.

Unsafe close, partial-write/race behavior, open-poll/dispatch/eligibility policy and admin
retention are the major blockers. Coordinator verification precedes any implementation.
