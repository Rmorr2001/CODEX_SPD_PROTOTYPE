# Railway browsing demo

Runs the existing application from `smk37git/SPDWEBAPP_ENV`, based on main commit
`004a433`, with its original routes and design. This package owns demo-only
settings, persona entry, demo boundaries, fictional seed records, and tests.
Business models and views remain in HOME, AUTHENTICATE, PARLEYPRO, PHILANTHROPY,
NEWMEMBER, and MISC. No private database or machine-local secret configuration is imported.
Our own `SPDWEBAPP/secret_config.py` provides runtime configuration with inline
comments; it contains no literal secrets and can be edited with this clone.

## Setup and verification

From the repository root:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-demo.txt
export DJANGO_SETTINGS_MODULE=railway_demo.settings
.venv/bin/python SPDWEBAPP/manage.py check
.venv/bin/python SPDWEBAPP/manage.py migrate --noinput
.venv/bin/python SPDWEBAPP/manage.py seed_railway_demo
.venv/bin/python SPDWEBAPP/manage.py collectstatic --noinput
.venv/bin/python SPDWEBAPP/manage.py test railway_demo
.venv/bin/python SPDWEBAPP/manage.py makemigrations --check --dry-run
```

There is no configured lint, formatting, or type-checking tool. Existing business
app tests are scaffold placeholders; the demo tests exercise real seeded routes,
role boundaries, CSRF protection, seed idempotency, and interactive profile/voting/request flows.

## Deployment and data lifecycle

The root Dockerfile installs the repository's existing pinned requirements plus
Gunicorn/WhiteNoise. It collects existing static assets, then starts as a non-root
user. Startup migrates a separate SQLite database and seeds 12 fictional users
and profiles, executive roles, dashboard links, banner/rush images from public
repository assets, announcements, polls, service hours, and new-member marks.
Repeated seeds upsert known samples; existing usable or privileged demo
credentials cause an error. Seed records use `example.invalid` emails and unusable
passwords. No shared password or administrator is created.

Use **Enter demo** in the banner to select executive, active, new-member, or
alumni browsing. POST entry is CSRF-protected; the original application workflows
remain interactive against fictional data. Administrator access is blocked.
All visitors share the selected demo persona and its sample changes. This is not
a full production deployment.

Storage is disposable, with no persistent volume. Replacement resets the data;
startup refreshes the known sample fields. A single worker uses an ephemeral
in-memory key unless a stable secret binding is supplied, so sessions expire on
restart. The original application settings and routes are preserved; demo settings load
only our explicitly selected secret_config.py.

Configuration keys (never document values): `DJANGO_SETTINGS_MODULE`,
`DEMO_DATABASE_PATH`, `DEMO_MEDIA_ROOT`, `RAILWAY_PUBLIC_DOMAIN`, `PORT`, and
`DJANGO_SECRET_KEY`. The public hostname supplies allowed-host validation.
Railway terminates TLS; secure cookies and the forwarded-protocol header remain
configured. The original home page is the deployment health check.

Longer integration or architecture notes belong in this package's `docs/` when
needed. Keep this README authoritative for the demo; link to it elsewhere.
