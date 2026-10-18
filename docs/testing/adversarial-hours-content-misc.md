# Independent adversarial review: service hours, public content and alerts

Reviewed `cb69127`, branch `prototype/railway`, on 2026-10-18. This reviewer did not implement the regression tests. Findings below concern preservation during the Django REST/Vite React migration; they are not proposed runtime fixes or new business policy.

## Ranked findings

### 1. Medium: HOME can show the wrong officer under an office while all 63 tests pass

Source: `SPDWEBAPP/HOME/views.py:49–55`. READY contract `HOME-T02c`, `SPDWEBAPP/HOME/test/cases/public-routes.md:142`, requires each holder-office pair exactly once. Its mapped method, `PublicPageTests.test_board_role_order_and_multi_office_pairs` in `SPDWEBAPP/HOME/test/test_public_pages.py:114–142`, checks office order, pair uniqueness and three particular President/Philanthropy pairs. It does not check the other officers' identities, or the complete expected pair set.

The process-local `home_board` mutation replaces exactly:

```python
Brother_Profile.objects.filter(roles=role)
```

with:

```python
Brother_Profile.objects.filter(roles=role if role_code != 'EXT_VP' else Role.objects.get(name='PRESIDENT'))
```

The complete existing HOME suite passes **63/63** with this defect. It associates President profiles with External Vice President and omits the actual external VP. This is a meaningful public content identity error, not a tie-order or eligibility-policy choice. The unchanged source is correct.

Independent `BoardWitness.test_external_vp_is_correct_profile` creates two distinct synthetic profiles: `president` has ACTIVE/EXEC/PRESIDENT; `vp` has ACTIVE/EXEC/EXT_VP. Anonymous GET `/executive-board/` must return precisely `(President, president_profile)` and `(External Vice President, vp_profile)`. Baseline passes; mutant fails one assertion, zero errors: the observed VP profile is the President profile (logged IDs 75 rather than 76); restored suite plus witness passes **64/64**.

Minimum useful addition: compare the complete set of `(office_display, profile.pk)` pairs against fixture-owned expected pairs, keeping the declared office ordering check separate and avoiding a tie-order policy.

### 2. Low: philanthropy descending progress ordering is checked with an already sorted fixture

Source: `SPDWEBAPP/PHILANTHROPY/views.py:44`. READY `PH-C18a`, `SPDWEBAPP/PHILANTHROPY/test/cases/statistics.md:148–149`, requires sorted progress `[A:10,B:5,C:0]`. The mapped `StatisticsTests.test_chapter_and_personal_approved_totals_are_scoped`, `test_statistics.py:81–114`, creates profiles in that same order. The assertion can pass without the view sorting.

The `ph_sort` mutation replaces:

```python
sorted(brothers_progress, key=lambda x: x['total_hours'], reverse=True)
```

with `brothers_progress`. The complete existing PHILANTHROPY suite passes **66/66**. Independent `SortingWitness.test_descending_progress_reverses_creation_order` creates ACTIVE `first` with 2 approved hours and then ACTIVE `later` with 7 approved hours, logs in `first`, and GETs `/philanthropy/?year=2026`. Baseline returns `[later, first]`; mutant returns `[first, later]` (logged IDs `[9,10]` versus `[10,9]`), causing one assertion failure, zero errors. Restored suite plus witness passes **67/67**.

Minimum useful addition: assign totals contrary to profile insertion order and assert the ordered owner/hour pairs. No policy concerning equal totals is necessary.

### 3. Low, design extension: dashboard member names can disappear undetected

`SPDWEBAPP/PHILANTHROPY/views_functions.py:53` supplies `full_name` to the dashboard link at `templates/philanthropy_dashboard.html:144`. Unlike findings 1–2, this is **not an unimplemented explicit READY assertion**: the frozen statistics contracts enumerate owner IDs/hours but do not independently require display-name output. It is a small source-preservation extension for the migration.

