# React screen delivery log

Historical nine-screen release evidence. For subsequent transaction work, see
[functional milestone 1](../migration/functional-milestone-1.md).

Scope: [screen plan](screen-plan.md), generated concepts and actual domain rules.
All acceptance evidence below is local synthetic Django/demo data unless a row
explicitly says otherwise. This work does not deploy a new Railway release.

| Screen | Correctness review | Visual comparison | Delivery status |
| --- | --- | --- | --- |
| S01 Home | [PASS](reviews/S01-code.md) | [PASS](reviews/S01-visual.md) | Accepted: React public home + real read API |
| S02 About & Brotherhood | [PASS](reviews/S02-code.md) | [PASS](reviews/S02-visual.md) | Accepted: real public leadership and history |
| S03 Recruitment | [PASS](reviews/S03-code.md) | [PASS](reviews/S03-visual.md) | Accepted: real recruitment slides and safe links |
| S04 Dashboard + session boundary | [PASS](reviews/S04-code.md) | [PASS](reviews/S04-visual.md) | Accepted: real session, CSRF demo entry, dashboard |
| S05 Member directory | [PASS](reviews/S05-code.md) | [PASS](reviews/S05-visual.md) | Accepted: private directory, search, mobile detail selection |
| S06 My profile | [PASS](reviews/S06-code.md) | [PASS](reviews/S06-visual.md) | Accepted: caller-only profile + functioning legacy edit link |
| S07 Chapter decisions | [PASS](reviews/S07-code.md) | [PASS](reviews/S07-visual.md) | Accepted: authorized Aye/Nay snapshot and stored results |
| S08 Service hours | [PASS](reviews/S08-code.md) | [PASS](reviews/S08-visual.md) | Accepted: own academic-year hours and discoverable mobile table |
| S09 New-member marks | [PASS](reviews/S09-code.md) | [PASS](reviews/S09-visual.md) | Accepted: scoped personal/active/board-only marks |

Review reports live in [reviews/](reviews/); concept boards in
[references/](references/); rendered screenshots in `evidence/`.
Acceptance means a real React read experience plus explicitly labeled links to
existing Django write workflows. It does not mean those transactions have been
rewritten as React forms or that generated sample policies were adopted.

## Final verification

All nine screen gates passed, including the login/access states. The
[machine-readable evidence](verification.json) identifies the verified source
commit and counts. Twenty-four screenshots cover desktop/mobile, login, selected
member details, table scrolling and personal/active marks variants.

| Check | Actual result |
| --- | --- |
| Audited backend suite | 472 passed; 393/393 frozen READY IDs verified; no failures/errors/skips |
| Demo suite | 13 passed |
| Full built-app Playwright suite | 44 passed without retries, 2.2 minutes |
| Required mutation checks | 13/13 caught by assertions; clean/restored passes; no mutant errors |
| TypeScript, Vite production build, Prettier | Passed |
| Django checks / migration drift | Passed / no changes detected |
| OpenAPI validation with fail-on-warn | Passed without warnings |
| Source explorer | 5 passed |
| Configured Python statement/branch coverage | 94% rounded; no JavaScript source-coverage measurement |
| Modified application/test file limits | No violations of 400/600 physical-line limits |

Commands run from repository root with the existing isolated Python environment:

```sh
npm run format:check --prefix frontend
npm run build --prefix frontend
python -m coverage run tools/testing/run_regressions.py --report work/screen-regressions.json
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.demo_settings python -m coverage run --append SPDWEBAPP/manage.py test railway_demo --noinput
python -m coverage report
python tools/testing/probe_regressions.py
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings python SPDWEBAPP/manage.py check
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings python SPDWEBAPP/manage.py makemigrations --check --dry-run
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings python SPDWEBAPP/manage.py spectacular --file work/screens-openapi.yaml --validate --fail-on-warn
python -m unittest discover -s tools/file_tree -p 'test_*.py'
PYTHON_EXECUTABLE=/path/to/venv/bin/python PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium npm run test:e2e --prefix frontend
```

`python` above represents the selected virtual-environment interpreter. The full
browser run started its own synthetic Django fixture and consumed the real Vite
bundle. Review screenshots came from a separately seeded local fixture; both
were stopped afterward. No private database or runtime credentials were used.

## Corrections and limits

Review loops fixed non-scrolling section navigation, malformed configured URLs,
missing arrow glyphs, hero-label contrast, misleading demo guidance, mobile
directory detail discovery and mobile table-scroll discovery. Reports retain the
initial findings and correction evidence.

Integration initially found two stale test expectations: a schema limited to the
foundation status endpoint and the old demo announcement text. Their exact
assertions were updated for the intentional delivered contracts; the schema test
also verifies all eleven GET-only paths and authentication requirements. Explicit
enum names fixed a schema warning without changing stored status values. The
[independent integration review](reviews/integration-code.md) passed before the
clean full audit and mutation rerun were accepted.

One independent S09 browser login wait timed out, then passed in isolation; its
cause is not established. The full 44-test browser suite subsequently passed
without retries. See [S09 correctness evidence](reviews/S09-code.md).

All 284 previously blocked business designs remain blocked. Passing UI/read tests
does not settle those policies or port the legacy transactions. Existing integer
service-hour storage, disposable demo data and legacy write limitations remain
documented in their owning domains. No Railway redeployment or hosted CI result
is claimed by these local checks.


## Marks functional migration

The original S09 acceptance above covers the historical scoped read screen.
The [current behavior/acceptance contract](../../SPDWEBAPP/NEWMEMBER/docs/react-behavior.md)
now maps batch submission, review, edit/retarget, educator denial, history, exports,
role boundaries and the new shared operation receipt migration. Current React
workflows have contextual legacy comparison links rather than legacy-only forms.
Local browser and built-image evidence is recorded with that domain contract;
live deployment acceptance is verified separately by the coordinator.
