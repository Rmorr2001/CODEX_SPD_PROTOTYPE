# AUTHENTICATE regression design

Wave 1 source inspection only; proposed cases have not been implemented or run.
This specification requires coordinator source verification before Wave 2.

Scope: member login/logout/password/session behavior, own profile and images,
major catalog/selection, dashboards and rosters, filter/cleanup helpers, shared
identity/role/admin boundaries, demo persona entry and demo admin exclusion.
See [regression-spec.md](regression-spec.md) for 14 operation groups and 55 named
case specifications, including parameterized boundary cases.

Follow the [shared Wave 1 contract](../../../docs/testing/wave-1-agent-prompt.md),
[root guidance](../../../AGENTS.md), and [testing map](../../../docs/testing/README.md).
Inspected branch `prototype/railway`, commit
`7e25ac2f06b2d88a0220526771585f30df10c57a`.

Existing `../tests.py:1–3` is an empty scaffold. `railway_demo/tests.py` provides
limited integration assertions for rendering, anonymous redirects, demo entry,
role routing and one profile response; these do not verify most persisted profile
state or the failure/ownership boundaries here. See the assertion map in the spec.

Proposed layout, created only in Wave 2:

```text
test/
  __init__.py
  assertions.py             # reusable business state assertions
  test_sessions.py          # A01–A03, S01–S02
  test_profile.py           # A04, A10
  test_photos.py            # A05–A06
  test_majors.py            # A07–A08, A11
  test_visibility.py        # A09
  test_identity_admin.py    # C03
  test_demo_boundary.py     # D01, admin portion of D03
```

Use real ORM `TestCase`; pure string helpers use `SimpleTestCase`; commit/failure
and PostgreSQL concurrency cases may need `TransactionTestCase`. Agree on shared
minimal factories, safe test settings and temporary media before implementation;
do not seed the executive persona for ordinary domain cases. No network, real
uploads, credentials or production data. Core and demo URL/middleware modes must
be independently selectable. Source settings reference runtime config; do not
open its values. See the proposed interface in the spec.

Current documented commands, from repository root with an already configured
`.venv` (not executed by this agent):

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
```

The first currently discovers the placeholder, not the proposed suite. Proposed
Wave 2 command, after adding `test/__init__.py` and verifying discovery:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE.test
```

A shared isolated test-settings module, if approved, should replace the settings
argument for non-demo cases; its name/location remain coordinator-owned. Confirm
whether default/app-label discovery reaches singular `test/`. No numerical
coverage measurement, application tests, lint or type checks were run in Wave 1.
