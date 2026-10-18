# Regression case design readiness

Wave 1.5 expands all 217 original groups into 677 independently named designs.
These are pseudocode specifications, not implemented or executed tests. Each
domain index links the original groups to its new cases and records all blockers.

| Domain index | Original groups | Named designs | READY | NEEDS_FIX | POLICY_BLOCKED | INFRA_BLOCKED |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [AUTHENTICATE](../../SPDWEBAPP/AUTHENTICATE/test/case-index.md) | 55 | 157 | 76 | 3 | 78 | 0 |
| [PARLEYPRO](../../SPDWEBAPP/PARLEYPRO/test/case-index.md) | 40 | 114 | 58 | 5 | 48 | 3 |
| [PHILANTHROPY](../../SPDWEBAPP/PHILANTHROPY/test/case-index.md) | 33 | 118 | 66 | 11 | 41 | 0 |
| [NEWMEMBER](../../SPDWEBAPP/NEWMEMBER/test/regression-spec.md) | 38 | 88 | 50 | 14 | 24 | 0 |
| [HOME](../../SPDWEBAPP/HOME/test/case-index.md) | 21 | 97 | 63 | 6 | 26 | 2 |
| [MISC](../../SPDWEBAPP/MISC/test/case-index.md) | 30 | 103 | 80 | 2 | 20 | 1 |
| Total | 217 | 677 | 393 | 41 | 237 | 6 |

READY is a design assessment: unambiguous preservation cases can be implemented
after the shared harness and discovery are verified. It does not claim execution
or establish business approval. Cases requiring an undefined policy use
POLICY_BLOCKED even if they also need a defect fix or PostgreSQL/browser support.

Start Wave 2 with [the fixture contract](fixture-contract.md), then choose cases
from the READY columns. Keep defect regressions/fixes and policy decisions
separately reviewable. Do not turn blocked cases into passing coverage with
arbitrary assertions, skips or expected failures.
