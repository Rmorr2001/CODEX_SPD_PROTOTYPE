# React workspace

Owns the new member-interface shell at `/app/`. Existing Django pages remain
available at their original URLs. React 19, TypeScript 7, Vite 8 and React Router 7
are pinned in `package.json` and `package-lock.json`; use Node 24.19.0.
The [screen plan](../docs/design/screen-plan.md) maps the public and member read
screens to their design/spec references. The [delivery log](../docs/design/delivery-log.md)
records per-screen acceptance and screenshots. Business writes remain clearly
linked to the original Django forms; a read screen is not a migrated transaction.

## Structure and boundaries

- `src/app/`: application composition, router, public legacy links and styles.
- `src/api/client.ts`: same-origin JSON request and runtime status-contract validation.
- `src/components/ServiceConnection.tsx`: loading, connection, error/retry and cancellation.
- `src/domains/public/`: public page presentation, validated HOME content,
  red/black layout and domain-local `test/`. See its README.
- `src/domains/identity/`: session/access states, member shell, dashboard,
  directory and own profile, with its README and browser `test/`.
- `src/domains/decisions/`: Aye/Nay motion presentation and aggregate/stored
  results; voting remains linked to the existing chapter workflow.
- `src/api/read.ts` and `links.ts`: shared authenticated read/cancellation states
  and safe presentation URLs. Domain clients validate their own payload contracts.
- `test/`: Playwright checks against actual built assets and Django, including a
  real seeded legacy page. Network interception is limited to loading/error cases.

Future business features belong in descriptive domain folders with colocated
`test/`, README and optional `docs/`, proportionate to their responsibilities.
Framework composition stays in `app/`; server authorization remains in Django.

## Setup and local preview

From the repository root, install Python test requirements into `.venv`, then:

```sh
npm ci --prefix frontend
npm run build --prefix frontend
FRONTEND_TEST_PORT=8000 .venv/bin/python tools/testing/serve_frontend.py
```

Open `http://127.0.0.1:8000/app/`. This fixture server uses standalone synthetic
settings, a temporary SQLite database/media/static directory, fictional seeded
members and no runtime secret configuration. It resets when stopped and is not
for real accounts or member data. The existing site remains at `/`.

For hot reload, keep that backend running and start a second terminal:

```sh
npm run dev --prefix frontend
```

Open `http://127.0.0.1:5173/app/`. Vite serves source assets from `/` in development
and proxies `/api` and `/media` to port 8000. Legacy links open Django's origin.
The production build uses `/static/app/` and same-origin relative API URLs.

## Checks

```sh
npm run typecheck --prefix frontend
npm run format:check --prefix frontend
npm run build --prefix frontend
cd frontend
npx playwright install --with-deps chromium
PYTHON_EXECUTABLE=../.venv/bin/python npm run test:e2e
```

`npm run test:e2e` starts `tools/testing/serve_frontend.py` on loopback port 8765,
waits for the API, and stops it afterward. Build first. `PYTHON_EXECUTABLE` selects
an installed Python environment; `FRONTEND_TEST_PORT` changes the fixture port.
`FRONTEND_TEST_URL` targets an already running isolated image instead of starting
that fixture server. `PLAYWRIGHT_CHROMIUM_EXECUTABLE` optionally selects a local
Chromium binary; CI installs Playwright's matching browser. Traces are retained on
failure under ignored `test-results/`. No frontend linter is configured.

## Production and configuration

The Docker Node stage builds `dist/`; only built files reach the Python runtime.
Django serves its fixed `index.html`, and WhiteNoise serves content-hashed assets.
The shell revalidates; hashed assets are immutable. Refreshing a React deep link
stays within `/app/`; missing `/api/` routes return JSON 404s.

No application secret belongs in `VITE_*`: those values are public bundle content.
The current client needs no custom frontend environment values and stores no
bearer token. API authentication/session adapters are the next increment.
See [foundation delivery](../docs/migration/part-2-foundation.md) for Docker,
backend contracts and verification limits.
