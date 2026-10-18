# Backend regression coverage

Wave 1 inventories backend behavior. Wave 1.5 turns its bundled scenarios into
named case designs with short GIVEN / WHEN / THEN steps. Wave 2 implements the
reviewed designs. These are specifications, not executable tests or coverage.

| Slice | Test and documentation entry point | Original Wave 1 groups |
| --- | --- | --- |
| AUTHENTICATE | [Identity and members](../../SPDWEBAPP/AUTHENTICATE/test/README.md) | 55 |
| PARLEYPRO | [Polling](../../SPDWEBAPP/PARLEYPRO/test/README.md) | 40 |
| PHILANTHROPY | [Service hours](../../SPDWEBAPP/PHILANTHROPY/test/README.md) | 33 |
| NEWMEMBER | [New-member marks](../../SPDWEBAPP/NEWMEMBER/test/README.md) | 38 |
| HOME | [Public content and demo integration](../../SPDWEBAPP/HOME/test/README.md) | 21 |
| MISC | [Announcements and alerts](../../SPDWEBAPP/MISC/test/README.md) | 30 |

Six `gpt-6.1-sol` agents at medium reasoning produced the original 217 case groups
in commit `c8bbc4e`. Each domain now links those original IDs to the new named
case designs. A group may split into several tests or explicit parameter sets.
The historical group counts above are not passing-test counts.

[Current case readiness](case-readiness.md) lists the 677 named designs and
primary statuses. [The Wave 1.5 handoff](wave-1-5-review.md) explains verification
and the boundary between a readable specification and an executable suite.

For a short example, read
[casting one Aye vote](../../SPDWEBAPP/PARLEYPRO/test/cases/voting.md#pp-07a--test_cast_aye_creates_own_current_choice).
It names the fixture, request, response and records that must remain unchanged.

## Readiness and shared setup

- `READY`: complete preservation design; implement after the shared harness.
- `NEEDS_FIX`: a specific defect prevents the required safe result.
- `POLICY_BLOCKED`: the expected result needs a named business/transport decision.
- `INFRA_BLOCKED`: an additional facility such as PostgreSQL or a browser is needed.

Each case lists its primary status and all additional blockers. READY is a design
assessment, not a claim the case ran. See each domain's case index for details.

[The shared fixture contract](fixture-contract.md) fixes the interface for users,
roles, clocks, requests, storage and state assertions. It is the Wave 2 target;
the helpers/settings do not exist yet. It does not settle business-policy questions.

The user-selected convention is `SPDWEBAPP/<DOMAIN>/test/` (singular):

```text
test/
  README.md                 entry point and commands
  regression-spec.md        inventory, decisions and case links
  cases/*.md                named pseudocode cases grouped by workflow
  test_*.py                 future Wave 2 executable tests
```

Existing placeholder `tests.py` files are unchanged. Discovery must be verified
when executable packages are introduced; no empty package is added just for docs.

[The original agent prompt](wave-1-agent-prompt.md) and
[Wave 1.5 refinement prompt](wave-1-5-agent-prompt.md) record design standards
and file ownership. Each domain owns its business assertions.

[Coordinator review and baseline](wave-1-review.md) records actual execution,
shared ownership decisions, source spot checks and unresolved policy boundaries.

Admin cases stay with their owning domains. AUTHENTICATE covers demo entry and
admin blocking; HOME covers cross-domain fictional seeding and media composition.
These delivery assignments do not move code out of `railway_demo`.
