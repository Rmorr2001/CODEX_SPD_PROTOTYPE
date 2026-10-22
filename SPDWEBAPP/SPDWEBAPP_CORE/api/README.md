# Versioned API composition

Framework delivery for `/api/v1/`; business behavior stays in its owning domain.
DRF and drf-spectacular are pinned alongside the unchanged Django 6.1.1 version.

- `urls.py`: mount versioned contracts and the JSON-only unknown-path boundary.
- `views.py`: public liveness serializer/view and consistent unknown API errors.
- `test/`: real dispatch, schema, methods, namespace isolation and permission defaults.

`GET /api/v1/status/` returns exactly `{"status":"ok","api_version":"v1"}`.
It is a public, noncached liveness check, with no database query or member data;
it does not prove database readiness. `GET /api/v1/schema/` returns OpenAPI JSON
for all currently mounted contracts. Unmatched `/api/` paths return JSON 404s,
including unknown versions and non-GET methods. They never use the SPA fallback.

`web_settings.py` supplies JSON rendering, SessionAuthentication and deny-anonymous
IsAuthenticated defaults. Public status/schema/error boundaries opt out explicitly.
SessionAuthentication's anonymous denial is 403. Domain endpoints define their
own action/object permissions and explicit response whitelists; see their READMEs
and the [screen plan](../../../docs/design/screen-plan.md). Session and caller
read endpoints now reuse existing Django cookie authentication. The demo entry
form posts to the original CSRF-protected endpoint with a narrowly allowlisted
React return path; no DRF business write or password-login API is introduced.

From the repository root:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py test SPDWEBAPP_CORE.api.test --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py spectacular --file work/openapi.yaml --validate --fail-on-warn
```

These tests use synthetic settings and fixtures, no runtime credentials.
The [combined audit](../../../docs/testing/README.md) also discovers this package.
Update serializers, contract documentation and meaningful tests together.

`links.py` owns the shared safe presentation-link guard used by public and
member read models. It rejects executable/protocol-relative/malformed URLs and
embedded credentials; domain serializers still whitelist every returned field.

Schema enum names distinguish public liveness from request approval statuses in
`web_settings.py`. The service serializer uses its model's existing status choices;
this changes schema naming, not stored values. The schema contract test locks the
current eleven GET-only paths and their public/optional/protected authentication.
