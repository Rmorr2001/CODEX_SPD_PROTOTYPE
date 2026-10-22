# Part 2 DRF and bundled React foundation

This increment adds a working React shell and versioned JSON composition beside
the existing Django app. Models, migrations, legacy routes and business rules
remain unchanged. No live Railway service or configuration is modified.

## Delivered structure

| Area | Current implementation |
| --- | --- |
| `SPDWEBAPP_CORE/api/` | JSON liveness, OpenAPI schema, fail-closed permission defaults, JSON 404 boundary and tests |
| `SPDWEBAPP_CORE/frontend/` | Fixed HTML shell, isolated `/app/` fallback, asset-cache rule and tests |
| `SPDWEBAPP_CORE/web_settings.py` | Shared composition settings for actual and standalone test configurations |
| `SPDWEBAPP_CORE/build_settings.py` | Static-only image assembly without runtime secrets or database access |
| `frontend/` | React/TypeScript/Vite application, router, validated API client, loading/error/retry states and browser checks |
| `tools/testing/serve_frontend.py` | Loopback-only synthetic Django/demo fixture server for local development and browser checks |

Runtime dependencies are pinned: DRF 3.18.3 and drf-spectacular 0.30.0 with the
existing Django 6.1.1. New schema dependencies are pinned too. React/React DOM
19.3.1, Vite 8.3.4, TypeScript 7.0.2 and React Router 7.18.4 are recorded in the
npm lockfile. Node 24.19.0 is used for the build and CI.

## Routing and runtime

```text
Existing web service / Python image
  /                         existing Django site
  /auth/, /poll/, ...       existing Django workflows
  /app/                     built React workspace
  /app/connection           refreshable React route
  /api/v1/status/           public JSON liveness
  /api/v1/schema/           OpenAPI JSON
  /api/<unmatched>          JSON 404
  /static/app/assets/       compiled content-hashed JS/CSS via WhiteNoise
```

The shared API client uses same-origin cookies and validates untrusted JSON before
rendering. No browser-stored bearer token or session-login endpoint is introduced.
Unknown React routes display a useful missing-page state; they do not swallow API
errors. The legacy site remains linked and operational during coexistence.

The Dockerfile has three build stages: Node builds React, Python generates the
source explorer, and the final Python image installs the backend and collects
static assets. Build stages are not additional production services. Gunicorn is
still the only web process, with the existing one-worker fictional demo startup.
Source files are copied with web-user ownership so restrictive cloud-checkout
permissions cannot prevent non-root startup. Node is absent from the runtime.

Static collection uses explicit build settings without importing `secret_config`.
Railway builds use native CA trust without session-specific CA or secret build
arguments. Its Dockerfile parser rejects secret mounts, even optional ones; the
first live packaging attempt identified this and the deployment Dockerfile now
uses plain install steps. The existing `railway.json` and root health path stay
unchanged.

## Commands and configuration

[Frontend setup](../../frontend/README.md) is authoritative for npm, hot reload,
type-checking, formatting and browser commands. Backend test commands are in
[API composition](../../SPDWEBAPP/SPDWEBAPP_CORE/api/README.md),
[frontend delivery](../../SPDWEBAPP/SPDWEBAPP_CORE/frontend/README.md) and the
[combined testing map](../testing/README.md). No Python lint/type checker is added.

```sh
docker build -t codex-spd-foundation .
docker run --rm -p 127.0.0.1:8766:8000 codex-spd-foundation
FRONTEND_TEST_URL=http://127.0.0.1:8766 npm run test:e2e --prefix frontend
```

Open `http://127.0.0.1:8766/app/`. These commands run an isolated local image, not
a Railway deployment. For local builds behind the cloud proxy, use a temporary
Dockerfile copy with trusted public CA secret mounts on npm/pip install steps
and their `NODE_EXTRA_CA_CERTS`/`PIP_CERT` settings. Keep that local adaptation
outside the repository and preserve TLS verification; never copy the CA or
credential bindings into the runtime image.
Runtime keys are described in the demo README; the new non-secret build-location
key is `FRONTEND_DIST_DIR`. Frontend `VITE_*` values are public; no secrets are
passed to the frontend bundle. Existing disposable SQLite/media and session-key
limitations remain; this increment does not authorize real member data storage.

## Verification scope

Meaningful backend checks cover real JSON/status/schema/method dispatch, secure
default permissions, fixed shell-file selection, controlled missing-build errors,
API/SPA namespace separation and actual WhiteNoise cache headers. Browser checks
load compiled assets and exercise real API calls, refresh, legacy navigation,
small screens, loading and three failure/retry cases. Only error/loading responses
are intercepted; the connected path uses the actual Django service.

The combined audit includes the two new composition test packages while retaining
all 393 READY case mappings and 284 blocked designs. The existing 13 mutation gates
remain required. GitHub Actions builds/type-checks/checks formatting of the frontend, runs the
backend audit, demo and mutation suites, validates OpenAPI, builds a Docker image
and runs browser checks against that image. It uploads JSON, schema, coverage and
failure traces; a hosted CI run is not implied by successful local execution.

Next comes live Railway packaging verification, then session authentication and a
policy-cleared read-only roster pilot. No DRF business adapters, new permissions,
React business screens, schema/data migrations or production cutover are included.

## Actual local results

Subsequent Railway deployment and its remaining live-verification limitation are
recorded in the [deployment evidence](railway-foundation-deployment.md).
The later nine-screen redesign is tracked separately in the
[screen delivery log](../design/delivery-log.md); its read adapters and demo
session entry extend this foundation without rewriting the legacy transactions.

Completed 18 October 2026 (America/Chicago), from baseline `79cff62`:

| Check | Result |
| --- | --- |
| New API/frontend Python package tests | 14 passed |
| Combined regression audit | 419 passed in 77.529s; 393/393 frozen READY IDs verified |
| Existing demo tests | 9 passed |
| Required effectiveness probes | 13/13 caught by assertions; clean/restored passes and zero errors |
| Source explorer | 5 passed |
| TypeScript, Prettier, Vite production build | Passed |
| OpenAPI validation with fail-on-warn | Passed |
| Python dependency consistency / migration drift | No broken requirements / no changes detected |
| Browser suite with synthetic Django fixture server | 9 passed |
| Final Docker image and browser suite | Built; 9 passed in 18.4s |
| Vite development routing/proxy | Deep-link refresh and actual API connection passed |

The final image ran as UID 1000 with no Node executable. Actual HTTP checks
observed shell `200` with `no-cache`, hashed JavaScript `200` with immutable
caching, and the exact public status payload. Desktop/mobile rendering was
inspected, and the browser suite checks mobile overflow and legacy navigation.
The [JSON evidence](part-2-evidence.json) records counts, headers and image ID.
Python coverage now includes the new delivery packages; earlier percentages used
a smaller source scope. Frontend source coverage is not measured by that report.

The container exercise first exposed restrictive source-copy permissions blocking
the non-root user from reading `manage.py`. Image-owned source copies now belong
to the web user; the rebuilt image and final browser checks passed. An earlier
cache test also rejected a dotted-string WhiteNoise hook (treated as a regex);
the shared settings now pass the callable and real cache-header tests pass.

Cloud build verification retained proxy/CA trust and used a writable
`BUILDX_CONFIG` under `work/` when the default home-directory state was read-only.
Docker credentials/proxy configuration were not replaced. The final build used
locked npm installation and a public CA secret mount; no runtime secret was
provided to the build. This verifies a local image, not a live Railway release.
