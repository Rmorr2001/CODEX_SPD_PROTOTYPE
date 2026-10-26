# PARLEYPRO — chapter decisions

Owns a single open chapter motion, global per-user Aye/Nay choices, closure and
stored historical results. Both frontends operate on the same records.

- `urls.py` / `views.py`: legacy HTML under `/poll/`.
- `api/urls.py`: REST routes under `/api/v1/polls/`; `serializers.py` owns JSON
  contracts, `reads.py` snapshots, `commands.py` HTTP mutation adapters.
- `operations.py`: shared validation, ACTIVE voting and ACTIVE+EXEC create/close,
  serialized atomic transitions. The internal `PollWorkflowLock` row serializes
  the global ballot store, including creation when no motion is open.
- `pp_functions.py`: supported count helper and HTML action translation.
- `test/`: regression designs, mappings and executable tests.

REST collection GET returns current/closed motions, caller-only choice and
management capability. POST creates a named motion. `GET <id>/` returns detail;
`PUT <id>/vote/` accepts `choice: Aye|Nay`; `POST <id>/close/` saves results and
resets current ballots. All require ACTIVE; creation/closure also require EXEC.
Writes use Django sessions and real CSRF protection. Invalid input is400,
denied access403, missing target404 and conflicting state409. No voter identities
are disclosed. Results refresh every five seconds in the visible React list.

Creating a second open motion is rejected. Repeated same-choice voting keeps
one user row; closing an already closed ID cannot close another motion or reset
its votes. A failed reset rolls back both stored totals and closure. Global tally
membership and chapter-wide executive closure preserve established behavior;
no quorum, pass threshold, new eligibility policy or per-poll ballots are invented.
Legacy out-of-band multiple-open rows still read newest-first; supported writes
never create them. Admin is not a prototype write surface.

See [milestone scope and release impact](../../docs/migration/functional-milestone-1.md).
`test/test_transactions_api.py` exercises both frontend directions, real CSRF,
role denial, repeat/stale operations and failure rollback. `test/test_read_api.py`
retains read privacy/order tests. Run with the root AGENTS.md standalone commands.
Browser transactions live in `frontend/test/zz-transactions.spec.ts`. No new
credentials or runtime configuration keys are required.


Management controls in both interfaces use operations.can_manage_polls, the
same ALL-role boundary as create/close. test/test_ui_permissions.py covers normal
ACTIVE, ACTIVE+EXEC, EXEC-only and anonymous capabilities plus forged closure.
See [the permission correction](../../docs/migration/permission-affordances.md).
