# Voting and action dispatch

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

<a id="pp-07a"></a>

### PP-07a — test_cast_aye_creates_own_current_choice

Parent: `PP-07` | Operation: `PP-V02-CAST` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE and no choice; A owns open P
  AND B has only ACTIVE with Nay; before = snapshot_scope([A, B, P, B_choice])
WHEN A POSTs /poll/ with {aye: value}
  AND isolated value variants are "1", "", and "false"
THEN response is 200 using poll_index.html
  AND exactly one new choice belongs to A with value Aye
  AND assert_unchanged(before)
  AND P's saved counts/end do not change; no historical ballot row exists
```

<a id="pp-07b"></a>

### PP-07b — test_cast_nay_creates_own_current_choice

Parent: `PP-07` | Operation: `PP-V02-CAST` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE and no choice; A owns open P
  AND B has only ACTIVE with Nay; before = snapshot_scope([A, B, P, B_choice])
WHEN A POSTs /poll/ with {nay: value}
  AND isolated value variants are "1", "", and "false"
THEN response is 200 using poll_index.html
  AND exactly one new choice belongs to A with value Nay
  AND assert_unchanged(before)
  AND P's saved counts/end do not change; no historical ballot row exists
```

<a id="pp-07c"></a>

### PP-07c — test_change_choice_keeps_user_row_identity

Parent: `PP-07` | Operation: `PP-V02-CAST` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE; A owns open P; B has Nay
  AND isolated variants start A_choice=Aye then submit nay, or Nay then submit aye
  AND before = snapshot_scope([A, B, P, A_choice, B_choice])
WHEN A POSTs /poll/ with the named opposite-choice key and value "1"
THEN response is 200; A_choice has the opposite value with identical PK/user
  AND no second choice row is inserted
  AND B_choice, P, A and B are unchanged
  AND only A_choice.user_vote_choice differs from its snapshot
```

<a id="pp-07d"></a>

### PP-07d — test_repeat_identical_choice_is_idempotent_for_current_row

Parent: `PP-07` | Operation: `PP-V02-CAST` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE and owns open P; B has Nay
  AND isolated variants have A_choice=Aye with aye, or A_choice=Nay with nay
  AND before = snapshot_scope([A, B, P, A_choice, B_choice])
WHEN A POSTs /poll/ twice with the existing-choice key and value "1"
THEN each response is 200
  AND A_choice keeps its PK, user and existing value
  AND total choice row count is unchanged
  AND assert_unchanged(before); poll aggregates/end are not saved
```

<a id="pp-08a"></a>

### PP-08a — test_forged_target_fields_cannot_create_another_users_choice

Parent: `PP-08` | Operation: `PP-V02-CAST` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE and no choice; A owns open P
  AND B owns closed H and has Aye; before = snapshot_scope([A, B, P, H, B_choice])
WHEN A POSTs /poll/ with {nay: "1", user: B.id, user_id: B.id}
  AND payload also contains poll: H.id and user_vote_choice: "Aye"
THEN response is 200; exactly one A choice is Nay
  AND the inserted row belongs to A, never B
  AND assert_unchanged(before)
  AND B_choice, all poll fields and all profile/role relations are unchanged
```

<a id="pp-08b"></a>

### PP-08b — test_forged_target_fields_cannot_redirect_existing_choice

Parent: `PP-08` | Operation: `PP-V02-CAST` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE and an existing Aye choice; A owns open P
  AND B owns closed H and has Aye; before = snapshot_scope([A, B, P, H, B_choice])
WHEN A POSTs /poll/ with {nay: "1", user: B.id, user_id: B.id}
  AND payload also contains poll: H.id and user_vote_choice: "Aye"
THEN response is 200; exactly one A choice is Nay
  AND A's original choice PK and user are preserved
  AND assert_unchanged(before)
  AND B_choice, all poll fields and all profile/role relations are unchanged
```

<a id="pp-09a"></a>

### PP-09a — test_dual_choice_keys_have_explicit_dispatch_policy

Parent: `PP-09` | Operation: `PP-V02-DISPATCH` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-02: dual-choice rejection or precedence
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:66–71`

```text
GIVEN A has only ACTIVE with no choice; A owns open P; B has Nay
  AND before = snapshot_scope([A, B, P, B_choice])
WHEN A POSTs {aye: "1", nay: "1"} and separately reverses key insertion order
THEN POL-02 must choose reject-without-write or one deterministic accepted choice
  AND response and A's resulting row/value follow that chosen rule
  AND the outcome must not depend on client key insertion order
  AND P and B_choice must remain unchanged
  AND current Nay-then-Aye implementation is evidence, not settled policy
