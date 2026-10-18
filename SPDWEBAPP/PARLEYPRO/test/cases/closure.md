# Close, count and reset workflow

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

<a id="pp-16a"></a>

### PP-16a — test_close_saves_exact_totals_and_end_without_rewriting_metadata

Parent: `PP-16` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:30–38`

```text
GIVEN A has only EXEC and ACTIVE and owns open P
  AND ACTIVE A/B/C choices are Aye, Aye, Nay; B owns closed H with counts 7/3
  AND before = snapshot_scope([A, B, C, P, H, A_choice, B_choice, C_choice])
WHEN under at_time(T), A POSTs /poll/ with {end_vote: "1"}
  AND A then GETs /poll/past_polls/
THEN both responses are 200; refreshed P has counts 2/1 and end T
  AND history renders stored counts 2 Aye and 1 Nay for P
  AND P's PK, creator, name and start match the snapshot
  AND no extra poll or choice row is inserted; reset identity is specified in PP-16d
  AND H, users and role/profile relations are unchanged
```

<a id="pp-16b"></a>

### PP-16b — test_close_reset_scope_for_nonvoters_and_corrupt_rows

Parent: `PP-16` | Operation: `PP-V03-CLOSE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-03: count/reset eligibility
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:40–41`; `SPDWEBAPP/PARLEYPRO/models.py:21–24`

```text
GIVEN A has only EXEC and ACTIVE and owns open P
  AND ACTIVE A has Aye; ACTIVE B has No Vote
  AND raw ORM rows include NULL/invalid choice and nullable-user Aye
WHEN A POSTs /poll/ with {end_vote: "1"} under at_time(T)
THEN POL-03 must define count and reset eligibility for each exceptional row
  AND reset rows keep their PK/user associations rather than being deleted
  AND P's creator/name/start and unrelated closed-history rows are unchanged
  AND response/count/reset assertions follow the chosen scope, not invented ballots
```

<a id="pp-16c"></a>

### PP-16c — test_cross_creator_close_has_explicit_ownership_policy

Parent: `PP-16` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-04: close ownership boundary
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:23–38`

```text
GIVEN A has only EXEC and ACTIVE; ACTIVE B owns open P
  AND A has Aye and B has Nay; before = snapshot_scope([A, B, P, A_choice, B_choice])
WHEN A POSTs /poll/ with {end_vote: "1"}
THEN POL-04 must choose chapter-wide EXEC+ACTIVE close or creator-only close
  AND denial must preserve every named row
  AND permitted close stores 1/1 and end T, then resets choices without new rows
  AND response and permission assertion follow the selected rule
  AND P's creator, name and start must never be reassigned
```

<a id="pp-16d"></a>

### PP-16d — test_close_resets_current_rows_without_deleting_identity

Parent: `PP-16` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:40–41`

```text
GIVEN A has only EXEC and ACTIVE and owns open P
  AND ACTIVE A/B/C choices are Aye, Nay and No Vote with known row PKs
  AND closed H exists; before = snapshot_scope([A, B, C, P, H, A_choice, B_choice, C_choice])
WHEN A POSTs /poll/ with {end_vote: "1"} under at_time(T)
  AND A then GETs /poll/poll-results/
THEN POST/GET are 200; JSON is exactly {"aye_votes": 0, "nay_votes": 0}
  AND the same three choice rows all contain No Vote
  AND no choice row is inserted/deleted; PKs and user links are unchanged
  AND H and every actor/profile/role relation are unchanged
  AND P is closed with counts 1/1; reset creates no historical individual ballots
```

<a id="pp-18a"></a>

### PP-18a — test_close_without_open_poll_is_noop

Parent: `PP-18` | Operation: `PP-V03-CLOSE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:24–41`

```text
GIVEN A has only EXEC and ACTIVE; no poll is open
  AND A has Aye; B owns closed H with counts 3/2; B has Nay
  AND before = snapshot_scope([A, B, H, A_choice, B_choice])
WHEN A POSTs /poll/ with {end_vote: "1"}
THEN response is 200 with no-active-poll text
  AND no poll or choice row is inserted
  AND A_choice stays Aye and B_choice stays Nay
  AND assert_unchanged(before); H's end/counts are not overwritten
```

<a id="pp-18b"></a>

### PP-18b — test_repeat_close_does_not_rewrite_single_closed_poll

Parent: `PP-18` | Operation: `PP-V03-CLOSE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:24–41`

```text
GIVEN A has only EXEC and ACTIVE and owns the only open P; A has Aye
  AND A closes P under at_time(T), producing counts 1/0 and No Vote choice
  AND before = snapshot_scope([A, P, A_choice])
