# Independent adversarial regression review

Reviewed `cb69127` on 2026-10-18, before the Django REST/Vite React migration.
Two reviewers independently inspected three domains each; neither implemented
Wave 2. Goals were declared in chat before dispatch: trace real behavior to
assertions, challenge all six domains with new defects, distinguish READY gaps
from documented blockers, and report practical adequacy with reproducible evidence.

**Verdict: adequate with gaps.** The suite provides useful protection for current
policy-cleared behavior. It needs a small set of stronger fixtures/output checks
before green runs can approve the corresponding migrated paths. No evidence
supports discarding the suite, calling it complete behavioral equivalence, or
resolving blocked policy through test assumptions.

## Findings and smallest useful improvements

These are test/design gaps, not defects observed in the unchanged application.
Each deliberately broken variant passed the complete affected domain suite;
a separate distinguishing fixture demonstrated different source/mutant behavior.

| Priority for migration | Domain / contract | Defect that existing tests miss | Minimum useful improvement |
| --- | --- | --- | --- |
| Fix before migrating profile writes | AUTH / `AUTH-A04-01a` | Omit saving `pclass`; initial and submitted classes are both Alpha | Submit a different class, refresh the profile, assert new value and unchanged foreign profile |
| Fix before migrating poll presentation | PARLEYPRO / `PP-26a,b` | Reverse current-page Aye/Nay context values; fixtures are tied 1/1 | Use unequal nonzero counts and check context plus correctly labeled HTML |
| Fix before migrating officer outputs | HOME / `HOME-T02c` | Put the president's profile under External VP; only selected holder pairs are checked | Assert the complete expected office/profile pair set, separately from office order |
| Strengthen dashboard ordering | PHILANTHROPY / `PH-C18a` | Remove descending progress sorting; insertion order already matches totals | Create owners in a different order from their totals and assert ordered owner/total pairs |
| Extend aggregate preservation | NEWMEMBER / `NM-05-01b` | Truncate fractional class means; existing examples are integral | Assert explicit fractional and one-decimal rounding examples |
| Extend read-model preservation | NEWMEMBER / `NM-05-01a` | Drop surnames from progress names; name output is not enumerated | Assert literal full names for distinct members and a permitted dashboard |
| Extend read-model preservation | PHILANTHROPY dashboard | Blank member names; owner IDs/totals still match | Assert literal context and rendered display name |

The first four are READY fixture/assertion omissions. The last three extend
incomplete preservation designs around existing source outputs; they are not
failures of the original designs' literal examples. None requires choosing a
new audience, approval, precision-of-hours or deletion policy. Priority describes
migration work, not a claim of seven high-severity production vulnerabilities.

Detailed source/test/spec locations, observed values and commands:

- [Identity, polling and new-member review](adversarial-identity-polling-marks.md)
- [Service hours, public content and alerts review](adversarial-hours-content-misc.md)
- [Recorded machine-readable evidence](evidence/adversarial-review.json)
- [Repeatable probe commands](../../tools/testing/adversarial/README.md)

## What the challenges demonstrated

Fourteen new bounded probes were run beyond Wave 2's original six:

| Outcome | Probes | Interpretation |
| --- | ---: | --- |
| Meaningful preservation gaps survived full suites | 7 | Findings above; distinguishing fixtures show the changed behavior |
| Survivor already covered by a policy blocker | 1 | Cross-creator poll closure, `PP-16c`; excluded from new READY findings |
| Defects rejected by assertions without errors | 4 | Foreign major target, service-hour owner reassignment, inactive announcement exposure, missing admin change audit |
| Defects rejected with assertions and subsequent file errors | 2 | Foreign photo reset and omitted seed slide; errors are reported separately, not counted as assertion kills |

Every probe had passing clean and restored full-domain runs. A surviving mutant
was never inferred from one selected test passing. Seven findings have separate
non-equivalent distinguishing fixtures: profile class Beta→Alpha, poll counts
2/1, marks totals [1,0], full member names, a different officer profile, and
progress order contrary to creation order. The service-hour name witness also
checks rendered output. No comprehensive mutation percentage is claimed.