The `ph_name` mutation replaces exactly `'full_name': f"{brother.firstName} {brother.lastName}",` with `'full_name': '',` in `collect_philanthropy_statistics`. All **66 existing domain tests pass**, although member links lose their labels. Independent `NameWitness.test_progress_preserves_member_display_name` creates one ACTIVE synthetic profile named Alex Synthetic, logs in, GETs `/philanthropy/?year=2026`, and asserts both its context name and rendered name. Clean witness passes; mutant fails one assertion (`'' != 'Alex Synthetic'`), zero errors; restored suite plus witness passes **67/67**. Minimum useful addition: one literal expected profile display-name assertion in the dashboard context and HTML. This needs no new access or naming policy for the existing ordinary fixture.

## Execution and new mutation evidence

All commands below run from `/workspace/CODEX-SPD-PROTOTYPE`, using synthetic standalone settings, in-memory SQLite and temporary media. No runtime secret configuration, network, deployment or real data was used. Source and tracked tests/harness were never mutated. The script alters function code objects, or one admin-instance hook, only inside its process and restores them in `finally` blocks.

Reproduce each probe:

```sh
/workspace/work/spd-mizzou-venv/bin/python work/adversarial_hours/probe_content_misc.py ph_sort
/workspace/work/spd-mizzou-venv/bin/python work/adversarial_hours/probe_content_misc.py ph_name
/workspace/work/spd-mizzou-venv/bin/python work/adversarial_hours/probe_content_misc.py ph_owner
/workspace/work/spd-mizzou-venv/bin/python work/adversarial_hours/probe_content_misc.py home_board
/workspace/work/spd-mizzou-venv/bin/python work/adversarial_hours/probe_content_misc.py home_media
/workspace/work/spd-mizzou-venv/bin/python work/adversarial_hours/probe_content_misc.py misc_filter
/workspace/work/spd-mizzou-venv/bin/python work/adversarial_hours/probe_content_misc.py misc_audit
```

Each command runs the **full affected domain suite** cleanly, under mutation and after restoration; independent witnesses are run separately where specified. The script explicitly selects `SPDWEBAPP_CORE.testing.settings`. JSON contains actual executed test counts, assertion failures, errors, skips and affected IDs; per-phase logs retain tracebacks. Artifacts are under `work/adversarial_hours/<probe>.json` and `<probe>-{baseline,mutant,restored}.log`; witness phases have additional `-witness-` logs. No aggregate mutation percentage is claimed.

| New probe | Full clean | Existing suite under mutation: failures / errors | Restored | Meaning |
| --- | ---: | ---: | ---: | --- |
| `ph_sort` | 66 pass | 0 / 0, survivor | 67 pass including witness | Ranked finding 2 |
| `ph_name` | 66 pass | 0 / 0, survivor | 67 pass including witness | Finding 3, design extension |
| `ph_owner` | 66 pass | 3 / 0 | 66 pass | Approval ownership and downstream state protected |
| `home_board` | 63 pass | 0 / 0, survivor | 64 pass including witness | Ranked finding 1 |
| `home_media` | 63 pass | 4 / 2 | 63 pass | Seed media omission detected; errors separated below |
| `misc_filter` | 80 pass | 4 / 0 | 80 pass | Inactive announcement disclosure detected |
| `misc_audit` | 80 pass | 6 / 0 | 80 pass | Missing admin change audit detected |

Exact additional mutation fragments and outcomes:

