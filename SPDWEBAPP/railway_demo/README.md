# CODEX-SPD-PROTOTYPE Railway demo

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

The [backend regression suite](../../docs/testing/README.md) now implements the
reviewed READY cases. The demo tests additionally exercise real seeded routes,
roles, CSRF, seed idempotency and interactive profile/voting/request flows.
Frontend build, formatting, type and browser checks are documented in
[frontend/README](../../frontend/README.md); Python has no lint/type tooling.

## Deployment and data lifecycle

The root Dockerfile installs the repository's existing pinned requirements plus
Gunicorn/WhiteNoise and the API dependencies. A Node build stage supplies the
bundled React assets for `/app/`; static collection uses secret-free build settings.
The final Python image runs as a non-root user. Startup migrates a separate SQLite database and seeds 12 fictional users
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
configured. The original home page remains the Railway health check. `/api/v1/status/` is
an additional database-independent liveness contract; `/api/v1/schema/` documents
the current API. `FRONTEND_DIST_DIR` identifies the image-owned HTML/asset build
directory. See [Part 2](../../docs/migration/part-2-foundation.md).

Longer integration or architecture notes belong in this package's `docs/` when
needed. Keep this README authoritative for the demo; link to it elsewhere.


## Interactive file tree

Open `/static/railway_demo/file-tree.html` on the demo host. Each Docker build
regenerates it from that build's clean source context before static collection;
it no longer embeds a committed, manually maintained file list. Refresh the page
after a deployment to see file additions, removals, and metadata changes. It is
not a live filesystem view between builds. The URL revalidates on refresh.

`tools/file_tree/` owns the generator, purpose labels, viewer source, and checks.
It lists file paths, descriptions, symbol names, and line counts, not credentials
or private database data. It never imports application code to inspect files and
never reads configuration file contents. Generated files, private runtime data,
virtual environments, and outside symlinks are excluded.

When Railway provides `RAILWAY_GIT_COMMIT_SHA` as a build argument, the viewer
shows and links to that commit. Otherwise it labels a digest of the source
manifest and links to the configured demo branch without inventing a commit.

Notes and review marks are keyed by repository and file path in the browser,
not by deployment commit. The viewer reads the old snapshot keys automatically
and keeps the originals. Notes for removed paths remain in exports. Storage is
browser-local, so copy/export notes to share or back them up. The browser view
works independently of the ChatGPT embed.

See [the generator README](../../tools/file_tree/README.md) for manual build and
verification commands.
