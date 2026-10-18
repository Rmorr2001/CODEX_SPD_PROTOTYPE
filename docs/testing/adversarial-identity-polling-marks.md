# Independent adversarial review: identity, polling and marks

Reviewed `cb69127` on `prototype/railway`, 2026-10-18. This reviewer did not
implement these tests. Scope: AUTHENTICATE, PARLEYPRO and NEWMEMBER only.

## Findings, ranked by migration significance

### 1. P1: profile class persistence can disappear while every identity test passes

`AUTHENTICATE/views.py:159` assigns the submitted `pclass`. The frozen READY
`AUTH-A04-01a` promises persistence of all profile payload fields
(`AUTHENTICATE/test/cases/profile.md:19`), and
`test_profile.py:11–29` explicitly checks them. However, actor A starts in Alpha
(`support.py:83–84`) and every normal profile payload also submits Alpha
(`support.py:16–19`). The pclass equality is therefore insensitive to losing
that write; repeating it over thirteen role variants does not strengthen it.

**Demonstrated:** removing only `brother_profile.pclass = pclass` passed the
entire 76-test AUTHENTICATE suite. Clean baseline and restoration also passed
76/76. A separate synthetic fixture starting in Beta and submitting Alpha
returned `{success:true}` in both versions: clean persisted Alpha, mutant kept
Beta. This is a changed-value fixture omission in an existing READY persistence
contract, not a request to decide new field-validation policy.

**Impact:** a serializer/service migration could silently discard class changes,
affecting profile and class-based consumers despite a green identity suite.
**Minimum change:** initialize A's class to a different valid value for
`AUTH-A04-01a` or submit a different valid class, assert refreshed persistence,
and retain B's unchanged-state assertion. Keep the idempotent case separate.

### 2. P1: the current polling page can reverse Aye and Nay without detection

`PARLEYPRO/views.py:27–32` maps aggregate values into page context. READY
`PP-26a` and `PP-26b` specify the page counts, but their fixtures are both 1/1
(`cases/reads-and-routes.md:18–49`; `test_reads.py:20–49`). Swapping context keys
preserves every asserted value. The asymmetrical 2/1 helper, JSON and closed
history tests use other paths and do not cover this mapping.

**Demonstrated:** replacing page context with `nay_votes=aye_votes` and
`aye_votes=nay_votes` passed all 58 PARLEYPRO tests; baseline and restored were
also 58/58. A fresh fixture with two Ayes and one Nay produced page context
2/1 clean and 1/2 mutated, both HTTP 200. The original source count helper and
JSON endpoint were left intact.

**Impact:** initial page/API adapter data can report the opposite vote majority.
This is within existing current-page preservation scope, independent of blocked
voter-eligibility, no-open-poll or outcome policies.
**Minimum change:** use unequal nonzero counts in `PP-26a`, assert each context
field and its correctly labeled rendered text. Preserve zero/tie cases too.

### 3. P2: personal class-average tests do not distinguish averaging from truncation

`NEWMEMBER/views_functions.py:90–94` divides member totals and rounds to one
decimal. READY `NM-05-01b` uses totals -3/0/0 and expects -1.0
(`cases/read-models.md:29–46`; `test_read_models.py:44–54`). Empty cases also
expect zero. Python equality treats -1 and -1.0 as equal, and none of these
fixtures has a fractional mean.

**Demonstrated:** replacing `round(class_average, 1)` with `int(class_average)`
passed the full 50-test NEWMEMBER suite; baseline and restored were 50/50.
For fresh member totals [1,0], the source reports 0.5 and the mutant reports 0.
The dashboard renders this metric at `templates/newmember_marks_dashboard.html:34`.

**Impact:** a migration using integer arithmetic can silently distort comparative
member metrics. This is a narrow design/input gap around an existing READY
aggregate, not failure to satisfy that design's literal -1.0 example. No named
blocked case reserves ordinary fractional class-average arithmetic.
**Minimum change:** add an unequal-total fixture with a nonintegral mean,
including one that exercises one-decimal rounding (for example 1/3 → 0.3).
Assert the explicit numeric result rather than reproducing the implementation's
aggregate expression in the test.