The poll-creator mutant was a preliminary candidate mentioned in chat. Inspection
of `PP-16c` established it as an already documented policy boundary, so it is
excluded from the seven findings. This distinction prevents an intentionally
blocked case from being mislabeled as a failed READY implementation.

The controls show substantive assertions beyond HTTP success: preserving record
owners, filtering inactive content, recording actor/object/action audit effects,
and creating real seed media. Reviewed tests also exercise actual ORM writes,
password authentication, CSRF, roles/model permissions, decision audit fields,
XLSX cell values/types, timestamps, file bytes and transaction rollback. Snapshot
helpers compare named rows/relations/files; they do not prove universal absence
of side effects across uncaptured tables.

## Coordinator verification

Independently reran from the repository root, with the existing isolated Python
environment (`/workspace/work/spd-mizzou-venv/bin/python` locally):

```sh
.venv/bin/python tools/testing/run_regressions.py --report work/adversarial-coordinator-baseline.json
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings .venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE PARLEYPRO PHILANTHROPY NEWMEMBER HOME MISC SPDWEBAPP_CORE.testing --noinput --shuffle=20261018
```

- Clean combined audit: 404 tests passed, 393/393 mapped READY methods succeeded,
  zero skips/errors/failures, 56.302 seconds.
- Shuffled combined suite: 404 passed, zero skips/errors/failures, seed 20261018,
  50.859 seconds. This one seed found no order leak; it is not proof of all orders.
- A fresh independent changed-class witness passed clean, failed exactly one
  assertion under omitted persistence, then passed after restoration. Its initial
  synthetic username contained a substring rejected by existing moderation; that
  setup failure was corrected before accepting the witness results.
- Result-accounting challenge used synthetic clean, failed-subtest, skipped-subtest,
  expected-failure and unexpected-success methods. Only the clean method appeared
  in `RecordedResult.successful_ids`; all adverse outcomes would fail acceptance.
- Preserved the review probes under `tools/testing/adversarial/` and reran the
  identity witness, the 76-test major-ownership control, and the 66-test service-hour
  sorting survivor with its distinguishing witness. Their recorded classifications
  held after portable path/import adjustments.
- Reviewed the shared settings/factories/state helpers, audit and CI configuration.
  The mapping audit establishes discovery and successful execution; it cannot
  establish that a fixture or assertion is semantically adequate. This review
  supplies sampled behavioral evidence for that separate question.

The second reviewer independently passed 209 domain tests and the nine original
demo tests. Detailed reports distinguish full test-source inspection from sampled
specification/template review; this is not a line-by-line re-proof of 677 designs.

## Remaining boundaries and next increment

The 284 non-READY designs remain unchanged: 41 NEEDS_FIX, 237 POLICY_BLOCKED,
6 INFRA_BLOCKED. They receive no coverage credit. Browser/React interaction,
PostgreSQL concurrency, deployment/runtime composition and unapproved policy are
outside this review. Standalone business login redirects use the demo's trailing
slash; original non-demo settings differ. The reports qualify that transport
boundary rather than claiming exact production configuration parity.

A proportionate next increment is seven focused fixture/assertion improvements,
with literal expected values and the demonstrated mutants as acceptance checks.
Update the three output-design gaps explicitly; retain the frozen historical
inventory and original Wave 2 execution evidence. Re-run affected suites, the
combined audit and the relevant mutants. Keep behavior/policy fixes separate.
No application, existing test, harness, schema, deployment or business-policy
changes were made during this review. New probe tools are diagnostic artifacts,
not CI approval gates, and preserve their mutations within their own processes.

## Follow-up implementation

[Part 1 hardening](part-1-hardening.md) addresses the seven demonstrated gaps.
This review and its JSON snapshot retain the historical `cb69127` findings;
current probe outcomes and acceptance results are recorded in the follow-up.
