# CODEX-SPD-PROTOTYPE

Our editable Sigma Phi Delta prototype. The active cloud checkout is
`/workspace/CODEX-SPD-PROTOTYPE`.

The GitHub repository is
[`Rmorr2001/CODEX_SPD_PROTOTYPE`](https://github.com/Rmorr2001/CODEX_SPD_PROTOTYPE)
(underscores in the GitHub name). The local `origin` remote points here. Our
working branch is `prototype/railway`; local `main` still represents the
original imported upstream revision, not the prototype branch.

`upstream` points to `smk37git/SPDWEBAPP_ENV` for deliberate source comparisons;
local pushes to upstream are disabled. There is no automatic synchronization.
Railway's project and service display names remain `Codex App` and
`spdwebapp-demo`; the configured project token does not authorize renaming them.

The original upstream is `smk37git/SPDWEBAPP_ENV`. Internal Django paths such as
`SPDWEBAPP/` and `SPDWEBAPP_CORE/` are implementation identifiers, retained to
preserve imports, migrations, and deployment entry points.

## Original application setup

## Setup Instructions
For security purposes, the website stores the database, secret key, development environment, and the path to the admin panel in a seperate file that is *two directories above the website files*, aka, *the same directory that the git repo is stored in*.

In that folder, you need two things:

1. The `db.sqlite3` file (which will be automatically generated unless you have a previous database you want to use)
2. A file called `secret_config.py`

Create the secret_config.py file to match this template
```python
SECRET_KEY = 'paste here'
ADMIN_URL = 'admin'
ENVIRONMENT = 'local'
```
Then paste the output of this command into the file
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
You may change the admin path to whatever you wish. The environment should be set to either 'local' or 'development'


## Isolated Railway demo

See [railway_demo/README.md](SPDWEBAPP/railway_demo/README.md) for the separate
seeded interactive deployment. The demo uses our own inline-commented
`SPDWEBAPP/secret_config.py`; the original manual setup above describes non-demo use.

## Backend regression work

Each business domain has a singular `test/` folder containing executable tests,
case mappings, specifications and testing documentation. Start with
[the six-domain testing map](docs/testing/README.md) for setup and commands.

Wave 2 verifies all 393 READY case designs: 405 combined tests including the
shared harness, plus the nine existing demo tests. The 284 remaining designs
retain explicit defect, policy or infrastructure blockers. An executable mapping
audit prevents missing or skipped tests from being counted as verified cases.
See [Wave 2 results](docs/testing/wave-2-results.md) for evidence and limitations.

[Part 1 hardening](docs/testing/part-1-hardening.md) strengthens the seven
demonstrated review gaps and requires 13 assertion-effectiveness probes in CI.

## React and API foundation

[Part 2 delivery](docs/migration/part-2-foundation.md) adds a bundled React workspace
at `/app/`, JSON contracts under `/api/v1/` and OpenAPI schema. Existing Django
pages remain at their original URLs. See [frontend setup](frontend/README.md)
for local preview and checks. The Dockerfile builds React and runs only Python
in production; this repository change does not itself verify a Railway release.

## React screen redesign

The [screen plan](docs/design/screen-plan.md) maps all nine public/member concepts
to routes, reference images and executable specifications. The
[delivery log](docs/design/delivery-log.md) records each builder/reviewer/visual
comparison loop, actual screenshots and checks. Existing Django transaction
forms remain available through clearly labeled links as read screens migrate.
