# Wave 2 verifiable goals

Declared before the six implementation agents are launched. Baseline:
`4b103f6`, branch `prototype/railway`, `Rmorr2001/CODEX_SPD_PROTOTYPE`.

Implementation completed: see [actual results and limits](wave-2-results.md).

## Acceptance criteria

1. Freeze the 677-design inventory and its 393 READY cases before implementation.
   Account for all cases. Implement each READY contract using named discoverable
   Django tests, with an explicit case-to-test mapping. Parameter sets may share
   a method only when every mapped case's assertions are present.
2. Use standalone test settings and synthetic fixtures: no runtime secret import,
   production/member database, external network or deployed service dependency.
   Provide business/admin and demo modes without weakening actual application
   authorization. Keep real models, ORM, sessions, middleware and templates.
3. Verify explicit domain-package and app-wide discovery. Keep executable tests
   and documentation in singular domain `test/` directories. Remove obsolete
   empty `tests.py` modules when package discovery is established.
4. Require passing domain suites and one combined run, then run the existing nine
   demo tests under isolated demo settings. Publish actual counts/results and
   setup/check commands, not proposed commands labeled as available.
5. Include relevant authorization, ownership, validation, boundary and state
   assertions. Assert changed and unchanged records, parsed XLSX values/types,
   real synthetic media and explicit CSRF cases. No empty tests, generic-success
   assertions, skip/expected-failure credit or mocking business decisions.
6. Audit every mapped test against discovery and execution; missing, skipped or
   failed mappings fail the acceptance audit. A source-confirmed specification
   error must be reported with evidence and coordinator approval as an explicit
   blocker, never silently dropped, softened or reclassified by an agent.
7. Prove selected regression assertions are effective using temporary, bounded
   behavior mutations across all six domains. Record the exact targeted tests
   and their expected failures, restore source, and rerun the clean suite.
8. Leave application behavior, database schema, deployment and business policy
   unchanged. Keep 284 non-READY cases in a blocker registry; do not turn unsafe
   behavior into a passing contractual expectation. Tests/harness/CI/docs are in
   scope; runtime fixes and arbitrary policy choices are not.

## Frozen domain goals

| Domain | READY cases to implement | Non-READY designs retained |
| --- | ---: | ---: |
| AUTHENTICATE | 76 | 81 |
| PARLEYPRO | 58 | 56 |
| PHILANTHROPY | 66 | 52 |
| NEWMEMBER | 50 | 38 |
| HOME | 63 | 34 |
| MISC | 80 | 23 |
| Total | 393 | 284 |

READY is a pre-implementation classification, not proof the source satisfies every
assertion. Demonstrated contradictions remain visible in the final report with
case ID, source location, observed result and required fix/decision. A complete
mapping audit must distinguish implemented cases from those explicit exceptions.

## Shared implementation interface and ownership

The coordinator implements `SPDWEBAPP_CORE/testing/`: `settings`, `demo_settings`,
`factories`, `helpers`, `state`, `base`, and harness tests. Six domain agents own
their own domain `test/` Python files, README and `case-map.json`, plus removal of
their obsolete placeholder `tests.py`. Agents do not edit shared files, Git state,
other domains, application code, dependencies, secrets or deployment settings.

Imports for implementation:

```python
from SPDWEBAPP_CORE.testing.factories import make_user, make_profile, TEST_PASSWORD
from SPDWEBAPP_CORE.testing.helpers import login_actor, csrf_client, temporary_media, at_time
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
```

`RegressionTestCase` supplies isolated temporary media and otherwise uses the real
Django TestCase/client. Use explicit override_settings for a demo-mode class or
run original demo tests separately with `SPDWEBAPP_CORE.testing.demo_settings`.
Fixtures return real ORM objects; app roles never imply staff or other roles.

Each domain writes a JSON object mapping every frozen READY case ID to a nonempty
list of fully qualified unittest IDs. Example:

```json
{"PP-07a": ["PARLEYPRO.test.test_votes.VoteTests.test_cast_aye_creates_own_current_choice"]}
```

The coordinator owns the frozen inventory, blocker registry, executable audit,
combined validation, CI configuration, mutation probes and final integration.
Domain agents run isolated scopes only after the coordinator announces the harness
is available. Shared fixture problems go to the coordinator for one common fix.