WHEN A POSTs {end_vote: "1"} again under at_time(T+1 second)
THEN response is 200 with no-active-poll text
  AND P's saved counts remain 1/0 and its end remains T
  AND assert_unchanged(before)
  AND no replacement poll, choice or audit row is created
```

<a id="pp-19a"></a>

### PP-19a — test_repeated_close_cannot_silently_advance_to_other_open_poll

Parent: `PP-19` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-01: target identity under repeated close
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:24–41`

```text
GIVEN A has only EXEC and ACTIVE and owns P1 at T-2 and P2 at T-1
  AND A has Aye; ACTIVE B has Nay; closed H is unrelated
WHEN A POSTs {end_vote: "1"} twice to /poll/
THEN POL-01 must choose rejected multi-open state or explicit target-specific closes
  AND the second request must not silently misattribute zero totals to another poll
  AND response, target PKs and saved counts follow the selected identity rule
  AND H and creator/name/start metadata remain unchanged
  AND reset/retry behavior must not be inferred from current newest-open selection
```

<a id="pp-20a"></a>

### PP-20a — test_close_tie_stores_equal_counts

Parent: `PP-20` | Operation: `PP-V03-CLOSE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:30–41`; `SPDWEBAPP/PARLEYPRO/templates/past_polls.html:25–37`

```text
GIVEN A has only EXEC and ACTIVE and owns open P; A has Aye
  AND ACTIVE B has Nay; before = snapshot_scope([A, B, P, A_choice, B_choice])
WHEN under at_time(T), A POSTs {end_vote: "1"} then GETs /poll/past_polls/
THEN POST is 200; history GET is 200 and shows 1 Aye and 1 Nay for P
  AND P stores counts 1/1 and end T
  AND both choice rows become No Vote with identical PKs/users
  AND P's name/creator/start and users/profile roles remain unchanged
  AND no majority/quorum rule is inferred; POL-05 remains separate
```

<a id="pp-20b"></a>

### PP-20b — test_close_zero_votes_stores_zero_and_renders_no_votes

Parent: `PP-20` | Operation: `PP-V03-CLOSE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:30–41`; `SPDWEBAPP/PARLEYPRO/templates/past_polls.html:39–40`

```text
GIVEN A has only EXEC and ACTIVE and owns open P
  AND isolated variants have no choices or ACTIVE users with only No Vote
  AND before = snapshot_scope([A, P, existing_No_Vote_rows])
WHEN under at_time(T), A POSTs {end_vote: "1"} then GETs /poll/past_polls/
THEN POST and GET are 200; history says No votes recorded for P
  AND P has counts 0/0 and end T
  AND no choice row is created/deleted and existing No Vote values stay unchanged
  AND P's name/creator/start and A's profile/roles remain unchanged
```

<a id="pp-20c"></a>

### PP-20c — test_tie_business_outcome_is_separate_from_admin_label

Parent: `PP-20` | Operation: `PP-C03-ICON` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-05: tie, zero and quorum business semantics
Source: `SPDWEBAPP/PARLEYPRO/admin.py:20–33`

```text
GIVEN A has only ACTIVE; closed P has counts 1/1
  AND closed Z has counts 0/0; before = snapshot_scope([A, P, Z])
WHEN a business consumer asks whether either motion passed
THEN POL-05 must choose tie/zero outcome and any quorum or majority threshold
  AND the admin's existing Tied display is not a business adjudication rule
  AND expected business output follows that selected rule
  AND assert_unchanged(before)
  AND no historical individual ballots may be reconstructed
```

<a id="pp-37a"></a>

### PP-37a — test_close_response_does_not_present_closed_poll_as_current

Parent: `PP-37` | Operation: `PP-V04-PAGE` | Priority: P1
Status: `NEEDS_FIX` | Blockers: DEF-06: stale pre-dispatch context
Source: `SPDWEBAPP/PARLEYPRO/views.py:22–34`; `SPDWEBAPP/PARLEYPRO/pp_functions.py:30–41`

```text
GIVEN A has only EXEC and ACTIVE and owns the only open P; A has Aye
  AND before = snapshot_scope([A, P, A_choice])
WHEN A POSTs /poll/ with {end_vote: "1"} under at_time(T)
THEN response must recompute current state or redirect to a fresh current page
  AND its final rendered page must not offer voting controls for closed P
  AND fresh GET /poll/ excludes P and history GET includes P
  AND P stores 1/0 and end T; A_choice is No Vote with identical PK/user
  AND creator/name/start and actor roles are unchanged
```
