# MISC regression tests

Wave 2 implements all **80 frozen READY cases as 80 named Django tests**.
The remaining 23 designs stay blocked: 20 POLICY_BLOCKED, 2 NEEDS_FIX and
1 INFRA_BLOCKED. There are no skips, expected failures or READY exceptions.
Source baseline: `7e25ac2`; refinement: `c8bbc4e`; frozen implementation inventory:
`4b103f6`. See [execution findings](wave-2-findings.md),
[case-to-unittest mapping](case-map.json), [design index](case-index.md) and
[source inventory/decisions](regression-spec.md).

MISC owns announcement fields/filtering/rendering, Chicago calendar calculations,
alert settings/tags and the two models' admin behavior. Real HOME/AUTHENTICATE
routes provide integration coverage. There is no mounted MISC endpoint.
Stored executable override HTML, physical fall-transition timing, unresolved
policies and browser interaction remain outside passing contractual coverage.

Run from repository root with the shared standalone business settings:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test MISC.test --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test MISC --noinput
```

Both commands discover and pass 80 tests. The interpreter shown is the available
coordinator environment; another checkout can use its prepared `.venv/bin/python`.
No runtime settings/secret_config, member DB, demo seed, credentials, external
network or dependency installation is required. Tests use synthetic shared
factories, temporary media and isolated database from
[the shared fixture contract](../../../docs/testing/fixture-contract.md).
The old empty `MISC/tests.py` was removed after package discovery was established.

| File | Contract |
| --- | --- |
| `test_records.py` | Defaults, validation, timestamps, string helpers and escaped fragments |
| `test_alerts.py` | Real tag defaults/overrides/visibility, local controls and injected fallback seams |
| `test_calendar.py` | Aware Chicago calendar dates, spring boundary and rollover |
| `test_integration.py` | Mounted filtering/role/redirect/home boundaries; direct unused callable context |
| `test_admin_permissions.py` | Narrow Django permission sets and denied crafted requests |
| `test_admin_writes.py` | Editable/excluded fields, validation, save flags and authorized cloning |
| `test_admin_actions.py` | Enforcing CSRF, detail/bulk deletion, demo block and audit history |
| `test_transactions.py` | Real-write rollback after deliberate stock admin hook failures |
| `support.py` | Thin MISC constructors, admin assertions and actual consumed clock seams |

Business settings expose real admin; one explicit override tests the actual demo
boundary middleware with HTTPS. `misc_time` preserves datetime construction while
freezing `MISC.utils.datetime.now(tz)`; `audit_time` also freezes LogEntry's captured
field-default callable. No role, filtering, permission, template or model write
is mocked. Only deliberate failure seams and the unmounted view's render-argument
capture use mocks.

Historical design commands using `railway_demo.settings` are superseded for this
isolated regression suite; they are not needed here. Combined six-domain runs,
existing nine demo tests, mapping audit and mutation-effectiveness probes belong
to the coordinator. This domain reports only its own scoped results.
