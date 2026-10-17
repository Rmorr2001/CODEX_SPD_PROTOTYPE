# MISC regression testing

Wave 1 is source inspection and proposed pseudocode only, pending coordinator
verification. No application tests were run and no coverage percentage is claimed.

MISC owns announcement records, Chicago DST calculation, alert selection,
fragment rendering, and the two models' admin behavior. The dashboard is an
AUTHENTICATE interface; HOME currently does not render these alerts. There is no
mounted MISC public endpoint. See the [regression specification](regression-spec.md)
for operation/case mapping, defects, transaction/audit contributions and decisions.
Follow the [shared Wave 1 contract](../../../docs/testing/wave-1-agent-prompt.md)
and [six-domain map](../../../docs/testing/README.md).

`../tests.py` is an empty Django scaffold. Existing `railway_demo/tests.py`
checks dashboard access/status and demo admin blocking, without MISC content,
clock, model, permission or failure assertions.

Proposed Wave 2 layout (not created):

```text
test/
  __init__.py
  assertions.py                 # business invariants, reusable after migration
  test_models.py
  test_dst.py
  test_alert_tag.py
  test_rendering.py
  test_admin.py
  test_transactions.py
```

From repository root, existing documented commands use an already configured
isolated `.venv` and synthetic demo settings:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py check
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test MISC
```

The last command currently discovers no meaningful MISC assertions. Proposed
explicit command after implementation is the same prefix followed by
`SPDWEBAPP/manage.py test MISC.test`; verify both app-label and package discovery
without double counting. C03 admin HTTP tests require coordinator-owned isolated
test settings that permit the real admin URL, rather than the public-demo
middleware's intentional 403. Use the shared settings module name only once
agreed; do not change deployed settings to run tests.

Setup needs Django/pytz from existing dependencies, migrated disposable database,
minimal users with explicit profile/roles and Django permissions, controlled aware
clock, and shared baseline isolation. No network, real accounts, member data,
uploads, dependency installation, CI, shared harness or executable tests are part
of this wave. Coordinator runs the shared baseline. Read the ordered Wave 2
checklist before implementing.
