# Functional migration milestone 1

Implementation on `prototype/railway`, based on deployed commit8749c4a.
This document describes the pending release; it does not assert that these changes
are deployed or that live browser QA passed. Marks/account mutations remain future
work. Historical nine-screen evidence remains in `docs/design/verification.json`.

## Result and architecture

The same chapter poll and service records work through both interfaces. React is
the primary landing: `/` redirects to `/app/`; original home is `/legacy/`.
Existing `/auth/`, `/poll/`, `/philanthropy/`, `/newmember/`, `/rush/`, history and
ethics deep links remain. Links explicitly label Django HTML/CSS versus React.
Root health changes to `/api/v1/status/` so a redirect is not used as readiness.

Legacy `urls.py`/`views.py` are HTML adapters. Each migrated domain has distinct
`api/urls.py`, serializers, read and command adapters. Shared `operations.py`
owns validation, role checks and atomic writes; both fronts call it. AUTHENTICATE
owns the common domain-role interface. CORE translates validation/permission/
conflict errors into JSON400/403/409; no database internals are returned.

Password login honors safe local return paths, otherwise selects the caller's
React landing. Demo entry defaults to React and retains narrowly allowlisted
legacy return paths. GET logout confirms without changing state; CSRF-protected
POST ends the session and returns to React. Denied role routes never redirect to
themselves or an external Referrer. React remains mounted at `/app/` for direct
refreshes; no change to Vite asset base or Docker copy paths is needed.

## Complete flows

- [Polls](../../SPDWEBAPP/PARLEYPRO/README.md): create, list/detail, cast/change
  Aye/Nay, refresh results, executive close and saved historical totals.
- [Service](../../SPDWEBAPP/PHILANTHROPY/README.md): fractional submission,
  pending queue, chair approve/deny/edit, own statuses, approved academic/lifetime
  totals, chapter statistics/member histories and numeric XLSX export.
- React read/write → legacy read, and legacy write → React read use the same
  fictional records. There is no parallel mock store.

## Policy boundaries

The user clarified parallel means the same poll in both fronts, not independently
concurrent polls. One open motion is enforced by supported operations; historical
out-of-band multiple-open rows retain newest-first reads. ACTIVE votes;
ACTIVE+EXEC creates/closes chapter-wide. Existing global tally membership is
preserved; no quorum/majority policy is invented.

Fractional service storage was explicitly authorized. Minimum0.5 and two-decimal
precision are explicit contracts. Self-review and decision reversals are pending
user clarification and fail closed in both interfaces. Existing chair-only edits,
ACTIVE approved member history and authenticated approved export scope remain;
these are documented compatibility boundaries, not production policy endorsement.

The original frozen READY tests remain mapped. Expectations changed only for
intentional root/login destinations, POST logout, safe denial fallback,
newly supported REST verbs/schema, decimal storage/form step, the model-clock isolation target after operation extraction, and the conditional
update failure-injection point. New tests exercise the changed safety contracts.
Blocked legacy designs are not silently promoted to passing policy guarantees.

## Migrations and release review

1. PARLEYPRO0006 adds an internal singleton workflow-lock table. It serializes
   global-ballot transitions including create with no currently open row.
2. PHILANTHROPY0005 changes integer hours to Decimal(10,2). Existing integer values
   and statuses survive upgrade. Lost historic fractions cannot be reconstructed.
   Downgrade refuses fractional data rather than truncating it.
3. Docker startup already migrates and seeds the isolated SQLite demo. No new
   service, volume, credentials or external API is required. Keep one replica and
   the existing non-root image/start command. Existing ephemeral-data and session
   reset behavior remains documented in railway_demo/README.md.
4. This branch auto-deploys on push: review and authorize release before pushing.
   Read back the effective Railway health path (`/api/v1/status/`); an explicit
   service override may otherwise retain the old `/` value.
5. Do not point these migrations at real production data as part of this demo.
   Public live QA remains blocked until the runtime permits the exact demo host.

## Verification

Use root AGENTS.md setup commands. Main evidence commands:

```sh
python -m coverage run tools/testing/run_regressions.py --report work/milestone-regressions.json
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.demo_settings python -m coverage run --append SPDWEBAPP/manage.py test railway_demo --noinput
python tools/testing/probe_regressions.py
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings python SPDWEBAPP/manage.py spectacular --file work/milestone-openapi.yaml --validate --fail-on-warn
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings python SPDWEBAPP/manage.py makemigrations --check --dry-run
npm run build --prefix frontend
npm run format:check --prefix frontend
PYTHON_EXECUTABLE=/path/to/venv/bin/python PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium npm run test:e2e --prefix frontend -- --workers=1
```

The browser suite uses actual bundled assets and a disposable synthetic Django
server. One worker prevents read scenarios racing the single-global-poll lifecycle
demonstration. It never connects to Railway or production data. The optional Vite
loopback dev origin is trusted only by the synthetic fixture helper; deployed
CSRF settings are unchanged. Final counts and any remaining limitations accompany
the release review, not the historical screen evidence.


Final local results are recorded in [verification JSON](functional-milestone-1-verification.json),
including a digest of changed source/test paths for this uncommitted release.
The first image-browser attempt had45 passes and two initial connection failures;
a bounded readiness setup was added so external Docker tests wait for the exact
liveness contract before navigating. No retries were enabled to hide failures.


Final validation:497 backend tests and393/393 mapped READY cases,13 demo tests,
13/13 assertion mutation kills with clean baselines/restorations,47 browser tests
against the synthetic server, and47 against the locally built disposable Docker
image. TypeScript/Vite, formatting, system/migration checks, schema fail-on-warn,
source explorer checks and file-size/diff reviews passed. Configured Python
statement/branch coverage is94% rounded; JavaScript source coverage is not measured.
The image build used an external temporary Dockerfile solely to mount this cloud
runtime's trusted CA during npm/pip installation. The canonical Railway Dockerfile
and dependency pins are unchanged. Hosted CI and public Railway browser QA are
not claimed. The task-owned QA container was removed after verification.


Release review added an explicit legacy-CSRF POST regression for self-review and
repeated/reversed decisions: no event or audit field changes. The11 service
transaction tests pass; the full audit now has497 passing tests and393/393 mapped
cases. The47 browser tests passed once per target (94 successful executions),
not47 combined. A fresh built-image health request without cookies/authorization
returned HTTP200 and the exact public JSON contract. Both QA containers were
removed. No commit was created, no files staged and no branch pushed; approval
to publish is pending.


The user subsequently approved publishing this tested milestone to the disposable
demo on26October2026. The no-commit/no-push statements above describe the release
review snapshot. Publishing triggers the existing branch-following Railway
workflow; terminal deployment status must be verified separately from local tests.
