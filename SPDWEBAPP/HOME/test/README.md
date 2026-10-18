# HOME regression design

Wave 1.5 refines 21 dense groups into 97 atomic, unexecuted case designs:
63 READY, 6 NEEDS_FIX, 26 POLICY_BLOCKED and 2 INFRA_BLOCKED.
READY means an implementation-ready preservation design, not approval or a passed test.

Start with the [inventory, roles and decisions](regression-spec.md), then the
[case/status index and complete old-ID mapping](case-index.md).
Detailed cases cover C01 public pages, C04 singleton lifecycle, HOME C03 admin,
D02 demo seed integration and D03 media/composition. Demo code remains in
`railway_demo`; AUTHENTICATE owns D01 entry and demo admin blocking.
Other domains own their workflow rules; HOME checks cross-domain seed field shape.

Use the [shared fixture contract](../../../docs/testing/fixture-contract.md),
[refinement rules](../../../docs/testing/wave-1-5-agent-prompt.md) and
[six-domain map](../../../docs/testing/README.md). No helper is implemented here.
All fixtures are synthetic. Never load runtime secrets, real uploads or member data.

Current documented commands from repository root (not run in this wave):

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test HOME
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
```

`HOME/tests.py` remains an assertion-free scaffold. Existing demo tests provide
limited public-page and seed smoke assertions; the specification records their gaps.
No executable tests, application imports, dependency installation or app checks ran.

Proposed Wave 2 layout adds singular `test/__init__.py`, `assertions.py` and
`test_public_pages.py`, `test_content_models.py`, `test_admin.py`, `test_demo_seed.py`,
`test_media_composition.py` and `test_postgres_concurrency.py` beside these Markdown files.
Keep reusable business state assertions separate from HTML/redirect/status adapters.
Verify package and app-wide discovery while retaining existing demo tests.

Proposed commands after the coordinator supplies the safe business/demo settings
module paths and sets shell variable `SPD_TEST_SETTINGS_MODULE` to the relevant path:

```sh
DJANGO_SETTINGS_MODULE="$SPD_TEST_SETTINGS_MODULE" .venv/bin/python SPDWEBAPP/manage.py test HOME.test
DJANGO_SETTINGS_MODULE="$SPD_TEST_SETTINGS_MODULE" .venv/bin/python SPDWEBAPP/manage.py test HOME
```

Use business mode for actual admin/model permission checks and demo mode for composition.
Neither mode may import runtime secret configuration. Tests use actual middleware,
real ORM rows, `csrf_client` tokens, temporary media, `at_time` and named state snapshots.
Model/commit failure cases distinguish DB state from filesystem residue.
PostgreSQL races require independent connections and bounded synchronization.
Browser controls and collected-static serving need the case-specific facilities
listed in the index. Settings-module names and harness implementation remain coordinator-owned.

[File-tree generator checks](../../../tools/file_tree/README.md) remain a separate
tooling gate, not HOME business coverage. Only Markdown validation ran here;
no measured numerical coverage or passing-suite claim is made.
