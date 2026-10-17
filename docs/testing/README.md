# Backend regression coverage

Wave 1 designs six domain-owned regression specifications. Wave 2 implements
them after source verification and reconciliation of shared fixture contracts.
The specifications are proposals, not implemented tests or approved policy.

| Slice | Test and documentation entry point | Proposed case groups |
| --- | --- | --- |
| AUTHENTICATE | [Identity and members](../../SPDWEBAPP/AUTHENTICATE/test/README.md) | 55 |
| PARLEYPRO | [Polling](../../SPDWEBAPP/PARLEYPRO/test/README.md) | 40 |
| PHILANTHROPY | [Service hours](../../SPDWEBAPP/PHILANTHROPY/test/README.md) | 33 |
| NEWMEMBER | [New-member marks](../../SPDWEBAPP/NEWMEMBER/test/README.md) | 38 |
| HOME | [Public content and demo integration](../../SPDWEBAPP/HOME/test/README.md) | 21 |
| MISC | [Announcements and alerts](../../SPDWEBAPP/MISC/test/README.md) | 30 |

The six agents used `gpt-6.1-sol` at medium reasoning. Their specifications contain
217 proposed case groups; a group may have multiple inputs/assertions. This is a
design inventory, not 217 implemented or passing tests. Defects and policy-gated
cases remain separate from proposed preservation contracts.

The user-selected convention is `SPDWEBAPP/<DOMAIN>/test/` (singular), containing
the test README and regression specification now, with executable `test_*.py`
files added in Wave 2. Existing placeholder `tests.py` files are unchanged in
Wave 1. Discovery must be verified when the executable packages are introduced.

[The full shared agent prompt](wave-1-agent-prompt.md) defines design standards,
file ownership and the Wave 1 handoff contract. Shared test settings/factories
are proposals until coordinator verification; each domain owns its assertions.

[Coordinator review and baseline](wave-1-review.md) records actual execution,
shared ownership decisions, source spot checks and unresolved policy boundaries.

Admin cases stay with their owning domains. AUTHENTICATE covers demo entry and
admin blocking; HOME covers cross-domain fictional seeding and media composition.
These delivery assignments do not move code out of `railway_demo`.
