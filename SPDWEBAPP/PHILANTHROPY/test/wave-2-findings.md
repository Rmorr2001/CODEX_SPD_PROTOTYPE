# Wave 2 implementation findings

Frozen implementation inventory: `4b103f6`, branch `prototype/railway`,
repository `Rmorr2001/CODEX_SPD_PROTOTYPE`. Original source inspection baseline
is `7e25ac2`; documentation refinement baseline is `c8bbc4e`.

## Results and mapping

All **66 frozen READY cases** have named discoverable implementations and a
nonempty fully qualified unittest mapping in [case-map.json](case-map.json).
The 41 POLICY_BLOCKED and 11 NEEDS_FIX designs remain in the case documents;
no non-READY case is mapped, skipped or counted as passing implementation.

| Actual check | Result |
| --- | --- |
| Explicit `PHILANTHROPY.test` execution after transaction-boundary correction | 66 tests, 8.953s, OK |
| App-wide `PHILANTHROPY` execution | 66 tests, 5.162s, OK |
| Request module after adding explicit no-persistent-file error assertions | 11 tests, 0.669s, OK |
| Runtime DiscoverRunner package/app-wide ID comparison | Identical 66 IDs |
| Frozen READY IDs versus mapping keys versus discovered unittest IDs | 66/66 exact match; all lists nonempty |
| Skips, expected failures and failed mapped tests in final runs | 0 |
| Django system checks during both final runs | No issues |
| Python file size review | Every domain test/helper file below 600 lines |
| Domain diff whitespace review | Clean |

The successful executions used:

```text
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings
/workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY.test --noinput
/workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY --noinput
/workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY.test.test_requests --noinput
```

The mapping audit initialized only those standalone settings, built each domain
suite with DiscoverRunner, recursively extracted unittest IDs, compared both
66-ID sets, then compared them with every mapping value and frozen READY key.
Static review checked unique method names and file sizes. The coordinator owns
the combined suite, nine original demo tests, coverage audit and mutation probes.
This domain agent did not run or claim those integration checks.

## C06b/C07a transaction boundary observation

The initial implementation used RegressionTestCase for every request case.
Its first package run discovered 66 methods: 64 methods passed, and C06b/C07a
produced eight subtest errors. No case was silently dropped or weakened.

- `PHILANTHROPY/views.py:64–79` converts hours to float, calls save and catches
  exceptions before rendering the request template at line81.
- `PHILANTHROPY/models.py:21–22` stores IntegerField hours and DateField dates.
  Inputs such as `NaN` and an empty date fail during save preparation.
- In the installed Django runtime, `django/db/models/base.py:987` uses
  `transaction.mark_for_rollback_on_error`; `django/db/transaction.py:112–136`
  marks the connection for rollback when an outer atomic block already exists.
- TestCase supplies that outer block. Even though the view catches the
  conversion/validation error, the later real navbar/profile query raises
  TransactionManagementError before the response can complete. This is the
  initial failure observation, not a preserved HTTP500 contract.

The coordinator explicitly approved TransactionTestCase for these caught
persistence-error paths to model normal request autocommit. Only C06b/C07a moved
into `test_requests.AutocommitRequestTests`; shared temporary_media is entered
manually. Their original assertions remain intact: controlled error form,
no success, no inserted event, unchanged unrelated row/profile/role data and
preserved session identity. All concrete non-finite and malformed-date variants
are still exercised with the real ORM, middleware and templates.

Both cases then passed without application changes. This correction does not
assert safety under an enclosing request transaction or establish rollback for
write-then-raise paths. Those Q8 designs remain non-READY. The frozen inventory
classification and 66-case target were not changed.

## Boundaries and remaining blockers

There are **no unresolved source-backed exceptions to the 66 READY mappings**
under the approved settings and transaction boundaries. Tests assert exact
server-selected owner/status/submission/decision fields, metadata preservation,
real CSRF denials and successful token submissions/decisions, real approved
aggregates, year boundaries, XLSX values/types/totals and Django admin permissions.
Named users/profiles/role and permission relations plus unrelated event rows are
captured with the common state helper and checked from fresh database state.

Application behavior, database schema and deployment remain unchanged. Tests
never implement or choose fractional-hour precision, approval repeat/reversal/
self-review rules, export scope/access policy, formula fixes, concurrent update
semantics or admin retention policy. Their original case documents retain the
52 non-READY designs and decisions Q1–Q12. SQLite passing results are not proof
of PostgreSQL concurrency or post-write atomicity.

Only files under the domain's singular test/ package and removal of its empty
placeholder tests.py were changed. No dependencies were installed, no secrets or
real records were inspected, and no network, deployment or Git mutation ran.
