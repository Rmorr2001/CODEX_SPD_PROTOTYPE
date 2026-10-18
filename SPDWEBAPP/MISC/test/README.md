# MISC regression testing

Design only: 30 original groups refined into 103 named designs, with 80 READY,
20 POLICY_BLOCKED, 2 NEEDS_FIX and 1 INFRA_BLOCKED. None was executed.
Source baseline is `7e25ac2`; refinement baseline is `c8bbc4e`.

Start with the [specification](regression-spec.md) and
[case/status index and complete parent mapping](case-index.md).
The [Wave 1.5 contract](../../../docs/testing/wave-1-5-agent-prompt.md) and
[shared fixtures](../../../docs/testing/fixture-contract.md) govern implementation.

MISC owns announcements, Chicago calendar utility, alert tag/fragments and both
models' admin cases. AUTHENTICATE owns dashboard access; HOME currently renders
neither alert. MISC.urls is empty and unmounted. Do not invent a public endpoint.

Existing `../tests.py` is a scaffold. Demo tests check dashboard status/access and
admin blocking without MISC semantic assertions. No measured coverage is claimed.

Current documented commands from repository root (not run in this refinement):

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py check
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test MISC
```

Proposed Wave 2 commands target `MISC.test` explicitly and `MISC` app-wide,
using the coordinator's future shared `business` settings module; verify discovery
without duplicate counts. That module path is not selected here. Use shared
`demo` settings for the boundary case, not production secret imports or a change
to public admin protection. No fixture helper/settings/discovery package exists yet.

Proposed layout: `test/__init__.py`, `assertions.py`, `test_models.py`,
`test_dst.py`, `test_alert_tag.py`, `test_rendering.py`, `test_admin.py`,
`test_transactions.py`. Existing placeholder `tests.py` stays unchanged in this wave.
Business assertions remain separate from legacy HTML/redirect adapters.

Setup requires migrated disposable DB, existing Django/pytz dependencies,
explicit synthetic users/profiles/permissions, shared CSRF clients and consumed
aware clocks. Only browser capture is an infrastructure-only blocker; optional
PostgreSQL races first need Q10 policy. Follow the spec's Wave 2 order; no code,
application tests, installs, Git mutations or shared harness changes are included.
