# Failure phases and concurrent schedules

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

Use `TransactionTestCase`/autocommit for persistence phases. Inject only the named
failure boundary; never replace counting or lifecycle logic. Race workers require
PostgreSQL, separate connections/clients, bounded synchronization, propagated errors,
and finally cleanup. No SQLite outcome establishes PostgreSQL safety.

<a id="pp-21a"></a>

### PP-21a — test_count_query_failure_leaves_close_state_untouched

Parent: `PP-21` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-06: failure transport
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:30–38`

```text
GIVEN A has only EXEC and ACTIVE, owns open P, and has Aye; ACTIVE B has Nay
  AND TransactionTestCase/autocommit; before = snapshot_scope([A, B, P, A_choice, B_choice])
WHEN A POSTs {end_vote: "1"} and a database count-query boundary raises before save
THEN P stays open with its original counts; both choices retain their values
  AND assert_unchanged(before)
  AND POL-06 must choose explicit failure response or documented exception transport
  AND no reset, file write or admin audit row is allowed
  AND real counting logic is not replaced by mocked totals
```

<a id="pp-21b"></a>

### PP-21b — test_poll_save_failure_before_write_leaves_choices_untouched

Parent: `PP-21` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-06: failure transport
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:35–41`

```text
GIVEN A has only EXEC and ACTIVE and owns open P; A has Aye
  AND TransactionTestCase/autocommit; before = snapshot_scope([A, P, A_choice])
WHEN real counts complete but an injected poll-save failure occurs before its write
  AND the action was POST /poll/ with {end_vote: "1"}
THEN refreshed P remains open with prior counts; A_choice remains Aye
  AND assert_unchanged(before); no reset persisted
  AND POL-06 chooses failure response rather than approving the current 500
  AND no choice, poll or audit row is created
```

<a id="pp-22a"></a>

### PP-22a — test_reset_failure_has_atomic_or_recoverable_close_contract

Parent: `PP-22` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-06: atomicity or recovery; DEF-03: partial persistence
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:35–41`

```text
GIVEN A has only EXEC and ACTIVE and owns open P; A has Aye; ACTIVE B has Nay
  AND TransactionTestCase/autocommit; before = snapshot_scope([A, B, P, A_choice, B_choice])
WHEN real poll.save persists counts 1/1 and end T during POST {end_vote: "1"}
  AND the reset update raises before its database write
THEN POL-06 must choose rollback or an explicit recoverable partial-close state
  AND rollback means open P with old counts and original choices
  AND recovery must preserve counts 1/1 and prevent duplicate/lost accepted choices
  AND actor identities, poll metadata and unrelated history never change
```

<a id="pp-22b"></a>

### PP-22b — test_retry_after_partial_reset_failure_can_recover_without_recount_loss

Parent: `PP-22` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-06: repair/retry protocol; DEF-03
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:24–41`

```text
GIVEN A has only EXEC and ACTIVE; A owns P already closed at T with counts 1/1
  AND injected prior reset failure left A=Aye and ACTIVE B=Nay
  AND before = snapshot_scope([A, B, P, A_choice, B_choice])
WHEN A retries POST /poll/ with {end_vote: "1"}
THEN POL-06 must choose retry recovery or an explicit separate repair operation
  AND original close counts/end cannot be overwritten with zero or double-counted
  AND choice cleanup and response follow that repair rule
  AND P's PK/name/creator/start and both choice ownerships remain unchanged
```

<a id="pp-23a"></a>

### PP-23a — test_dual_choice_second_save_failure_has_defined_atomicity

Parent: `PP-23` | Operation: `PP-V02-CAST` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-02 and POL-06: multi-key handling and partial-write outcome
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:66–71`

```text
GIVEN A has only ACTIVE, owns open P, and has No Vote; B has Nay
  AND TransactionTestCase/autocommit; before = snapshot_scope([A, B, P, A_choice, B_choice])
WHEN A POSTs {nay: "1", aye: "1"}; real first Nay save succeeds
  AND an injected second Aye-save failure occurs before its write
THEN POL-02 must first choose reject-dual-key or an accepted precedence rule
  AND POL-06 then defines rollback/recovery if that path can perform two writes
  AND P/B_choice and actor/profile ownership must remain unchanged
  AND an incidental surviving Nay is not treated as an approved successful vote
```

<a id="pp-23b"></a>

### PP-23b — test_first_choice_save_failure_after_default_row_creation

Parent: `PP-23` | Operation: `PP-V02-CAST` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-06: default-row failure/retry semantics
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE, owns open P, and has no choice; B has Nay
  AND TransactionTestCase/autocommit; before = snapshot_scope([A, B, P, B_choice])
WHEN A POSTs {aye: "1"}; real get_or_create inserts a No Vote row
  AND an injected Aye-save failure occurs before its write
THEN POL-06 must choose rollback of creation or a documented harmless default row
  AND failure response and A-row existence follow that selected rule
  AND no accepted Aye may be reported if it was not persisted
  AND assert_unchanged(before); no B/P/role changes are permitted
```

<a id="pp-24a"></a>

### PP-24a — test_committed_vote_before_close_is_counted_on_postgresql

Parent: `PP-24` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `INFRA_BLOCKED` | Blockers: PostgreSQL test database; independent connections and bounded synchronization
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:30–41,60–71`

```text
GIVEN PostgreSQL TransactionTestCase and two real independent Django connections
  AND ACTIVE A has No Vote; EXEC+ACTIVE B owns the only open P
