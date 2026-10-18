# AUTHENTICATE regression design

Wave 1.5 documentation only; no executable tests or application changes.
Source baseline: `prototype/railway` at `7e25ac2f06b2d88a0220526771585f30df10c57a`.
Refinement baseline: `c8bbc4e`. Cases require coordinator verification.

Start with [inventory/role matrix](regression-spec.md), then
[atomic case index and status counts](case-index.md) and [decisions](decisions.md).
The index maps every one of the original 55 bundled groups to suffixed cases.
Scope includes login/sessions, profiles/images, majors/helpers, visibility,
identity/admin, shared ALL-role gate and demo entry/admin exclusion.

Follow the [refinement contract](../../../docs/testing/wave-1-5-agent-prompt.md),
[fixture contract](../../../docs/testing/fixture-contract.md) and
[root guidance](../../../AGENTS.md). Use the coordinator's shared fixtures/settings;
no parallel factory interface is proposed here. No secret/runtime config reads,
real data/uploads, network or app tests were used in this refinement.

Existing `../tests.py:1–3` is an empty scaffold. Demo integration assertions cover
some rendering, entry, role routing and profile response flags; the
[inventory](regression-spec.md#existing-assertion-evidence) maps their limits.

Current documented commands, repository root with an already configured `.venv`:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
```

These are existing commands, not execution results. The first currently reaches
only placeholder domain tests. Wave 2 adds singular `test/__init__.py`,
`assertions.py`, and `test_sessions.py`, `test_profile.py`, `test_photos.py`,
`test_majors.py`, `test_visibility.py`, `test_identity_admin.py`,
`test_demo_boundary.py`, `test_http_boundaries.py`. Pure helper assertions may
share test_majors.py. Keep business invariants separate from HTTP adapters.

Proposed package discovery command after files and safe settings exist:

```sh
DJANGO_SETTINGS_MODULE=<coordinator-safe-business-settings> .venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE.test
```

The settings argument is a design placeholder, not runnable shell input.
Use corresponding coordinator demo mode for demo cases; verify both explicit
package and app-wide discovery without dropping existing demo assertions.
READY means unambiguous preservation design, not executed or approved coverage.