```

<a id="pp-10a"></a>

### PP-10a — test_unknown_payload_with_absent_choice_has_explicit_policy

Parent: `PP-10` | Operation: `PP-V02-DISPATCH` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-02: missing/unknown action and default-row side effect
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE and no choice; A owns open P; B has Nay
  AND before = snapshot_scope([A, B, P, B_choice])
WHEN A separately POSTs {}, {unknown: "1"}, or {user_vote_choice: "Aye"} to /poll/
THEN POL-02 must choose rejection, side-effect-free no-op, or default No Vote creation
  AND response follows that choice; no path may infer an Aye action
  AND whether a No Vote row is allowed must be decided explicitly
  AND P and B_choice remain unchanged
  AND no payload-supplied user or poll target is honored
```

<a id="pp-10b"></a>

### PP-10b — test_unknown_payload_with_existing_choice_has_explicit_policy

Parent: `PP-10` | Operation: `PP-V02-DISPATCH` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-02: missing/unknown action and default-row side effect
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE and an existing Nay choice; A owns open P; B has Nay
  AND before = snapshot_scope([A, B, P, B_choice, A_choice])
WHEN A separately POSTs {}, {unknown: "1"}, or {user_vote_choice: "Aye"} to /poll/
THEN POL-02 must choose validation rejection or a side-effect-free no-op
  AND response follows that choice; neither path may infer an Aye action
  AND A_choice must retain its PK/user and Nay value
  AND P and B_choice remain unchanged
  AND no payload-supplied user or poll target is honored
```

<a id="pp-11a"></a>

### PP-11a — test_hidden_start_key_has_explicit_navigation_policy

Parent: `PP-11` | Operation: `PP-V02-DISPATCH` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-02; DEF-02: discarded redirect
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:52–53`; `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:9–10`

```text
GIVEN A has only ACTIVE and no choice; A owns open P; B has Nay
  AND before = snapshot_scope([A, B, P, B_choice])
WHEN A POSTs /poll/ with {start_vote: "1"}
THEN POL-02 must choose rejection/removal or an authorized create-page navigation
  AND navigation must still enforce EXEC plus ACTIVE on /poll/start_vote/
  AND no new poll, choice, close or reset is allowed from this key alone
  AND assert_unchanged(before)
  AND DEF-02's discarded redirect is not retained as a required 200 response
```

<a id="pp-11b"></a>

### PP-11b — test_start_key_mixed_with_actions_has_explicit_precedence

Parent: `PP-11` | Operation: `PP-V02-DISPATCH` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-02: mixed-action rule; DEF-02
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:52–71`

```text
GIVEN A has only EXEC and ACTIVE, owns open P and has Aye; B has Nay
  AND before = snapshot_scope([A, B, P, A_choice, B_choice])
WHEN A POSTs {start_vote: "1", end_vote: "1", aye: "1", nay: "1"} to /poll/
THEN POL-02 must choose reject-without-write or exactly one named action
  AND the response and changed fields must match that selected action
  AND no submission may perform a cast and a close together
  AND unrelated polls, creator/start metadata and user roles remain unchanged
  AND current start-first branch does not decide the future transport contract
```

<a id="pp-12a"></a>

### PP-12a — test_end_plus_choice_keys_with_existing_actor_choice

Parent: `PP-12` | Operation: `PP-V02-DISPATCH` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-02: end mixed with choice keys
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:55–71`

```text
GIVEN A has only EXEC and ACTIVE, owns open P, and has a Nay choice
  AND B has Aye; before = snapshot_scope([A, B, P, B_choice, A_choice])
WHEN A POSTs {end_vote: "1", aye: "1", nay: "1"} to /poll/
THEN POL-02 must choose reject-without-write or a close-only action
  AND rejection preserves all named rows and row counts
  AND close-only counts preexisting choices, not the supplied aye/nay keys
  AND close-only must not insert an absent actor choice or cast before counting
  AND response and reset/end fields follow the chosen close-only or reject rule
```

<a id="pp-12b"></a>

### PP-12b — test_end_plus_choice_keys_with_absent_actor_choice

Parent: `PP-12` | Operation: `PP-V02-DISPATCH` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-02: end mixed with choice keys
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:55–71`

```text
GIVEN A has only EXEC and ACTIVE, owns open P, and has no choice
  AND B has Aye; before = snapshot_scope([A, B, P, B_choice])
WHEN A POSTs {end_vote: "1", aye: "1", nay: "1"} to /poll/
THEN POL-02 must choose reject-without-write or a close-only action
  AND rejection preserves all named rows and row counts
  AND close-only counts preexisting choices, not the supplied aye/nay keys
  AND close-only must not insert an absent actor choice or cast before counting
  AND response and reset/end fields follow the chosen close-only or reject rule