WHEN A's client commits POST {aye: "1"} before B begins any close count query
  AND B's separate client POSTs {end_vote: "1"} with a bounded barrier
THEN both responses are 200 and refreshed P stores counts 1/0 with a nonnull end
  AND A's same choice row is No Vote; P's creator/name/start are unchanged
  AND workers join within timeout, propagate errors and close connections in finally
  AND SQLite success is not evidence for this PostgreSQL schedule
```

<a id="pp-24b"></a>

### PP-24b — test_vote_between_count_and_reset_has_defined_acceptance_boundary

Parent: `PP-24` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-01/POL-06; DEF-03; PostgreSQL independent connections
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:30–41`

```text
GIVEN PostgreSQL workers use separate clients/connections and bounded events
  AND ACTIVE A has No Vote; EXEC+ACTIVE B owns open P
WHEN B reads close counts; A commits POST {aye: "1"} before B's reset write
THEN POL-01/POL-06 must define accepted versus rejected late cast
  AND an accepted vote cannot disappear uncounted; a rejected cast cannot report success
  AND saved totals, A's choice and both responses follow that selected boundary
  AND P's creator/name/start and unrelated history stay unchanged
  AND workers join/propagate exceptions/close connections, with no sleep-based ordering
```

<a id="pp-24c"></a>

### PP-24c — test_vote_after_reset_has_explicit_closed_poll_policy

Parent: `PP-24` | Operation: `PP-V02-CAST` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-01/POL-06; PostgreSQL independent connections
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:40–41,60–71`

```text
GIVEN PostgreSQL workers use separate clients/connections and bounded events
  AND EXEC+ACTIVE B owns P; ACTIVE A has No Vote
WHEN B commits close and reset before A POSTs {aye: "1"}
THEN POL-01/POL-06 must choose closed-poll rejection or explicit staging elsewhere
  AND P's finalized counts/end cannot change because of that later cast
  AND A-row value and transport response follow that selected rule
  AND no residual choice is silently assigned to a nonexistent poll ballot
  AND workers terminate/close connections and preserve unrelated history
```

<a id="pp-24d"></a>

### PP-24d — test_vote_change_between_count_queries_has_coherent_snapshot_policy

Parent: `PP-24` | Operation: `PP-V02-COUNT` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-06: consistent count snapshot; DEF-03; PostgreSQL
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:11–14,30–32`

```text
GIVEN PostgreSQL separate connections; ACTIVE A starts Nay
  AND EXEC+ACTIVE B owns the only open P; synchronization uses bounded events
WHEN B reads Nay count, then A commits a change to Aye before B reads Aye count
THEN POL-06 must choose one coherent acceptance/snapshot boundary for close totals
  AND a single actor must not contribute both Aye and Nay to one closed result
  AND final counts/reset and response must follow that chosen boundary
  AND P's creator/name/start and A's choice PK/user remain unchanged
  AND all worker errors propagate and all connections close in finally
```

<a id="pp-25a"></a>

### PP-25a — test_two_closers_before_reset_preserve_first_finalized_result

Parent: `PP-25` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-06: close winner/loser; POL-04: noncreator permission; DEF-03; PostgreSQL
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:24–41`

```text
GIVEN PostgreSQL independent clients/connections; A and B have EXEC plus ACTIVE
  AND A owns the only open P and has Aye
WHEN both closers select P and read counts before either resets, using bounded barriers
  AND the two saves occur at distinct controlled times
THEN POL-06 must define winner/loser response and immutable finalization semantics
  AND later stale close cannot rewrite finalized counts/end
  AND P's PK/name/creator/start and choice PK/user remain unchanged
  AND workers join within timeout and close connections in finally
```

<a id="pp-25b"></a>

### PP-25b — test_late_closer_cannot_overwrite_counts_after_first_reset

Parent: `PP-25` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-06; POL-04: noncreator close; DEF-03; PostgreSQL
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:24–41`

```text
GIVEN PostgreSQL independent connections; A/B have EXEC plus ACTIVE
  AND A owns open P; ACTIVE C has Aye
WHEN both closers select P, A closes 1/0 and resets, then B counts zero and saves
  AND real query/write boundaries use bounded events, not mocked business behavior
THEN POL-06 must define a loser response without overwriting finalized 1/0 or end
  AND C's choice stays No Vote with original PK/user
  AND P's creator/name/start and unrelated history stay unchanged
  AND workers propagate exceptions and close connections in finally
```

<a id="pp-25c"></a>

### PP-25c — test_concurrent_closers_with_multiple_opens_have_explicit_targets

Parent: `PP-25` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-01/POL-06/POL-04; DEF-03; PostgreSQL
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:24–41`

```text
GIVEN PostgreSQL independent connections and bounded worker synchronization
  AND A/B have EXEC plus ACTIVE; A owns open P1 and P2; ACTIVE C has Nay
WHEN A and B concurrently POST /poll/ with {end_vote: "1"}
THEN POL-01 must choose rejection of multiple opens or explicit target identities
  AND POL-06 must define effective transition count and winner/loser responses
  AND no poll receives another poll's consumed/reset totals
  AND creators/names/starts and C's choice ownership stay unchanged
  AND workers join/propagate errors/close connections; SQLite cannot satisfy the design
```