### 4. P2: progress-member display names are outside the frozen asserted outputs

`NEWMEMBER/views_functions.py:36–40` returns user, full_name, total_marks and
is_negative. READY `NM-05-01a` checks user order, totals and negativity, but
omits full_name (`test_read_models.py:32–42`). READY single-role dashboard tests
also omit these labels (`test_read_models.py:108–130`). Both dashboard templates
consume `member.full_name` (`ACTIVE_newmember_marks_dashboard.html:105` and
`newmember_marks_dashboard.html:146`). No frozen case mentions that output key.

**Demonstrated:** returning only `member.firstName` instead of the full name
passed all 50 NEWMEMBER tests, with clean/restored 50/50. The distinguishing
fixture returned `Tess Able` clean and `Tess` mutated.

**Impact:** a migrated read model can drop member-identifying surnames while
retaining numerically correct rows. This is an inventory/output omission, not
an unimplemented literal assertion or an unresolved visibility policy.
**Minimum change:** assert exact full names in `NM-05-01a` and one permitted
single-role dashboard, using distinct names. Keep cross-member visibility
policy separate.

## Deliberately blocked behavior is not a new suite finding

A fifth surviving mutant assigns `current_poll.created_by = request.user`
immediately before closing. All READY closure fixtures have the closer own the
poll; all 58 tests pass. A separate different-creator fixture shows source
preserving `synthetic-creator` and mutant replacing it with `synthetic-closer`.
However, **PP-16c explicitly blocks cross-creator closure under POL-04**, and
already requires metadata never to be reassigned. This survival demonstrates
that documented boundary, not an additional missing READY test. No creator-only
or chapter-wide permission policy is selected by this review.

The frozen inventory was inspected directly, including owned-domain statuses:

| Domain | READY | NEEDS_FIX | POLICY_BLOCKED | INFRA_BLOCKED |
| --- | ---: | ---: | ---: | ---: |
| AUTHENTICATE | 76 | 3 | 78 | 0 |
| PARLEYPRO | 58 | 5 | 48 | 3 |
| NEWMEMBER | 50 | 14 | 24 | 0 |

Examples deliberately excluded from new findings: AUTH raw-next/referrer
redirects, missing/malformed profile/JSON handling, destructive photo failures,
roster audience and catalog cleanup; PP unauthorized ACTIVE-only close,
nonatomic close/reset, stale close response, multiple-open identity, cross-creator
permissions, browser races; NM direct-helper authorization, malformed inputs,
repeat/self-review, cross-member history/historical export audience, duplicate
export names and formula-like export text. These are represented by the frozen
NEEDS_FIX/policy/infra designs. The global 41/237/6 blockers were not converted
to test credit or relabeled as newly discovered suite failures.

## What is demonstrably protected

These are meaningful regression tests, not empty case mappings. Identity tests
use actual password authentication, credential failures, password replacement,
current/other sessions, unchanged foreign profiles/relations, real synthetic
image storage/deletion, CSRF middleware and granular admin permissions. Polling
covers exact ALL-role admission, forbidden actors, actor-bound creation, forged
vote targets, repeat/change row identity, literal/scoped tallies, closure totals
and reset identity, historical display, JSON types and granular admin gates.
Marks covers signed multi-target creation, board auto-approval, review/edit audit
fields, every persisted mark field through `assert_changes`, retarget failure,
real date filters, foreign-owner exclusion, signed totals, parsed XLSX values and
numeric/string cell types, and authorized/denied admin deletion.

A new ownership control changed `AUTHENTICATE.views.update_majors` to select the
posted `user_id`. All 76 tests executed: exactly one assertion failure, zero
errors. `HttpBoundaryTests.test_own_mutations_ignore_foreign_target_fields`
(operation `update_majors`) rejected the lost own-major update. Baseline and
restored runs passed. This is direct evidence that a representative foreign-target
regression is detected.

