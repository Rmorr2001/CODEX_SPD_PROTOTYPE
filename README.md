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

Each business domain has a singular `test/` folder for its test entry point,
regression specification, and future executable tests. Start with
[the six-domain testing map](docs/testing/README.md).

Wave 1 inventories current behavior and designs source-cited test pseudocode.
These documents do not implement coverage or approve unresolved business rules.
Wave 2 implements reviewed cases with shared isolated settings and fixtures.
Existing domain `tests.py` placeholders remain unchanged during design.
