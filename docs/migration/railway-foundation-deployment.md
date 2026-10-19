# Railway foundation deployment

Deployed 18 October 2026 (America/Chicago). This records deployment evidence,
separately from the [Part 2 local verification](part-2-foundation.md).

## Release and observed results

- Repository: `Rmorr2001/CODEX_SPD_PROTOTYPE`.
- Deployed commit: `02b146a7f2e7d039e80d0efc1e80c2a37a23fe75`.
- Railway project: `Codex App`, `938376a0-3274-45a3-867c-ce8b26fa6b0d`.
- Environment: `production`, `0a9a78da-0647-46e5-acb9-9213d54186e2`.
- Existing service: `spdwebapp-demo`, `a0aab21a-51ad-4c74-a728-dde169d92f80`.
- Deployment: `a0d3c027-f01a-4c71-aebd-62f410087767`.
- API returned HTTP 200 and deployment status `SUCCESS`; the service's active
  deployment ID matched. Deployment metadata confirmed the exact commit above.
- Startup logs confirmed migrations, 12 fictional members and associated samples,
  and Gunicorn listening on port 8080 with one worker.
- Railway built the React bundle and collected 173 static files.

The first attempt at `5b3b8ba` failed before startup because Railway's Dockerfile
parser rejects `type=secret` mounts. The deployed fix uses ordinary npm/pip install
steps with Railway's native trust. No new service or configuration change was
needed. The successful release was explicitly pinned to the commit; no automatic
deployment triggers were returned. Deployment metadata labels its branch `main`,
while the development branch remains `prototype/railway`; use the confirmed
commit hash to identify this release.

## URLs and remaining verification

- [React workspace](https://spdwebapp-demo-production.up.railway.app/app/)
- [Connection screen](https://spdwebapp-demo-production.up.railway.app/app/connection)
- [Existing chapter application](https://spdwebapp-demo-production.up.railway.app/)
- [Public API status](https://spdwebapp-demo-production.up.railway.app/api/v1/status/)

The cloud proxy rejected the public hostname with `Tunnel connection failed:
403 Forbidden`. Only Railway's API hostname is currently allowed. Consequently,
no public HTTP responses, live browser checks, or independent health-check result
were observed. `SUCCESS` and startup evidence do not establish those checks.
The earlier local image's nine browser checks passed; they are not live evidence.

After allowing the exact demo hostname in the cloud environment, run:

```sh
FRONTEND_TEST_URL=https://spdwebapp-demo-production.up.railway.app npm run test:e2e --prefix frontend
```

Also inspect real status/schema responses and static cache headers. Existing
disposable database, shared persona and session limitations still apply; see
the [demo README](../../SPDWEBAPP/railway_demo/README.md).

No environment-variable values were fetched. Automatic approval review rejected
a broader configuration query because its result might contain protected values;
that query was not executed and was unnecessary for deployment.