```

<a id="pp-13a"></a>

### PP-13a — test_cast_without_open_poll_has_explicit_transition_policy

Parent: `PP-13` | Operation: `PP-V02-CAST` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-01: cast acceptance with no open poll
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`; `SPDWEBAPP/PARLEYPRO/views.py:22–34`

```text
GIVEN A has only ACTIVE and no choice; B has Nay
  AND isolated variants have no polls or only closed H
  AND before = snapshot_scope([A, B, B_choice], relations=("roles",))
WHEN A POSTs /poll/ with {aye: "1"}
THEN POL-01 must choose rejection with no A row or documented global staging
  AND response and A-row presence follow that selected rule
  AND closed H, B_choice and user roles are unchanged in either outcome
  AND the missing UI button is not evidence of server-side rejection
```

<a id="pp-14a"></a>

### PP-14a — test_multiple_open_poll_cast_has_explicit_target_identity

Parent: `PP-14` | Operation: `PP-V02-CAST` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-01: open-poll cardinality and targeting
Source: `SPDWEBAPP/PARLEYPRO/views.py:22`; `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE; A owns open P1 at T-2 and P2 at T-1
  AND B has Nay; before = snapshot_scope([A, B, P1, P2, B_choice])
WHEN A GETs /poll/ then POSTs {nay: "1"}
THEN POL-01 must choose invalid multi-open rejection or a named target rule
  AND page selection, response and A's global choice follow that rule
  AND P1/P2 aggregates, end times and metadata must not change from casting
  AND B_choice is unchanged
  AND no fictitious per-poll ballot association may be asserted
```

<a id="pp-14b"></a>

### PP-14b — test_equal_start_open_poll_selection_is_deterministic_by_policy

Parent: `PP-14` | Operation: `PP-V04-PAGE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-01 and POL-07: equal-start selection
Source: `SPDWEBAPP/PARLEYPRO/views.py:22`

```text
GIVEN A has only ACTIVE; A owns open P1 and P2 with identical aware start T
  AND before = snapshot_scope([A, P1, P2])
WHEN A GETs /poll/
THEN POL-01/POL-07 must choose reject-multi-open or an explicit tie-break rule
  AND response/current_poll identity follows that rule
  AND no test assumes a PK from incidental database row order
  AND assert_unchanged(before)
  AND no choice row or audit record is inserted
```

<a id="pp-15a"></a>

### PP-15a — test_count_helper_excludes_nonchoice_literals

Parent: `PP-15` | Operation: `PP-V02-COUNT` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:11–14`

```text
GIVEN ACTIVE A/B/C/D/E have choices Aye, Nay, No Vote, NULL and "invalid"
  AND NULL/invalid values use explicit raw ORM setup rather than fixture validation
  AND before = snapshot_scope([A, B, C, D, E, A_choice, B_choice,
    C_choice, D_choice, E_choice])
WHEN count_all_current_votes(Brother_votes.objects) runs with real ORM queries
THEN its result is the tuple (1, 1) in Aye/Nay order
  AND No Vote, NULL and invalid strings contribute zero
  AND assert_unchanged(before)
  AND no poll, session, file or audit state is changed
```

<a id="pp-15b"></a>

### PP-15b — test_count_helper_respects_supplied_queryset

Parent: `PP-15` | Operation: `PP-V02-COUNT` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:11–14`

```text
GIVEN ACTIVE users A and B each have Aye; ACTIVE C has Nay
  AND before = snapshot_scope([A, B, C, A_choice, B_choice, C_choice])
WHEN count_all_current_votes receives queryset filtered to users A and C
THEN its result is (1, 1), excluding B's Aye
  AND calling with the full manager yields (2, 1)
  AND the supplied querysets still select their original rows
  AND assert_unchanged(before)
  AND no poll/session/file/audit writes occur
```

<a id="pp-15c"></a>

### PP-15c — test_global_count_eligibility_has_explicit_role_and_orphan_policy

Parent: `PP-15` | Operation: `PP-V02-COUNT` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-03: eligibility and nullable-user rows
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:11–14`; `SPDWEBAPP/PARLEYPRO/models.py:21–24`

```text
GIVEN ACTIVE A has Aye; ALUMNI B has Nay; EXEC-only C has Aye
  AND raw ORM setup adds a user=NULL choice with Aye
  AND before = snapshot_scope([A, B, C, A_choice, B_choice, C_choice, orphan_choice])
WHEN global counts feed live results or close aggregates
THEN POL-03 must choose all stored rows or explicit eligible-user filtering
  AND each role and orphan-row contribution follows that choice
  AND no historical per-poll ballot list may be inferred from these rows
  AND assert_unchanged(before) for the count/read phase
```
