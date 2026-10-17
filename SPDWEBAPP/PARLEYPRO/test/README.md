# PARLEYPRO regression testing

Wave 1 is a source-inspected design proposal; no domain tests were implemented or executed. Coordinator verification and policy decisions precede Wave 2.

Scope: create polls, current per-user choices, action dispatch, close/count/reset, current/history/live reads, route integration with the public shared `requires_role` decorator, and domain-owned poll admin behavior (C03). See the [regression specification](regression-spec.md) and shared guidance below.

- [Shared testing map](../../../docs/testing/README.md)
- [Wave 1 contract](../../../docs/testing/wave-1-agent-prompt.md)
- [Setup and demo settings](../../railway_demo/README.md)

Existing `../tests.py` contains no test methods. `../../railway_demo/tests.py:58-67,99-104` checks executive page rendering and one ACTIVE Aye write; its admin block assertion is cross-domain delivery coverage. It does not establish fine-grained polling permissions, counts, closure safety or concurrent behavior. No measured coverage percentage is available.

Proposed Wave 2 layout (only these two Markdown documents exist now):

```text
test/
  __init__.py                 # add and verify Django discovery in Wave 2
  README.md
  regression-spec.md
  assertions.py              # reusable state/business assertions
  test_creation.py
  test_votes.py
  test_closure.py
  test_reads.py
  test_access.py
  test_admin.py
  test_transactions.py       # explicit backend prerequisites
```

Current commands from repository root, for the coordinator or later work:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py check
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test PARLEYPRO
```

The last command currently discovers the placeholder and is not proof of coverage. Proposed focused command after introducing the package:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test PARLEYPRO.test
```

Use the documented isolated environment; do not assume a coordinator-only interpreter path is portable. Do not install packages as part of this design handoff. Synthetic ORM fixtures need migrated auth/profile/role/poll models, explicit role sets, a controlled aware clock, and enforced-CSRF clients. Ordinary cases use `TestCase`; pure admin formatting uses `SimpleTestCase`; partial commits and races need `TransactionTestCase`. Admin CRUD needs an isolated test URL/settings arrangement allowing Django admin while retaining the separately tested public-demo block. Real PostgreSQL with separate connections is required for the race designs; SQLite results cannot establish them. These shared test facilities are proposals, not existing fixtures.

Critical blockers: unauthorized ACTIVE close currently persists/reset votes; no transaction or open-poll invariant exists; policy for simultaneous polls, no-poll casts, ambiguous action keys, live-results audience and retention remains unresolved. Detailed expected safe outcomes and compatibility observations are separated in the specification. Application tests were intentionally not run in Wave 1; baseline execution belongs to the coordinator.
