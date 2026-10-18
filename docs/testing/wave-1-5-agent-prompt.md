# Wave 1.5 case clarification prompt

Refine the assigned domain's Wave 1 documentation into readable, implementation-
ready test designs. The user's request is to fix dense prose, split bundled
scenarios, settle shared fixture interfaces and identify actionable cases.
No test or application implementation is authorized in this wave.

## Scope and ownership

Read AGENTS.md, your domain `test/README.md` and `test/regression-spec.md`, and
[the fixture contract](fixture-contract.md). Write only Markdown beneath your
assigned `SPDWEBAPP/<DOMAIN>/test/`. Six agents share one checkout. Do not change
Git state, shared files, code/config/dependencies, secrets, or other domains;
do not run app tests, use network or spawn agents. Preserve source-backed facts
and unresolved policy; inspect source read-only if a case is unclear.

## Required organization

- Keep README a short entry point and regression-spec a concise inventory,
  role matrix, decisions and links. Move detailed cases into `test/cases/*.md`,
  grouped by workflow. Avoid new directories containing a single trivial case.
- Replace dense case paragraphs/tables with one independently named test per
  behavior. Parameterize equivalent input variants only if action, contract,
  status and state expectations are the same; list the concrete values.
- Preserve each original case ID as a parent. A split receives a suffix, e.g.
  `PP-07a`. Include an old-ID → new-ID mapping covering every original group;
  do not silently drop scenarios, merge policy and preserve cases, or inflate
  counts with duplicated assertions. Old source baseline remains recorded;
  the documentation-refinement baseline is `c8bbc4e`.
- Each case must use exactly the heading/metadata/pseudocode shape below.
  Use short readable lines, generally no more than 100 characters. Prefer
  8–16 lines of pseudocode; split responsibilities instead of long prose.

````markdown
### PP-07a — test_cast_aye_creates_own_choice

Parent: `PP-07` | Operation: `PP-V02-CAST` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN actor A has only ACTIVE and no current choice
  AND B has a Nay choice; poll P is open
WHEN A POSTs /poll/ with {aye: "1"}
THEN response is 200
  AND A has exactly one choice row with value Aye
  AND B's choice and P's saved counts/end time are unchanged
```
````

Each pseudocode block contains GIVEN, WHEN and THEN; secondary conditions may
use AND. Name concrete payloads, response assertions and changed/unchanged state.
Use fixture names from the shared contract but do not repeat its implementation.
Avoid context-dependent shorthand such as "valid", "same as above", "all U"
or "approved behavior" without naming what it means or linking a precise rule.

## Readiness

Each case has exactly one primary status and lists all other blockers:

- `READY`: complete, unambiguous preservation design, expected to pass current
  source once the common harness exists; not a claim of execution/approval.
- `NEEDS_FIX`: a concrete defect prevents safe expected behavior. State a
  specific safety assertion, link the defect and keep code fixes separate.
- `POLICY_BLOCKED`: expected behavior needs a business/transport decision. Name
  the decision and candidate outcomes; do not invent a final expected status,
  ownership rule, size limit, transition or retention rule.
- `INFRA_BLOCKED`: expected behavior is clear but a case-specific facility such
  as PostgreSQL/browser is missing. Name it and any policy/fix dependencies.

Use POLICY_BLOCKED as primary when expected outcomes remain undefined, even if
defects/infra also exist. Do not label a defect or policy case READY. A blocked
case's THEN may describe a concrete safety invariant plus explicit conditional
outcomes tied to named decisions, never a pretend settled contract.

## Handoff

Add a case-index table: new ID, test_name, primary status, case file/anchor.
Provide status counts and an original-to-new mapping. Do not keep the old dense
case prose alongside its replacement. Keep source/role/decision references
available and fix relative links. Distinguish current from proposed commands.

Check case-ID and test-name uniqueness, old-group completeness, status counts,
metadata format, local links and no dropped fixture/failure/unchanged-state
assertions. Report changed files, old/new counts and unresolved decisions. Do not
claim application tests or proposed cases ran. The coordinator verifies cross-
domain fixtures and the final diff before committing.