A second ownership control changed `reset_photo` similarly. It was rejected by
an assertion that A's photo should be cleared, then the next subtest errored
because B's file had been deleted by the mutant. This is **one assertion failure
plus one cascading FileNotFoundError**, not two assertion kills, a clean mutation
score, or an initial setup failure. Both clean runs passed 76/76. Independent
subtest media setup would make this diagnostic cleaner; the original assertion
still detects the business regression. No source/helper was changed to hide it.

Inspection found no mocked role/ownership/query/aggregate decisions in these
owned tests. Patches are clocks, storage call observation, or NM's explicit
pre-SQL `save` failure. That NM failure verifies a caught pre-write exception;
it does not establish post-write rollback/atomicity. Relevant partial-write
contracts remain blocked. Shared real-ORM factories grant exact roles and
independent staff permissions; direct invalid-choice/Current fixtures are
explicitly marked. Snapshot helpers compare named saved rows/relations rather
than the whole database; the tests supplement them with relevant counts/files.
AUTH's local exclusion helper mutates its snapshot dictionary when allowing
fields, but no demonstrated survivor here depends on that implementation.

## Execution and reproduction

Run from `/workspace/CODEX-SPD-PROTOTYPE`. All seven probes use the specified
interpreter and `SPDWEBAPP_CORE.testing.settings`, fresh Django in-memory SQLite
test databases and existing complete domain suites. Each runs clean baseline,
mutant, then restored, all within its own process. Code-object replacement keeps
real URL wrappers, ORM, templates and the other business functions. No tracked
application, test, settings or harness file is edited. No Git mutation,
credentials, external service, network or deployment was used.

