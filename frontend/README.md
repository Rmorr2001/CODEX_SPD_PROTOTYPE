# React workspace

Owns the React public/member experiences at `/app/`, including poll and service
transactions. `/` redirects here; original Django home is `/legacy/`, and other
legacy deep links remain. React 19, TypeScript 7, Vite 8 and React Router 7
are pinned in `package.json` and `package-lock.json`; use Node 24.19.0.
The [screen plan](../docs/design/screen-plan.md) maps the public and member read
screens to their design/spec references. The [delivery log](../docs/design/delivery-log.md)
records per-screen acceptance and screenshots. The [functional milestone](../docs/migration/functional-milestone-1.md) adds
shared poll/service writes; marks and account edits still use explicit legacy links.

## Structure and boundaries

- `src/app/`: application composition, router, public legacy links and styles.
- `src/api/client.ts`: same-origin JSON request and runtime status-contract validation.
- `src/components/ServiceConnection.tsx`: loading, connection, error/retry and cancellation.
- `src/domains/public/`: public page presentation, validated HOME content,
  red/black layout and domain-local `test/`. See its README.
- `src/domains/identity/`: session/access states, member shell, dashboard,
  directory and own profile, with its README and browser `test/`.
- `src/domains/decisions/`: Aye/Nay motion presentation and aggregate/stored
  results, real ballots, executive creation/closure and live refresh.
- `src/domains/service/`: own academic-year hours, approved totals and event
  statuses, fractional submissions, chair review/edit and approved reports.
- `src/domains/new-members/`: personal approved marks, active-member summaries
  and a limited board-only handoff; no invented milestone/eligibility engine.
- `src/api/write.ts`: CSRF-protected JSON mutations with explicit pending/error
  behavior and no automatic retries.
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
PYTHON_EXECUTABLE=../.venv/bin/python npm run test:e2e -- --workers=1
```

`npm run test:e2e` starts `tools/testing/serve_frontend.py` on loopback port 8765,
waits for the API, and stops it afterward. Build first. A bounded global setup waits for the status contract before any
scenario, including when targeting a newly started Docker image. `PYTHON_EXECUTABLE` selects
an installed Python environment; `FRONTEND_TEST_PORT` changes the fixture port.
`FRONTEND_TEST_URL` targets an already running isolated image instead of starting
that fixture server. `PLAYWRIGHT_CHROMIUM_EXECUTABLE` optionally selects a local
Chromium binary. Use one worker for the full suite so the single global poll
lifecycle scenario cannot race read scenarios; CI installs Playwright's matching browser. Traces are retained on
failure under ignored `test-results/`. No frontend linter is configured.

## Production and configuration

The Docker Node stage builds `dist/`; only built files reach the Python runtime.
Django serves its fixed `index.html`, and WhiteNoise serves content-hashed assets.
The shell revalidates; hashed assets are immutable. Refreshing a React deep link
stays within `/app/`; missing `/api/` routes return JSON 404s.

No application secret belongs in `VITE_*`: those values are public bundle content.
The client needs no custom frontend environment values and stores no bearer token.
Member reads reuse Django session cookies. `/app/login` provides existing-account
sign-in and a native CSRF-protected demo-role form when demo mode is enabled.
During Vite development, demo entry links to Django's origin to preserve CSRF
origin checks; the built application uses one origin. No DRF password-login API is introduced; poll and service write APIs now share the same
Django session and CSRF boundaries.
See [foundation delivery](../docs/migration/part-2-foundation.md) for Docker,
backend contracts and verification limits.

## Member experience migration

[The state/UI migration plan](../docs/migration/react-experience-next.md) records
confirmed updates, bounded three-second refresh, and selected A+C implementation.
Tailwind4 now styles the common member shell, combined poll card and Radix service
Sheet through reviewed shadcn-style primitives. Preflight is omitted to preserve
unmigrated domain/public CSS. No Zustand store or new business fields are added.
The plan records reference provenance, keyboard/draft protections, preview commands
and test evidence separately from live deployment verification.
