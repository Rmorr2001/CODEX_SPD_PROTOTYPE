# Versioned API composition

Framework delivery for `/api/v1/`; business behavior stays in its owning domain.
DRF and drf-spectacular are pinned alongside the unchanged Django 6.1.1 version.

- `urls.py`: mount versioned contracts and the JSON-only unknown-path boundary.
- `views.py`: public liveness serializer/view and consistent unknown API errors.
- `test/`: real dispatch, schema, methods, namespace isolation and permission defaults.

`GET /api/v1/status/` returns exactly `{"status":"ok","api_version":"v1"}`.
It is a public, noncached liveness check, with no database query or member data;
it does not prove database readiness. `GET /api/v1/schema/` returns OpenAPI JSON
for the current public status contract. Unmatched `/api/` paths return JSON 404s,
including unknown versions and non-GET methods. They never use the SPA fallback.

`web_settings.py` supplies JSON rendering, SessionAuthentication and deny-anonymous
IsAuthenticated defaults. Public status/schema/error boundaries opt out explicitly.
SessionAuthentication's current anonymous denial is 403. Future domain endpoints
must define their own action/object permissions; this foundation does not add
login, current-user or write endpoints. Anonymous login CSRF remains future work.

From the repository root:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py test SPDWEBAPP_CORE.api.test --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py spectacular --file work/openapi.yaml --validate --fail-on-warn
```

These tests use synthetic settings and fixtures, no runtime credentials.
The [combined audit](../../../docs/testing/README.md) also discovers this package.
Update serializers, contract documentation and meaningful tests together.
