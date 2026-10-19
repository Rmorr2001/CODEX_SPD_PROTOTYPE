# HOME regression tests

Wave 2 implements all **63 frozen READY cases** from baseline `4b103f6` as 63
named tests. Both `HOME.test` and `HOME` discover and pass all 63 with no skips or
expected failures. [case-map.json](case-map.json) maps each design ID to its exact
unittest method. A discovery check confirmed both labels match that map exactly.
This is design-case accounting, not a measured source-coverage percentage.

The other 34 designs remain unimplemented blockers: 6 NEEDS_FIX, 26 POLICY_BLOCKED
and 2 INFRA_BLOCKED. See the [case/status index](case-index.md),
[original inventory and decisions](regression-spec.md), and
[implementation findings](wave-2-findings.md). No business policy or runtime code changed.

Scope: C01 public pages/content, C04 successful singleton/model persistence,
HOME C03 Django admin/permissions/CSRF/reordering, D02 fictional seed integration,
and D03 media/composition. Demo implementation remains in `railway_demo`;
AUTHENTICATE owns persona entry/demo admin blocking. HOME seed tests inspect
other domains' seeded fields/relations without duplicating their permission suites.

From repository root, the actual isolated commands used in this workspace are:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test HOME.test --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test HOME --noinput
```

Final package run: 63 tests, 15.240s, OK. App-label run: 63 tests, 7.747s, OK.
Both runs reported no system-check issues. The environment path is local to this
workspace; substitute an interpreter with the repository's dependencies elsewhere.
The coordinator owns combined execution, the existing nine demo tests, mutation
probes and the cross-domain mapping audit.

| File | Purpose |
| --- | --- |
| [test_public_pages.py](test_public_pages.py) | Real public routes/templates, exact roles, ordering, escaping and CSRF |
| [test_content_models.py](test_content_models.py) | Successful ORM persistence, validation, boundaries and repeat deletion |
| [test_admin.py](test_admin.py) | Real admin permissions, forms, CRUD/logs, JSON ordering and injected DB failure |
| [test_demo_seed.py](test_demo_seed.py) | Exact fictional seed fields, stable identity, unrelated state and source/media boundaries |
| [test_seed_failures.py](test_seed_failures.py) | TransactionTestCase refusals, partial DB rollback, IO failures and retry |
| [test_media_composition.py](test_media_composition.py) | Temporary-media serving, traversal, static references, demo shell and pure cache headers |
| [helpers.py](helpers.py) | Thin synthetic image/model constructors and standard-library HTML parser |

`test/__init__.py` enables singular-package discovery. The obsolete empty
`HOME/tests.py` was removed after package discovery was established.

Tests use the [shared fixture contract](../../../docs/testing/fixture-contract.md)
and safe `SPDWEBAPP_CORE.testing` settings. They use real models, templates,
auth/session/message/CSRF middleware, synthetic users/images, temporary Path media,
controlled clocks and refreshed state assertions. Seed cases explicitly enable
DEMO_MODE, default DEMO_PUBLIC_DOMAIN to None, and use a temporary synthetic source
root. No runtime config, real uploads/member DB, network or deployment is used.

The media test URLconf intentionally binds the same real `django.views.static.serve`
view to each test's temporary document_root, because core URLs capture MEDIA_ROOT
at import. Demo cases explicitly install actual demo URL/middleware/context settings.
Only deliberate IO/DB failures or file-copy observation boundaries are mocked.
DB rollback assertions never claim filesystem compensation. PostgreSQL races,
file-retention policy, browser/static integration and unsafe behavior remain blocked.

[File-tree generator verification](../../../tools/file_tree/README.md) is a separate
tooling gate and is not counted as new HOME business coverage.

## Part 1 hardening

[The hardening results](../../../docs/testing/part-1-hardening.md) record the
stronger preservation assertions, clean-suite results and required mutation kills.
The historical Wave 2 findings above retain their original counts and evidence.
