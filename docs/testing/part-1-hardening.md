# Part 1 regression hardening

This increment addresses the seven demonstrated test gaps from the
[independent review](adversarial-review.md), starting at `be7261f`. It strengthens
preservation tests and their specifications without changing application behavior,
schema, runtime settings, deployment or business policy. User-facing completion
date: 18 October 2026 (America/Chicago).

## Changes and contracts

| Reviewed gap | Current protection | Existing contract |
| --- | --- | --- |
| Profile class saving omitted | Reset A to Beta for each role variant, submit Alpha, refresh and assert exact persistence plus unchanged B | `AUTH-A04-01a` |
| Current-page Aye/Nay swapped | Use two Ayes and one Nay in both open/no-open reads; assert context and labeled HTML where present; snapshot all choice rows | `PP-26a,b` |
| Wrong office holder | Assert every expected office/profile pair, separately from office order; no new ordering between tied holders | `HOME-T02c` |
| Progress sorting removed | Create A before B but give A5/B10/C0 approved hours; assert dashboard B/A/C and helper A/B/C input order | `PH-C18a` |
| Fractional average truncated | Add literal 0.5, 0.3, -0.3 and 0.7 examples; verify each member sees the same class mean and reads preserve state | `NM-05-01b`, extended |
| New-member surname omitted | Assert exact distinct full names in helper output, both permitted single-role contexts and rendered dashboards | `NM-05-01a`, `NM-05-04a`, extended |
| Service-hour member labels blanked | Assert exact owner/full-name/hour triples in helper/dashboard output and literal rendered names | `PH-C18a`, extended |

The fractional-average method is new; other changes strengthen existing methods.
`NEWMEMBER/test/case-map.json` maps `NM-05-01b` to both its original signed-total
method and `test_personal_stats_round_fractional_class_average`. The frozen
677-design inventory is byte-identical: all 393 READY IDs remain required, with
394 mapped domain methods plus 11 harness methods. The 284 blocked designs retain
all statuses and blockers. No permission, visibility, tied-order, fractional-hours
or approval-transition policy is selected here.

The current case documents describe the strengthened fixtures/output extensions.
The original Wave 2 results, adversarial reports and their JSON snapshots retain
their historical counts and observations.

## Required effectiveness checks

`tools/testing/probe_regressions.py` now requires **13** bounded mutation checks:
its original six mapped-case checks, plus the seven reviewed defects against
complete affected-domain suites. The existing GitHub Actions step invokes this
same command and uploads `work/mutation-results.json`.

Each check requires a positive, equal executed-test count in all three phases:
clean suite passes; mutant produces at least one assertion failure and zero
errors; restored suite passes. Skips, expected failures and unexpected successes
invalidate acceptance. JSON includes actual suite labels, mapped method IDs,
failed method/subtest IDs and every phase's outcomes. A missing fragment raises
an error rather than silently accepting an unexercised mutation.

The function code object is changed only inside the diagnostic process and
restored in `finally`; tracked source is never edited. The historical diagnostic
scripts under `tools/testing/adversarial/` remain available, with their original
results distinguished from the required current CI gate.

## Commands

From the repository root, with `requirements-test.txt` installed:

```sh
.venv/bin/python -m coverage run tools/testing/run_regressions.py
.venv/bin/python tools/testing/probe_regressions.py
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE PARLEYPRO PHILANTHROPY NEWMEMBER HOME MISC SPDWEBAPP_CORE.testing --noinput --shuffle=20261018
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.demo_settings .venv/bin/python -m coverage run --append SPDWEBAPP/manage.py test railway_demo --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py check
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py makemigrations --check --dry-run
.venv/bin/python -m unittest discover -s tools/file_tree -p 'test_*.py'
.venv/bin/python -m coverage report
```

Local execution uses `/workspace/work/spd-mizzou-venv/bin/python` in place of the
portable `.venv` path. No lint, formatter or static type checker is configured.
This SQLite backend evidence does not verify browser behavior, PostgreSQL
concurrency, live deployment or unresolved policy. It is a stronger baseline for
the next DRF/React foundation increment.

## Actual acceptance results

| Check | Observed result |
| --- | --- |
| Unchanged starting suite | 404 passed; all seven defects again survived their full domain suites |
| Five affected domains after hardening | 314 passed |
| Final clean combined audit after mutation restoration | 405 passed; 393/393 READY IDs verified; no skips/errors/failures |
| Shuffled combined suite, seed 20261018 | 405 passed |
| Existing demo suite | 9 passed |
| Source explorer | 5 passed |
| Django configuration / migration drift | No issues / no changes detected |
| Required effectiveness probes | 13/13 caught by assertions, with clean/restored passes and zero mutant errors |

The seven formerly surviving defects now produce these complete-domain results:

| Injected defect | Methods executed | Assertion failures | Errors | Clean / restored |
| --- | ---: | ---: | ---: | --- |
| Discard the submitted profile class | 76 | 13 | 0 | Pass / pass |
| Reverse the current-page Aye and Nay counts | 58 | 2 | 0 | Pass / pass |
| Display the president under External Vice President | 63 | 1 | 0 | Pass / pass |
| Remove descending dashboard progress ordering | 66 | 1 | 0 | Pass / pass |
| Truncate the fractional personal class average | 51 | 1 | 0 | Pass / pass |
| Drop the surname from new-member progress | 51 | 2 | 0 | Pass / pass |
| Blank the philanthropy progress member name | 66 | 1 | 0 | Pass / pass |

Failure counts can include subtests; they do not increase the number of mapped
case designs. The original six probes also passed their acceptance checks.
The [JSON evidence](evidence/part-1-hardening.json) records exact phase counts,
failed IDs, scope labels, baseline survivors and the frozen-inventory digest.

The clean combined and demo coverage runs measured 91.63% combined statement/branch
coverage in the existing six-domain/demo scope. The acceptance improvement is the
seven newly demonstrated assertion kills, with no percentage floor introduced.

Final scope review confirmed no application, schema, runtime configuration or
frozen-inventory changes. Modified Python files are at most 274 physical lines;
no function exceeds 80 lines. Documentation links, JSON, Python syntax, discovery
mapping and whitespace were checked. These are local results; the updated hosted
GitHub Actions workflow is not claimed to have completed here.
