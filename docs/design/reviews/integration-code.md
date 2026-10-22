# Cross-screen integration correctness review

**Verdict: PASS.** Integration corrections preserve the original regression
intent while recognizing the delivered read APIs and approved demo copy.

Scope: the final changes to `HOME/test/test_demo_seed.py`,
`SPDWEBAPP_CORE/api/test/test_contract.py`, `SPDWEBAPP_CORE/web_settings.py` and
the PHILANTHROPY service-event serializer. No application files were changed by
this reviewer, and no additional browser run was started for this review.

## Findings

- The seed test changes only the exact expected announcement sentence to the
  S04-reviewed neutral role-selection instruction. Its test identity, active
  flag checks, exact dashboard manifest assertion and unrelated-record canary
  remain intact. This is an approved copy update, not a weakened seed test.
- The original one-path schema assertion was obsolete after delivery. Its
  replacement asserts exactly **11** documented GET-only read paths, successful
  response contracts, no authentication requirement on public reads and exact
  cookie authentication on the six protected reads. Unknown API routes, denied
  anonymous defaults and actual authenticated session checks remain covered.
- The session endpoint permits anonymous status reads and authenticates cookies
  when present. The current schema assertion verifies optional authentication;
  as optional strengthening it could assert the exact cookie-plus-empty security
  list rather than only membership of the empty requirement. Existing identity
  tests independently exercise actual caller-only cookie authentication.
- Explicit `LivenessStatusEnum` and `ApprovalStatusEnum` names resolve ambiguous
  schema field-name inference without changing REST defaults, runtime permissions,
  response values, models or stored data. The schema test asserts their exact
  values. The service serializer now obtains canonical approval choices from
  its owning model; all three raw values remain approved/requested/denied.

## Independent checks

- **2 targeted tests passed**: the expanded schema/auth contract and the exact
  seed alert/dashboard manifest case, using standalone synthetic settings.
- **OpenAPI generation and validation passed** with `--validate --fail-on-warn`,
  writing only the non-secret generated schema to
  `/workspace/work/integration-review-schema.yaml`.
- `git diff --check` passed. A first targeted command misspelled the seed method
  selector and produced one discovery error; the corrected command above ran
  both actual methods and passed. That invocation error was not an app defect.

The coordinator separately reports the combined 44-browser run passed. This
review does not count that as independently rerun evidence; final backend audit,
mutation and demo results belong to the coordinator's delivery record. The S09
single initial login timeout and successful isolated rerun remain documented in
[its review](S09-code.md), rather than being erased by a later aggregate pass.
