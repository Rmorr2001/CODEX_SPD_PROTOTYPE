# CODEX-SPD-PROTOTYPE development guidance

Applies throughout the `CODEX-SPD-PROTOTYPE` checkout. Follow more specific instructions
within a directory when present. Keep work focused on the requested change.

## Current repository

- Active cloud checkout: `/workspace/CODEX-SPD-PROTOTYPE`. The GitHub remote is
  still `Rmorr2001/SPDWEBAPP_ENV` until its rename is completed; use the actual
  remote for source links. See the root README for pending remote names.

- This demo branch imports `smk37git/SPDWEBAPP_ENV` main commit `004a433`;
  it contains the full Sigma Phi Delta Mizzou application, not the older scaffold.
- `SPDWEBAPP/manage.py` is the management entry point. Preserve its existing
  instruction not to modify it.
- `SPDWEBAPP/SPDWEBAPP_CORE/` contains framework settings, root URLs, ASGI/WSGI.
- Existing domains: `HOME`, `AUTHENTICATE`, `PARLEYPRO`, `PHILANTHROPY`,
  `NEWMEMBER`, and `MISC`. Preserve existing routes and naming in relevant work.
- `SPDWEBAPP/static/` contains shared site styles/images. Each domain owns its
  templates, models, views, migrations, and currently scaffold-only tests.
- [`railway_demo`](SPDWEBAPP/railway_demo/README.md) owns separate demo settings,
  persona entry, fictional seeding, and meaningful demo tests. The root README
  links to its authoritative setup/deployment instructions.
- `SPDWEBAPP/secret_config.py` is our inline-commented runtime config code,
  containing no literal credentials. Demo settings explicitly load this file.
- `requirements.txt` pins original dependencies including Django 6.1.1;
  `requirements-demo.txt` adds Gunicorn/WhiteNoise. Docker and railway.json
  define the disposable interactive demo deployment.
- [`tools/file_tree/`](tools/file_tree/README.md) generates the source explorer
  during each Docker build; generated HTML is not committed.
- Demo SQLite/media live separately in `/tmp`; never import private member data.
  No lint, formatter, type checker, or CI is configured.

This section is the current architecture map. Update it as the application grows
and link each domain README here (or link a single root architecture document
once one exists). The conventions below describe future development; they do
not imply these folders or capabilities already exist.

## Code quality and boundaries

- Use descriptive names, clear Python code, focused responsibilities, and
  Django conventions. Prefer straightforward implementations; add abstractions
  or dependencies only to solve a concrete need.
- Keep business rules out of views, templates, URL configuration, and external
  integration plumbing. Views validate/translate requests and call domain
  operations; domain operations express rules and invariants.
- Validate external inputs, including integration responses. Use Django forms
  and model validation where appropriate; do not assume persistence validates
  every rule automatically. Handle expected failures explicitly.
- Enforce authentication and authorization at request boundaries and enforce
  object/action permissions in domain operations where other callers could
  bypass a view. Test denied access as well as permitted access.
- Use type hints and explicit input/output contracts for public domain APIs
  where supported. Keep Django models, transactions, and migrations idiomatic.
- Remove obsolete code introduced or superseded by the change. Avoid unrelated
  cleanup, speculative layers, and broad restructuring.

## Domains and subdomains (future convention)

- Place business domains in Django apps alongside `SPDWEBAPP_CORE`, under
  `SPDWEBAPP/`. Keep framework settings and application composition in CORE.
- Keep implementation, tests, and documentation with the owning domain.
  Group distinct subdomains beneath it when responsibilities justify it; use
  separate Django apps only when their lifecycle or framework needs warrant it.
- Use descriptive folders/files and clear public interfaces between domains.
  Do not import another domain's internal implementation. Document supported
  entry points and dependencies; expose stable functions/classes as needed.
- Add layers/folders only when useful. Keep shared code to genuinely common
  concerns with explicit ownership; avoid catch-all utilities and oversized
  services. Preserve Django's discovery conventions for models and migrations.

Example only: `orders` and `fulfillment` are hypothetical, not existing domains.

```text
SPDWEBAPP/
├── manage.py                       # existing
├── SPDWEBAPP_CORE/                  # existing composition/configuration
└── orders/                         # hypothetical Django domain app
    ├── README.md
    ├── apps.py
    ├── models.py
    ├── migrations/
    ├── services.py                 # focused domain operations, if needed
    ├── views.py
    ├── urls.py
    ├── tests/
    ├── docs/
    └── fulfillment/                # hypothetical distinct subdomain
        ├── README.md
        ├── services.py
        ├── tests/
        └── docs/                   # only when longer explanations are needed
```

## Size, complexity, and explanations

- Aim for application source files of 250–300 physical lines or fewer; default
  maximum: 400 lines for manually maintained application source, 600 for tests.
  Comments and blank lines count.
- Keep functions focused, generally under 50 lines. Review functions over
  80 lines for decomposition. Split along responsibilities/domain boundaries
  while preserving cohesion, rather than mechanically splitting by line count.
- Exempt generated files/migrations, lockfiles, vendored code, and large data
  fixtures. Document narrow, justified exceptions in the relevant domain README
  or docs, with rationale. Apply limits progressively when relevant work touches
  oversized existing files; avoid unrelated restructuring.
- Add short comments for non-obvious reasoning, rules, invariants, and tradeoffs.
  Use concise docstrings for public interfaces and complex functions, describing
  contracts and relevant failure behavior. Update explanations with code; avoid
  comments that repeat code or boilerplate on every function.

## Domain documentation

- Each meaningful domain and subdomain needs a concise `README.md`: purpose,
  boundaries, important entry points, business rules, dependencies, and testing.
- Identify configuration keys and their purpose without recording secret values.
  Put longer explanations, integration details, and architecture decisions in
  the owning domain's `docs/`. Link subdomain documentation from its parent.
- Update documentation in the same change as behavior/interfaces. Keep one
  authoritative explanation and link to it instead of duplicating it.

## Setup and verification

Run from the repository root, using an isolated Python environment:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-demo.txt
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py check
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
```

- See the demo README for migration, seeding, static collection, and deployment.
  Preserve original non-demo setup instructions separately.
- Run `DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python
  SPDWEBAPP/manage.py makemigrations --check --dry-run` for model migration drift.
- Existing business tests are placeholders. The demo suite exercises original
  pages, roles, CSRF, seed idempotency, and interactive workflows. Add meaningful
  domain-local tests for changed business behavior.
- No lint, formatting, or type-check commands are configured. Do not claim these
  checks ran. If tooling is introduced, record its actual commands here and
  declare its dependencies/configuration in the same change.
- Add meaningful tests for changed behavior, including relevant validation,
  failure, and authorization cases. Use Django's test framework and domain-local
  tests. Target a domain with `manage.py test <app_label>` when one exists.
- Scale checks to the change; run system checks and relevant tests for application
  changes. For documentation-only changes, review accuracy and the diff. Report
  actual commands/results, missing dependencies, and checks that could not run.
- Before completion, review the final diff for correctness, scope, file sizes,
  obsolete code, documentation, and unintended database/generated changes.
- Never put credentials in source, documentation, logs, or test fixtures. Use
  configured secret bindings; do not reveal values while inspecting settings.
