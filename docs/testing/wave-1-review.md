# Wave 1 coordinator review

## Baseline and execution boundary

All six specifications inspect `prototype/railway` at
`7e25ac2f06b2d88a0220526771585f30df10c57a`. Wave 1 adds documentation only.
Specifications and pseudocode are not executable tests or measured coverage.

All six agent deliverables are present: one testing README and one regression
specification in each business domain. Relative documentation links, duplicate
case identifiers, expected file locations, whitespace, and documentation-only
scope were checked alongside the source spot checks below. The six specifications
contain 217 proposed case groups; these are not an executable test count.

The coordinator reran the existing suite from the repository root:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE PARLEYPRO PHILANTHROPY NEWMEMBER HOME MISC railway_demo --verbosity 1
```

Result: **9 tests passed**, with no Django system-check issues. These are the
existing demo tests; the six domain test modules remain placeholders. The
interpreter path above is this session's environment, not portable setup advice.
See the demo README for ordinary `.venv` setup. Agents did not execute the
proposed cases or read credentials/private member data.

## Shared decisions for the implementation handoff

- Use singular `SPDWEBAPP/<DOMAIN>/test/` for its README, specification and future
  `test_*.py` files. Add package initializers and verify discovery in Wave 2;
  do not count existing empty `tests.py` scaffolds as implemented tests.
- AUTHENTICATE owns the shared role-decorator contract specification even though
  the decorator source is in PARLEYPRO. PARLEYPRO and other domains own checks
  of their mounted endpoints. Keep source ownership unchanged.
- AUTHENTICATE proposes shared isolated settings, explicit-role user/profile
  factories, controlled clocks and temporary storage. The coordinator reconciles
  those interfaces before implementation; no domain builds a separate harness.
- Each domain owns its application-specific admin cases. AUTHENTICATE owns demo
  entry and public admin blocking; HOME owns fictional seeding and media/URL
  composition integration. Actual demo code remains in `railway_demo`.
- Keep approved business assertions reusable across template handlers and future
  DRF adapters. Status codes, redirects, JSON shapes and XLSX parsing belong to
  explicit adapter assertions, not incidental implementation snapshots.
- Use PostgreSQL to establish PostgreSQL concurrency guarantees. SQLite results
  do not establish locking/isolation or prove race safety.

## Source spot checks and unresolved policy

The coordinator independently checked the poll-close helper, mark batch creation
and approval helper, philanthropy approval helper, and DST inclusion-tag behavior.
The current code confirms several risks that need defect regressions or policy
decisions rather than passing preservation tests:

- A non-executive poll-close request can proceed after adding an error message.
  Closing stores poll aggregates and resets votes in separate writes.
- Profile, majors, photo replacement and singleton replacement have destructive
  steps before all related work succeeds. Database and file rollback are distinct.
- Approval helpers accept unknown actions without a controlled rejection;
  repeated/reversed/self decisions need explicit policy. Direct-helper boundary
  protection must be designed alongside actual callers.
- Fractional hours are accepted by the request parser but stored in an integer
  field. Chair-role names differ between the dashboard flag and permission gate.
- Marks have different role requirements for approval denial and edit denial;
  target eligibility and duplicate/empty batch behavior are not settled policy.
- Spreadsheet grouping by full name and user-controlled cell interpretation
  require dedicated integrity/security cases.
- Alert rendering permits configured HTML through the template, and DST/date
  behavior needs actual transition-boundary specifications.

The domain documents hold the authoritative case details and additional findings.
These spot checks are not execution of proposed regressions or approval of every
case. Preserve/defect/decision labels remain subject to review. Unambiguous
preservation cases can proceed after fixture/discovery verification; unsafe or
ambiguous behavior is not silently frozen as the future API contract.
