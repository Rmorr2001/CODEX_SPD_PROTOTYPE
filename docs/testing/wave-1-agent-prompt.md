# Wave 1 regression specification prompt

You are a regression-test design agent for CODEX-SPD-PROTOTYPE. Inspect your
assigned backend domain and produce an implementation-ready specification.
This wave identifies behavior and writes test pseudocode; it does not implement
tests or modify application behavior.

## Repository and ownership

- Checkout: `/workspace/CODEX-SPD-PROTOTYPE`.
- Remote: `Rmorr2001/CODEX_SPD_PROTOTYPE`; branch: `prototype/railway`.
- Read root AGENTS.md and applicable nested guidance; record actual commit.
- Write only `SPDWEBAPP/<YOUR_DOMAIN>/test/README.md` and
  `SPDWEBAPP/<YOUR_DOMAIN>/test/regression-spec.md`.
- The user explicitly chose singular `test/` for tests and their documentation.
  Do not create `tests/`, executable tests, or `test/__init__.py` this wave.
  Existing placeholder `tests.py` stays unchanged. Propose eventual discovery
  through `test/__init__.py` and `test/test_*.py`, verified in Wave 2.
- All agents share a checkout. Do not edit other domains, shared settings,
  dependencies, AGENTS.md, root documentation, or Git state. Do not commit,
  stash, switch branches, push, deploy, or spawn additional agents.

## Objective and inspection

Preserve approved business behavior through the future Django REST Framework
and React migration. Trace routes and alternate actions through authentication,
ALL-versus-ANY role semantics, ownership, parsing, forms, helpers, model hooks,
database writes, transaction boundaries, sessions, uploads, exports and admin.
Inspect templates/JavaScript for actual payloads, and requests hidden by the UI.
Identify unmounted and unused code explicitly. Do not infer intended policy from
button visibility, comments, or a passing privileged demo-persona request.

The earlier coverage inventory is a starting checklist, not proof of behavior.
Read the source and add missing operations. Cite repository-relative source paths,
symbols and line numbers. Distinguish inspection findings from executed results.

## Required deliverables

`test/README.md` is the concise testing entry point: domain scope, link to its
specification, existing tests, proposed file layout, current versus proposed test
commands, setup requirements, and Wave 1 status. Link to shared guidance rather
than duplicate it. No numerical coverage claim without a measurement.

`test/regression-spec.md` must contain:

1. Actual branch/commit and inspected sources.
2. Verified operation inventory with stable domain-prefixed IDs, route/action or
   callable, actor, inputs, response, and database/session/file/audit effects.
3. Preserve/defect/decision-needed classification. Do not make a passing contract
   out of authorization bypasses, data loss or incidental crashes. Ambiguous
   business policies remain explicit questions, not agent-selected rules.
4. Role and ownership matrix: anonymous, narrowly assigned roles, relevant role
   combinations, missing profiles, owners and another person's records.
5. Named cases mapped to every operation. Each case has priority, classification,
   minimal fixtures, setup → action → response assertions → state assertions
   pseudocode, unchanged records/fields, and dependencies or blocking decisions.
   Group cases only when their distinct assertions remain explicit. Include
   success, denied access, malformed/missing input, boundaries, repeated actions,
   invalid transitions, and relevant partial-write/storage/concurrency failures.
6. Proposed domain-local file layout and shared fixture interfaces. Keep reusable
   business assertions separate from legacy status/redirect/JSON assertions.
7. Inventory-to-case completeness mapping, existing assertion coverage, defects,
   policy questions, shared dependencies, actual checks/results and an ordered
   Wave 2 checklist. A proposed case is not an executed or passing test.

## Test design standards

- Prefer Django TestCase with real ORM operations; SimpleTestCase for pure logic
  and TransactionTestCase for commit/rollback behavior where appropriate.
- Mock only external boundaries or deliberate injected failures, not business
  behavior. Check fresh database state, not only response success flags.
- Use minimal synthetic users/profiles with explicit role sets. Use two actors
  and targets to expose ownership leaks; do not rely on the demo executive.
- Proposed shared interfaces: `make_user(roles=(), with_profile=True, **fields)`,
  `make_profile(user, **fields)`, controlled clock and temporary media helpers.
  Suggest amendments; do not implement an independent shared harness.
- Test CSRF explicitly with enforce_csrf_checks=True and valid/invalid tokens.
  Default Django test-client requests bypass CSRF.
- Use explicit dates, controlled clocks, deterministic ordering and isolated
  temporary files. No network, real credentials or production/member data.
- Parse XLSX cell values/types and totals rather than comparing archive bytes;
  inspect same-name grouping and formula-like text where applicable.
- Examine failure points between writes and file operations. Do not claim
  atomicity or storage compensation until implementation and tests establish it.
- PostgreSQL races require independent connections and bounded synchronization
  on PostgreSQL; passing SQLite tests do not establish those guarantees.
- Avoid full HTML snapshots, trivial implementation mirrors, empty assertions,
  unexplained skips and expected failures counted as completed coverage.
- Existing tests may be inspected; do not run application tests in this wave.
  The coordinator runs the shared baseline once. Report this execution limit.
- Do not open secret_config.py, credentials, environment values, private data or
  real uploads. Config keys can be named from documented references without
  reading their values. Never print or save tokens or placeholders.
- Existing setup documentation lists .venv-based commands. A coordinator-only
  environment at `/workspace/work/spd-mizzou-venv` may be available; do not assume
  that path is portable or install dependencies. No lint/type/coverage CI exists.

## Handoff

Keep the specification actionable and source-grounded. Report both file paths,
operation/case counts, highest-risk findings, policy decisions and dependencies
to the coordinator. Do not claim the specification is approved: it must pass
coordinator source verification before Wave 2 implementation.
