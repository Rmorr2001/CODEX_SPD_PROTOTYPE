# Wave 2 results

Completed 2026-10-18 on `prototype/railway`. Design baseline: `4b103f6`;
application source baseline: `7e25ac2`. Six domain agents implemented tests after
[verifiable goals](wave-2-goals.md) and the [677-case inventory](wave-2-inventory.json)
were frozen. The coordinator integrated the harness, audit, mutation probes and CI.

## Acceptance evidence

| Check | Actual result |
| --- | --- |
| Frozen READY mappings | 393/393, each maps to one distinct executable method |
| Explicit-package and app-label runs | All six domains passed independently |
| Initial combined audit | 404 tests passed in 50.215 seconds |
| Final combined audit after mutation restoration | 404 tests passed in 73.786 seconds |
| Original demo suite, isolated demo settings | 9 tests passed in 1.145 seconds |
| Source-explorer stdlib suite | 5 tests passed |
| Django system check | No issues |
| Migration drift | No changes detected |
| Assertion-effectiveness probes | Six of six mutants failed by assertion; all baselines/restorations passed |
| Audit negative probes | Missing, empty, blocked and wrong-domain mappings rejected |
| Skips / expected failures / unexpected successes | Zero |

The combined total is 393 domain methods plus 11 shared-harness tests. It does
not include the nine demo methods or five source-explorer methods. Case mapping
counts come from actual discovery and successful execution, not static method
names alone. `work/test-results.json` records individual IDs and all blockers.
Each domain README records its independent package/app results.

Commands are in the [testing map](README.md). Local verification used
`/workspace/work/spd-mizzou-venv/bin/python` in place of its portable `.venv`
path. Coverage 7.11.0 was installed from `requirements-test.txt` into that isolated
environment. No lint, formatting or type-check tooling is configured.

## Assertions demonstrably reject changed behavior

The probe tool changes a function's code object only within its own process;
it never edits application source or deployment. Each selected test first
passed cleanly, failed with the mutation, then passed after restoration. The
full combined suite subsequently passed again. Subtests can produce multiple
assertion failures from one method; these are not additional covered cases.

| Domain / case | Deliberate defect | Mutant outcome |
| --- | --- | --- |
| AUTHENTICATE / `AUTH-A04-01a` | Corrupt the saved own-profile first name | 13 assertion failure(s), zero errors |
| PARLEYPRO / `PP-15b` | Inflate the Aye tally by one | 1 assertion failure(s), zero errors |
| PHILANTHROPY / `PH-C17a` | Move academic-year start from July to August | 1 assertion failure(s), zero errors |
| NEWMEMBER / `NM-05-01b` | Include requested marks instead of approved personal marks | 1 assertion failure(s), zero errors |
| HOME / `HOME-T02a` | Count alumni instead of active profiles | 1 assertion failure(s), zero errors |
| MISC / `MISC-T15b` | Select the first March Sunday instead of the second | 2 assertion failure(s), zero errors |

Exact targeted methods:

- `AUTH-A04-01a`: `AUTHENTICATE.test.test_profile.ProfileTests.test_edit_own_profile`
- `PP-15b`: `PARLEYPRO.test.test_votes.VoteTests.test_count_helper_respects_supplied_queryset`
- `PH-C17a`: `PHILANTHROPY.test.test_statistics.AcademicYearTests.test_academic_year_dates_are_july_through_june`
- `NM-05-01b`: `NEWMEMBER.test.test_read_models.ReadModelTests.test_personal_stats_use_approved_signed_totals`
- `HOME-T02a`: `HOME.test.test_public_pages.PublicPageTests.test_active_count_uses_distinct_role_membership`
- `MISC-T15b`: `MISC.test.test_calendar.CalendarTests.test_second_and_first_sunday_dates_across_years`

The repeatable tool is `tools/testing/probe_regressions.py`; JSON evidence is
written to `work/mutation-results.json`. These six probes establish selected
assertion effectiveness, not an exhaustive mutation score.

## Coverage and boundaries

The final clean combined run plus the existing demo run measured **91.63% combined
statement/branch coverage** over the six domains and `railway_demo`: 1,284/1,391
statements and 227/258 branch destinations. Migrations and test code are excluded.
The shared harness and tools are outside that application-source coverage scope.
There is no arbitrary coverage floor. A covered line does not establish that all
security, concurrency, failure or business-policy cases are resolved.

All **284 non-READY designs remain blocked**, without skips, expected failures
or passing-test credit: 41 NEEDS_FIX, 237 POLICY_BLOCKED, 6 INFRA_BLOCKED. Their
primary status, additional blockers, source and domain remain in the frozen
inventory and audit report. PostgreSQL concurrency, browser behavior, live Railway
integration and unresolved policy are not verified by this SQLite backend suite.
No application behavior, schema, runtime settings or deployment changed. Only
obsolete empty app-root `tests.py` placeholders were removed after discovery passed.

## Visible specification clarifications

No READY case was dropped or reclassified. Coordinator-approved corrections
preserve each case's substantive assertions:

- AUTH: assert Django's real `last_login` update; exercise adminsortable's actual
  reorder endpoint; replace the success fixture hometown rejected by the existing
  substring filter. See [AUTH findings](../../SPDWEBAPP/AUTHENTICATE/test/wave-2-findings.md).
- PARLEYPRO: use the view-only admin's actual Result column index and the template's
  zero-padded date. See [polling findings](../../SPDWEBAPP/PARLEYPRO/test/implementation-findings.md).
- NEWMEMBER: assert Django's admin-index redirect for a delete-only/view actor,
  retaining minimal permissions. See [mark findings](../../SPDWEBAPP/NEWMEMBER/test/wave-2-findings.md).
- HOME: assert seed password markers remain unusable rather than byte-identical;
  Django randomizes those markers. See [HOME findings](../../SPDWEBAPP/HOME/test/wave-2-findings.md).
- PHILANTHROPY: two caught-validation/database error paths use `TransactionTestCase`
  to reflect ordinary request autocommit rather than TestCase's outer transaction.
  See [service-hour findings](../../SPDWEBAPP/PHILANTHROPY/test/wave-2-findings.md).

The common harness also keeps the unconditional demo context processor out of
business settings and deep-copies template configuration in demo settings. This
fixes test composition without changing runtime rendering or routes. Domain
findings record test-development failures and their final clean results.

## Review and automation

New Python files are at most 329 physical lines; no function exceeds 80 lines.
No skip/expected-failure markers were introduced. Source-scope inspection verified
that application behavior, migrations, management entry points and runtime secret
configuration were untouched. Documentation links and staged whitespace were
reviewed. The GitHub Actions workflow repeats the audit, probes, original demo,
Django/drift checks and source-explorer tests, uploading JSON and coverage evidence.
Local results above do not claim a hosted GitHub Actions run has passed.
