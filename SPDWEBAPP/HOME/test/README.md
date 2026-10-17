# HOME regression design

Wave 1 is source inspection and proposed pseudocode only; no tests were implemented or executed. The specification requires coordinator source verification before Wave 2.

[Regression specification](regression-spec.md) covers C01 public pages, C04 content singleton lifecycle, HOME's C03 admin/sortable actions, D02 fictional demo seeding, and D03 media/composition. Code ownership for demo behavior remains `railway_demo`. AUTHENTICATE owns demo entry/admin blocking; other domains own their workflow rules. Follow the [shared contract](../../../docs/testing/wave-1-agent-prompt.md) and [six-domain map](../../../docs/testing/README.md).

Existing `HOME/tests.py` is an assertion-free scaffold. `railway_demo/tests.py` has seeded public-page smoke assertions and limited seed idempotency/refusal assertions; see the specification for their precise limits. No measured coverage is claimed.

Proposed singular-directory layout (none implemented):

```text
test/
  __init__.py                  # verify Django discovery alongside tests.py
  README.md
  regression-spec.md
  assertions.py               # reusable content/seed invariants
  test_public_pages.py        # legacy HTTP/template adaptation
  test_content_models.py      # real ORM and temporary storage
  test_admin.py               # non-demo settings, CSRF and permissions
  test_demo_seed.py           # delivery here; production code in railway_demo
  test_media_composition.py
  test_postgres_concurrency.py
```

Current documented commands, from repository root (not run here):

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test HOME
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
```

The first currently discovers only the HOME scaffold. Proposed Wave 2 targeted command after creating the package:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test HOME.test
```

Verify targeted and app-label discovery once, then use focused module labels. Admin tests need a coordinator-approved isolated settings override disabling only the demo boundary, with a synthetic admin mount; production config must never be imported for this purpose. PostgreSQL concurrency tests require a separately configured disposable PostgreSQL database and independent connections; SQLite cannot verify singleton replacement serialization.

Use the [demo setup](../../railway_demo/README.md), synthetic factories proposed in the shared contract, a controlled clock, and temporary `Path` media/static roots. Never read real uploads, environment values, `secret_config.py`, or member data. Mock only deliberate DB/storage failures and external boundaries. Dependency installation, app execution and shared baseline execution belong to the coordinator in Wave 1. File-tree generator verification is a separate tooling gate documented [here](../../../tools/file_tree/README.md), not HOME business coverage.
