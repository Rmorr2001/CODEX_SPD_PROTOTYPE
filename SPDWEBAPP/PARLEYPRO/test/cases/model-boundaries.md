# Model identity and retention boundaries

Use the [shared fixture contract](../../../../docs/testing/fixture-contract.md).
Actor A uses `make_user(username="a", roles=(...))`; B uses username="b", and so on.
Missing-profile fixtures use `with_profile=False` with no roles/profile fields.
Requests use `login_actor`; CSRF cases use `csrf_client` and real cookie/token pairs.
Polls/current choices are explicit local ORM rows; current choices have no poll FK.
Unless overridden, open P starts at T-10 seconds with counts 0/0 and NULL end.
Closed H/K start at T-20 seconds and end T-1 with counts 0/0 unless overridden.
T is aware UTC 2026-01-15T18:00:00Z; T-1/T-2 mean one/two seconds earlier.
Use `at_time` for each consumed clock and refresh rows named by `snapshot_scope`.
Each equivalent input/actor variant resets its fixture; no request uses real member data.
Public actions create no files/admin logs; identity/roles and unmentioned rows stay unchanged.
These are proposed designs, not executed tests or approved policy.

Raw ORM bypass is explicit corruption setup; it is not request validation.
User deletion is synthetic and isolated, and cannot settle historical retention.

<a id="pp-36a"></a>

### PP-36a — test_current_choice_is_unique_per_nonnull_user

Parent: `PP-36` | Operation: `PP-V02-CAST` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/models.py:21–24`

```text
GIVEN make_user(username="a", roles=("ACTIVE",)) creates A
  AND A has an Aye choice; B has Nay; before = snapshot_scope([A, B, A_choice, B_choice])
WHEN an explicit ORM insert attempts a second Brother_votes row for user A
THEN the database rejects it with IntegrityError inside a scoped atomic savepoint
  AND refreshed A_choice retains its PK/user and Aye value
  AND no duplicate row remains after the savepoint rollback
  AND assert_unchanged(before)
  AND no poll/session/file/audit state changes
```

<a id="pp-36b"></a>

### PP-36b — test_model_choice_validation_accepts_only_declared_nonnull_values

Parent: `PP-36` | Operation: `PP-V02-CAST` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/models.py:22–24`

```text
GIVEN ACTIVE A exists; before = snapshot_scope([A])
  AND unsaved Brother_votes instances use user A
WHEN full_clean runs for Aye, Nay and No Vote, then invalid strings "aye" and "Bad"
THEN declared choices pass and invalid strings raise a choices ValidationError
  AND unsaved validation inserts no Brother_votes row
  AND assert_unchanged(before)
  AND raw ORM save bypass is only a corruption-fixture technique, not input validation
  AND no individual historical ballot model is inferred
```

<a id="pp-36c"></a>

### PP-36c — test_deleting_poll_creator_has_explicit_history_retention_policy

Parent: `PP-36` | Operation: `PP-C03-WRITE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-09: user-cascade historical retention
Source: `SPDWEBAPP/PARLEYPRO/models.py:18,23`

```text
GIVEN ACTIVE A owns open P and closed H and has Aye
  AND ACTIVE B owns closed K and has Nay
  AND before = snapshot_scope([A, B, P, H, K, A_choice, B_choice])
WHEN synthetic A is deleted through the real ORM in an isolated transaction
THEN POL-09 must choose protected deletion, retained/anonymized history or explicit cascade
  AND A-created poll/choice existence must match that selected retention rule
  AND B, K, B_choice and B's profile/roles remain unchanged
  AND deleted history is not invented later from current choices
```