- `ph_owner`: in `PHILANTHROPY.views_functions.philanthropy_approval_POST`, replace `event.save()` with `event.user = request.user` followed by the original save. Both initial approval and initial denial fail their comparisons of all fields outside the three allowed decision fields. `ApprovedProjectionTests.test_submit_then_approve_updates_all_approved_projections_once` also fails its preserved-owner snapshot. Three assertion failures, no setup errors. This demonstrates ownership/state preservation beyond a response-status assertion.
- `home_media`: in `railway_demo.management.commands.seed_railway_demo.seed_home`, replace `shutil.copyfile(source, media / "rush_slides/demo-slide.webp")` with `pass`. Four assertion failures cover observed copy count, expected media existence, missing second-copy failure and partial-failure retry. Two additional `FileNotFoundError` errors come from test bodies reading the omitted slide bytes (`test_first_seed_creates_public_content_and_media`, `test_late_seed_db_failure_rolls_back_all_database_writes`); these are **not counted as assertion kills or setup success evidence**. The four assertion failures independently show this integration defect is detected.
- `misc_filter`: in `AUTHENTICATE.views.dashboard`, replace `AnnouncementAlert.objects.filter(is_active=True)` with `AnnouncementAlert.objects.all()`. The MISC-owned integration tests for active-only selection, empty/inactive-only state, subsequent activation changes and eligible-role visibility each fail assertions. Four failures, zero errors; the source function remains the real authenticated dashboard throughout.
- `misc_audit`: temporarily replace only the registered `AnnouncementAlert` admin instance's `log_change` with `lambda *a, **k: None`. Six assertion failures include scoped history, a valid-CSRF change, profileless staff change, preserved inactive flag, excluded-field payloads and save redirects. The model writes still happen; the tests reject absent audit effects. This is a simulated regression in the inherited Django admin behavior, not a change to application ownership policy.

Independent clean command results:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY.test HOME.test MISC.test --noinput
# 209 tests, 23.452s, OK; zero failures/errors/skips; no system-check issues

DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.demo_settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test railway_demo --noinput
# 9 tests, 2.708s, OK; zero failures/errors/skips; no system-check issues
```

Logs: `work/adversarial_hours/content-baseline.log` and `demo-baseline.log`. Every probe's own full clean/restored run also passed, as recorded above. Counts establish execution only; the findings depend on changed behavior and assertion inspection.

## Inspected scope and substantive preservation

Read root `AGENTS.md`; no more specific AGENTS file was present in these domains. Read `docs/testing/{README,wave-2-goals,wave-2-results,fixture-contract}.md`, the frozen inventory's complete entries for these three domains, domain testing READMEs and findings. Compared representative READY specifications directly with mapped test bodies, especially statistics, office membership, submissions/decisions, export cells, seed refusal/media failures and admin writes/deletions. This is an independent focused adversarial review, not a claim to have re-proved every clause in every case document.

Runtime inspection covered all PHILANTHROPY/HOME/MISC model, view/helper, admin and URL code; relevant template branches were sampled directly. Reviewed `railway_demo` seed command, middleware, context, cache-header function, persona view and original nine tests. Persona security in depth belongs to the other reviewer. Reviewed the executable test modules in all three domain packages, their local constructors/assertions, and shared base/factories/helpers/state/settings. Dense seed identity manifests and other case-document prose were sampled rather than independently re-enumerated.

Representative source-to-test traces:

- **PHILANTHROPY create/decision/read/export:** real logged-in request creates an actor-owned requested event; forged owner/status/audit payloads are ignored; real CSRF is exercised separately. Initial approve/deny changes exactly status, approver and decision timestamp while preserving owner and original fields. Integration follows submit through approval to own/chapter totals, history and parsed XLSX numeric cells. Statistics distinguish approved/requested/denied, other owners, inactive owners and July/June boundaries; history independently checks descending year buckets and ownership. Export assertions inspect actual workbook cells, numeric/string types, exclusion of non-approved events, totals and thresholds. They do not merely re-run a helper to compute expected values.
- **PHILANTHROPY admin/edit/delete:** tests grant actual staff/model permissions, do not infer them from PHIL_CHAIR, and verify denied changes leave rows/logs unchanged. Add success checks persisted fields and log identity. Edit GET, missing IDs and CSRF are tested; successful business edits and authorized hard-delete behavior are deliberately blocked in the frozen inventory, not omitted READY implementations. `last_edited_by` deletion's SET_NULL behavior is explicitly tested.
- **HOME content/admin:** singleton create/replace/update, slide persistence and deletion use real rows and synthetic bytes. Admin routes exercise distinct model permissions, real CSRF, selected deletes/logs, actual sortable payloads and failure rollback. The singleton admin insertion failure is injected after the destructive delete hook, so restoring the old row tests a real request transaction; direct-model destructive failure policy remains separately blocked.
- **Seed/media integration:** fixed synthetic manifests check fictional names/roles/workflows and unusable passwords; repeat seeding checks stable PKs, fields, relations and real media while permitting randomized unusable-password markers. Unrelated records have their own sentinel snapshots. `TransactionTestCase` refusal, late DB failure, first/second-copy failure and retry tests distinguish database rollback from surviving files; they do not claim filesystem rollback. The dropped-media probe confirms these tests observe the seed's cross-domain/file side effects.
- **MISC records/admin/integration:** timestamps/defaults and escaped announcement rendering are checked with real models. Active-only selection and role redirects use actual AUTHENTICATE dashboard routes. Admin success checks rows and actor/object/action-specific logs; deletion checks selected versus unselected records; transaction tests inject failures after actual logging or deletion and inspect rollback. Profileless staff can perform a real permitted change. No invented creator ownership rule is imposed on global announcement content.

The fixtures do not grant implicit chapter or staff roles. `force_login` is used for authorization scope, not evidence of password authentication. Mocking inspected here principally targets clocks, deliberate IO/DB failures, impossible fallback injection and the unused MISC callable's render-argument capture. The latter is a narrow callable/context test and does not prove a mounted rendered endpoint; another test explicitly proves that no MISC view is mounted.

No broad vacuous-test or mocked-business-rule pattern was found. The demonstrated gaps concern incomplete identity assertions, a fixture that coincides with output order, and a missing display-name design. Scoped snapshots cannot prove that every uncaptured table/file remained unchanged; the reviewed suites supplement them with relevant counts and outputs rather than claiming universal state capture.

## Boundaries and verdict

Frozen non-READY designs remain **284 overall**; these owned domains account for **52 PHILANTHROPY + 34 HOME + 23 MISC = 109**. In particular, philanthropy precision, repeat/reverse/self decisions, successful edit/reapproval, export access/scope/name collisions/formula injection, direct-model singleton failure/file cleanup, media symlink escape, raw DST override HTML and physical fall-transition timing already have explicit blockers. Those are not newly discovered READY omissions and were not used to manufacture an adverse verdict. No policy is chosen here.

HOME media serving tests intentionally bind the real static view to temporary media through a test URLconf. They verify that local serving boundary, not deployed Railway routing or WhiteNoise. Browser JavaScript, collected static delivery, PostgreSQL concurrency, external services and deployment remain outside this evidence. This review does not independently validate the coordinator's complete mapping audit or mutation harness, and does not assess REST serializers, new API contracts or the future React UI.

**Verdict: adequate with gaps** for the inspected migration-preservation scope. MISC has substantive demonstrated filtering/audit protection; PHILANTHROPY preserves important ownership and approved projections; HOME seed/media/admin checks are meaningful. The two narrow READY survivor findings and the display-name extension are useful additions before relying on these suites to protect reconstructed dashboard/office outputs. Passing counts or coverage alone would have concealed these gaps. This is a practical migration baseline, not complete behavioral equivalence or resolution of the documented blockers. No fixes were made.

## Preserved review artifacts

The coordinator preserved portable copies of the probe scripts and a JSON result
snapshot. See [repeatable commands](../../tools/testing/adversarial/README.md)
and [the integrated review](adversarial-review.md). Commands above record the
actual scratch paths used by this reviewer; raw logs remain ignored.