Exact commands executed (one command per line):

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python work/adversarial_identity/probe.py auth_pclass
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python work/adversarial_identity/probe.py pp_page_swapped
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python work/adversarial_identity/probe.py nm_fraction
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python work/adversarial_identity/probe.py nm_display_name
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python work/adversarial_identity/probe.py pp_closer_creator
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python work/adversarial_identity/probe.py auth_foreign_photo
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python work/adversarial_identity/probe.py auth_foreign_majors
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python work/adversarial_identity/demonstrate.py > work/adversarial_identity/demonstration.log 2>&1
```

`probe.py` calls `DiscoverRunner(...).run_tests([DOMAIN + '.test'])` each phase;
these are full domain runs, not selected-method-only mutation results.

| Probe | Baseline | Mutant (full suite) | Restored |
| --- | --- | --- | --- |
| auth_pclass | 76 pass | 76 pass; survives | 76 pass |
| pp_page_swapped | 58 pass | 58 pass; survives | 58 pass |
| nm_fraction | 50 pass | 50 pass; survives | 50 pass |
| nm_display_name | 50 pass | 50 pass; survives | 50 pass |
| pp_closer_creator | 58 pass | 58 pass; documented blocked boundary | 58 pass |
| auth_foreign_photo | 76 pass | 76 run; 1 failure, 1 cascading error | 76 pass |
| auth_foreign_majors | 76 pass | 76 run; 1 assertion failure, 0 errors | 76 pass |

All phases had zero skips. No equivalence claim is inferred from a surviving
mutant: the separate demonstrator asserted the five source/mutant behavioral
differences and passed its one synthetic test. JSON contains exact results,
test IDs, elapsed seconds and log paths; verbose logs record all executed IDs.
Files live only in ignored `work/adversarial_identity/`: `probe.py`,
`demonstrate.py`, `<probe>.json`, `<probe>-{baseline,mutant,restored}.log`,
`demonstration.json` and `demonstration.log`.

For reproduction if ignored artifacts are unavailable, the exact mutations are:

| Module/function | Replace | With |
| --- | --- | --- |
| AUTHENTICATE.views.update_profile | `brother_profile.pclass = pclass` | `pass` |
| PARLEYPRO.views.poll_index context | `'nay_votes': nay_votes, 'aye_votes': aye_votes` | `'nay_votes': aye_votes, 'aye_votes': nay_votes` |
| NEWMEMBER.views_functions.get_personal_stats | `round(class_average, 1)` | `int(class_average)` |
| NEWMEMBER.views_functions.calculate_member_marks | `f"{member.firstName} {member.lastName}"` | `member.firstName` |
| PARLEYPRO.pp_functions.handling_end_vote_request | `current_poll.save()` | insert `current_poll.created_by = request.user` immediately before save |
| AUTHENTICATE.views.reset_photo | `Brother_Profile.objects.get(user=request.user)` | `Brother_Profile.objects.get(user_id=request.POST.get("user_id", request.user.pk))` |
| AUTHENTICATE.views.update_majors | `Brother_Profile.objects.get(user=request.user)` | `Brother_Profile.objects.get(user_id=data.get("user_id", request.user.pk))` |

Implementation method: unwrap the target with `inspect.unwrap`, obtain its source,
apply exactly one replacement, parse its AST and clear only the function's
`decorator_list`; compile using the original function's globals, then temporarily
replace the original unwrapped function's `__code__`. Run the complete domain
suite and restore that code object in `finally`; rerun the suite. Preserve existing
URL-bound decorators. These seven are different from the original six probes in
`tools/testing/probe_regressions.py`.

## Inspected breadth and limits

Read root AGENTS.md; a filename search found no scoped AGENTS.md. Read the shared
testing README, wave-2 goals/results and fixture contract; inspected frozen
inventory statuses and all owned READY IDs. Read all executable test methods and
local helpers: AUTH 76 methods in nine `test_*.py` files plus support/role_urls;
PP 58 in six files plus support; NM 50 in six files plus support. Read the shared
factories, helpers, state and base classes to assess fixture/assertion assumptions.
Coordinator owns independent audit/harness review; this review does not claim to
revalidate the combined 393 mapping audit.

Fully inspected current handwritten owned-domain backend sources: views, models,
admin, URL modules; AUTH forms/utils/clean_majors command; PP forms, pp_functions
and pp_decorators; NM views_functions and its template filter. Also read actual
demo entry view and boundary middleware used by identity tests. Traced identity
creation/profile/major/photo/password updates, photo/profile/user deletion;
poll creation/vote updates/closure/read totals; mark creation/review/edit,
admin deletion, history aggregates and XLSX serialization. Default framework
admin internals and migrations were not independently audited.

Specifications were sampled against fully read tests, rather than claiming a
line-by-line audit of all 359 owned designs. Fully read the findings' profile,
closure, polling reads/routes, marks read-model/history-filter designs and sampled
session/HTTP/admin/request/edit/export/helper boundaries and the operation/role
inventories. Checked READY vs blocked status for each proposed finding. Templates
were sampled at consumed field/form/label locations; no browser/JavaScript or
Vite/React behavior was executed. The full-domain baselines were rerun independently;
the historical combined coverage percentage was not used as adequacy proof.

Standalone composition is a practical limit: `testing/settings.py:52` sets
`LOGIN_URL='/auth/login/'`, matching `railway_demo/settings.py:32`; original
`SPDWEBAPP_CORE/settings.py:70` spells `/auth/login` without the final slash.
Anonymous tests checking `reverse('login')` therefore establish the standalone/demo
transport, not exact original non-demo redirect spelling. The AUTH specification
already records this source difference. No runtime settings/secrets were imported;
this is a composition qualification, not a newly demonstrated authorization defect.

## Verdict

**Adequate with gaps for the scoped, policy-cleared preservation baseline.** The
184 owned tests provide substantial state, permission and output evidence; the
four narrow survivors warrant small fixture/output improvements before relying
on green tests to approve these migrated paths. They do not justify discarding
the suite or demand exhaustive mutation testing. The suite alone is not an
approval gate for the entire Django REST/Vite React migration: documented blocked
security/integrity/policy behavior, PostgreSQL races, real runtime composition and
frontend behavior remain separate work. No implementation fixes were made.

## Preserved review artifacts

The coordinator preserved portable copies of the probe scripts and a JSON result
snapshot. See [repeatable commands](../../tools/testing/adversarial/README.md)
and [the integrated review](adversarial-review.md). Commands above record the
actual scratch paths used by this reviewer; raw logs remain ignored.
