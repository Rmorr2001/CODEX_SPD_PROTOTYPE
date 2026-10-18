# AUTHENTICATE regression tests

Implements all **76 frozen READY designs** from baseline `4b103f6` as 76 discoverable
Django unittest methods. Explicit-package and app-label runs both pass; these
counts describe case mappings, not measured line/branch coverage. The 81 non-READY
designs remain documented and unimplemented.

Read [case-map.json](case-map.json) for executable IDs,
[findings/results](wave-2-findings.md) for approved fixture/source clarifications,
[case index](case-index.md) for the complete design inventory, and
[regression specification](regression-spec.md) for routes/roles/source evidence.
Source/refinement design baselines remain `7e25ac2` / `c8bbc4e`.

Use the coordinator-owned [fixture contract](../../../docs/testing/fixture-contract.md)
and standalone `SPDWEBAPP_CORE.testing` harness. The local
[fixture legend](fixture-notes.md) defines named actors; support.py contains only
thin synthetic media/form helpers and identity-specific state assertions.
No runtime secret_config import, real member database/upload, network or deployment
is required. RegressionTestCase supplies isolated media for every test.

Actual successful commands from repository root:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE.test --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE --noinput
```

Both discover and pass 76 methods. The absolute environment path records this
session's existing environment; it is not a portable installation instruction.
The old empty tests.py was removed. Singular test/ now contains:

- test_sessions.py: credential/session/password and logout CSRF behavior.
- test_profile.py / test_photos.py: own fields, real image bytes and ownership.
- test_majors.py / test_visibility.py: catalog/relations/helpers and dashboard data.
- test_identity.py / test_admin.py: constraints/forms, shared ALL-role sentinel,
  and real core admin permission/logging behavior.
- test_demo.py: actual demo view/URLconf/middleware with explicit HTTPS/token settings.
- test_http_boundaries.py: anonymous, foreign-target and enforced-CSRF matrices.

Test-only role_urls.py puts the production role decorator behind real request
middleware; PARLEYPRO owns integration at its own mounted business routes. Admin
cases use business mode. Demo cases explicitly enable actual demo URLs, boundary
middleware, context processor and secure cookies without weakening permissions.

Shared setup/check instructions are in [AGENTS.md](../../../AGENTS.md).
Earlier `.venv`/railway_demo commands in design history are distinct from the
standalone commands above. Combined validation, original nine demo tests and
mutation probes are coordinator-owned; this README does not claim they ran here.
