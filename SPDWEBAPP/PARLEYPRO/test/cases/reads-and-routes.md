# Current, history, live and route reads

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

<a id="pp-26a"></a>

### PP-26a — test_current_page_shows_open_poll_and_live_counts

Parent: `PP-26` | Operation: `PP-V04-PAGE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:15–34`; `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:22–64`

```text
GIVEN A has only ACTIVE; A owns open P with saved aggregate counts 0/0
  AND ACTIVE B has Aye; A has Nay; B owns closed H
  AND before = snapshot_scope([A, B, P, H, A_choice, B_choice])
WHEN A GETs /poll/
THEN response is 200 using poll_index.html with current_poll=P
  AND context aye_votes=1 and nay_votes=1 and both numeric bars are rendered
  AND P's displayed start is converted to America/Chicago
  AND assert_unchanged(before); GET does not update P's stored aggregates
```

<a id="pp-26b"></a>

### PP-26b — test_no_open_poll_page_remains_read_only_with_residual_choices

Parent: `PP-26` | Operation: `PP-V04-PAGE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:22–34`; `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:70–76`

```text
GIVEN A has only ACTIVE; B owns closed H; no poll is open
  AND A has Aye and ACTIVE B has Nay
  AND before = snapshot_scope([A, B, H, A_choice, B_choice])
WHEN A GETs /poll/
THEN response is 200 with current_poll=None and No active poll at the moment
  AND context still has aye_votes=1 and nay_votes=1
  AND vote buttons for an active poll are absent
  AND assert_unchanged(before); no residual choices are deleted
```

<a id="pp-26c"></a>

### PP-26c — test_active_actor_reads_another_creators_current_poll

Parent: `PP-26` | Operation: `PP-V04-PAGE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:22–34`

```text
GIVEN A has only ACTIVE and no choice; ACTIVE B owns the only open P
  AND P's name is "Chapter motion"; before = snapshot_scope([A, B, P])
WHEN A GETs /poll/
THEN response is 200 with current_poll=P
  AND the rendered heading contains Chapter motion
  AND no creator-only filtering hides P
  AND assert_unchanged(before)
  AND no A choice is created by reading the page
```

<a id="pp-27a"></a>

### PP-27a — test_history_contains_closed_polls_in_descending_end_order

Parent: `PP-27` | Operation: `PP-V04-HISTORY` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:51–58`; `SPDWEBAPP/PARLEYPRO/templates/past_polls.html:14–48`

```text
GIVEN A has only ACTIVE; A owns open P and closed H1 ending at T-2
  AND ACTIVE B owns closed H2 ending at T-1; A has a current Aye choice
  AND before = snapshot_scope([A, B, P, H1, H2, A_choice])
WHEN A GETs /poll/past_polls/
THEN response is 200 using past_polls.html with ordered PKs [H2.id, H1.id]
  AND P is excluded and each history row shows its stored name and creator
  AND counts come from H1/H2 aggregates, not A_choice
  AND assert_unchanged(before); no historical individual ballots are exposed
```

<a id="pp-27b"></a>

### PP-27b — test_empty_history_renders_no_polls_message

Parent: `PP-27` | Operation: `PP-V04-HISTORY` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:54–58`; `SPDWEBAPP/PARLEYPRO/templates/past_polls.html:52–55`

```text
GIVEN A has only ACTIVE and owns open P; no poll is closed
  AND A has Nay; before = snapshot_scope([A, P, A_choice])
WHEN A GETs /poll/past_polls/
THEN response is 200 with an empty past_polls queryset
  AND No past polls available is rendered
  AND P's name does not appear as a history result
  AND assert_unchanged(before)
  AND no poll/choice/audit row is inserted
```

<a id="pp-27c"></a>

### PP-27c — test_history_formats_chicago_dst_without_changing_sort_order

Parent: `PP-27` | Operation: `PP-V04-HISTORY` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/templates/past_polls.html:19,46`; `SPDWEBAPP/PARLEYPRO/views.py:56`

```text
GIVEN A has only ACTIVE; A owns closed H1 ending 2026-11-01T06:30:00Z
  AND H2 ends 2026-11-01T07:30:00Z; both starts are earlier aware times
  AND before = snapshot_scope([A, H1, H2])
WHEN A GETs /poll/past_polls/
THEN response is 200 and ordered PKs are [H2.id, H1.id]
  AND both end displays contain Nov 1, 2026 and 1:30 AM in America/Chicago
  AND the repeated wall-clock hour does not reverse the UTC-based ordering
  AND assert_unchanged(before); persisted aware datetimes remain exact
```

<a id="pp-27d"></a>

### PP-27d — test_history_equal_end_times_have_explicit_tiebreak_policy

Parent: `PP-27` | Operation: `PP-V04-HISTORY` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-07: equal-end ordering
Source: `SPDWEBAPP/PARLEYPRO/views.py:54–56`

```text
GIVEN A has only ACTIVE; closed H1/H2 have the exact same aware end T
  AND before = snapshot_scope([A, H1, H2])
WHEN A GETs /poll/past_polls/
THEN response is 200 and both H1/H2 are present exactly once
  AND POL-07 must choose unspecified equivalent order or explicit PK/name tie-break
  AND no case assumes an order from incidental database iteration
  AND assert_unchanged(before)
  AND the chosen rule must remain stable across database backends
```

<a id="pp-27e"></a>

### PP-27e — test_history_nullable_aggregates_have_explicit_display_policy

Parent: `PP-27` | Operation: `PP-V04-HISTORY` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-09: nullable aggregates; related DEF-04
Source: `SPDWEBAPP/PARLEYPRO/models.py:15–16`; `SPDWEBAPP/PARLEYPRO/templates/past_polls.html:25–40`

```text
GIVEN A has only ACTIVE; closed H has raw ORM aggregate values NULL/1
  AND isolated additional variants are 1/NULL and NULL/NULL
  AND before = snapshot_scope([A, H])
WHEN A GETs /poll/past_polls/
THEN the response must not crash or fabricate historical individual votes
  AND POL-09 must choose unknown display, zero interpretation, or data repair
  AND rendered totals/bars and response contract follow that choice
  AND assert_unchanged(before) unless an explicit separately tested repair runs
```

<a id="pp-28a"></a>

### PP-28a — test_active_live_results_have_exact_integer_json_payload

Parent: `PP-28` | Operation: `PP-V04-LIVE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:61–68`

```text
GIVEN A has only ACTIVE and owns open P
  AND ACTIVE A/B/C choices are Aye, Aye, Nay
  AND before = snapshot_scope([A, B, C, P, A_choice, B_choice, C_choice])
WHEN A GETs /poll/poll-results/
THEN response is 200 with application/json
  AND JSON is exactly {"aye_votes": 2, "nay_votes": 1} with integer values
  AND assert_unchanged(before)
  AND no profile, choice, poll, file or audit state changes
```

<a id="pp-28b"></a>

### PP-28b — test_live_audience_outside_active_has_explicit_policy

Parent: `PP-28` | Operation: `PP-V04-LIVE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-03: live-results audience
Source: `SPDWEBAPP/PARLEYPRO/views.py:61–68`

```text
GIVEN A variants are authenticated no-profile, roles (), ("ALUMNI",), ("EXEC",)
  AND ACTIVE B owns open P and has Aye
  AND before = snapshot_scope([A, B, P, B_choice])
WHEN A GETs /poll/poll-results/
THEN POL-03 must choose login-only visibility or an explicit role-restricted audience
  AND allowed users get integer aggregate JSON; denied users receive no counts
  AND response status/redirect follows that selected visibility rule
  AND assert_unchanged(before); profile absence must not cause an incidental crash
```

<a id="pp-28c"></a>

### PP-28c — test_anonymous_live_results_redirect_without_counts

Parent: `PP-28` | Operation: `PP-V04-LIVE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:61–68`

```text
GIVEN no actor is authenticated; ACTIVE B owns P and has Aye
  AND before = snapshot_scope([B, P, B_choice])
WHEN client GETs /poll/poll-results/
THEN response is 302 to the business login URL with next=/poll/poll-results/
  AND no aggregate JSON is disclosed
  AND authenticated session identity remains absent
  AND assert_unchanged(before)
  AND no poll or choice row is inserted
```

<a id="pp-28d"></a>

### PP-28d — test_live_zero_counts_are_integer_zeros

Parent: `PP-28` | Operation: `PP-V04-LIVE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:63–68`

```text
GIVEN A has only ACTIVE and owns open P
  AND isolated variants have no choices or only No Vote choices
  AND before = snapshot_scope([A, P, existing_No_Vote_rows])
WHEN A GETs /poll/poll-results/
THEN response is 200 with application/json
  AND JSON is exactly {"aye_votes": 0, "nay_votes": 0}
  AND both values are integers, not strings or NULL
  AND assert_unchanged(before)
```

<a id="pp-28e"></a>

### PP-28e — test_live_counts_without_open_poll_have_explicit_scope_policy

Parent: `PP-28` | Operation: `PP-V04-LIVE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-01/POL-03: no-open-poll live scope
Source: `SPDWEBAPP/PARLEYPRO/views.py:63–68`

```text
GIVEN A has only ACTIVE; B owns closed H; no poll is open
  AND A has Aye and ACTIVE B has Nay
  AND before = snapshot_scope([A, B, H, A_choice, B_choice])
WHEN A GETs /poll/poll-results/
THEN POL-01/POL-03 must choose global residual counts or no-current-poll response
  AND response and JSON shape follow that selected scope
  AND closed H cannot acquire reconstructed ballots or rewritten totals
  AND assert_unchanged(before); the read must not reset residual choices
```

<a id="pp-30a"></a>

### PP-30a — test_poll_routes_reverse_and_resolve_to_mounted_views

Parent: `PP-30` | Operation: `PP-V04-ROUTES` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/urls.py:4–13`

```text
GIVEN the business root URLconf mounts PARLEYPRO at /poll/
  AND no authentication or ORM writes are needed for resolver checks
WHEN reverse/resolve run for poll, start_vote, past_polls and poll_results
THEN paths are /poll/, /poll/start_vote/, /poll/past_polls/, /poll/poll-results/
  AND callables are poll_index, start_vote, past_polls and poll_results respectively
  AND inbound live resolution is not a different endpoint because of duplicate entries
  AND no commented logout route is treated as supported
  AND database/session/file/audit state is untouched
```

<a id="pp-30b"></a>

### PP-30b — test_live_route_is_defined_once

Parent: `PP-30` | Operation: `PP-V04-ROUTES` | Priority: P2
Status: `NEEDS_FIX` | Blockers: DEF-08: redundant URL entry
Source: `SPDWEBAPP/PARLEYPRO/urls.py:8–11`

```text
GIVEN PARLEYPRO URL patterns contain duplicate poll-results/ definitions
  AND both currently name poll_results and call the same view
WHEN the route table is inspected after DEF-08 cleanup
THEN exactly one identical path/name/callable definition remains
  AND reverse("poll_results") stays /poll/poll-results/
  AND inbound resolution still reaches poll_results
  AND no alias or new public endpoint is invented
  AND database/session/file/audit state is untouched
```

<a id="pp-30c"></a>

### PP-30c — test_history_and_live_post_have_explicit_method_policy

Parent: `PP-30` | Operation: `PP-V04-ROUTES` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-08: POST read routes; POL-03: live scope
Source: `SPDWEBAPP/PARLEYPRO/views.py:51–68`

```text
GIVEN A has only ACTIVE and owns P; A has Aye; closed H exists
  AND a csrf_client obtains a real cookie/token from GET /poll/
  AND before = snapshot_scope([A, P, H, A_choice])
WHEN A POSTs {} with the token to /poll/past_polls/ and /poll/poll-results/
THEN POL-08 must choose read-only POST acceptance or 405 method rejection
  AND acceptance renders history/JSON, never a cast or close
  AND POL-03 still governs live audience and count eligibility
  AND assert_unchanged(before) in either transport outcome
```

<a id="pp-30d"></a>

### PP-30d — test_other_unsafe_methods_do_not_gain_mutation_semantics

Parent: `PP-30` | Operation: `PP-V04-ROUTES` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-08: allowed methods and future API transport
Source: `SPDWEBAPP/PARLEYPRO/views.py:24,38,51–68`

```text
GIVEN A has only EXEC and ACTIVE, owns open P and has Aye; closed H exists
  AND csrf_client has a real cookie/token; before = snapshot_scope([A, P, H, A_choice])
WHEN A sends PUT, PATCH and DELETE with token headers to page/create/history/live
  AND payload contains aye=1 and end_vote=1
THEN POL-08 must choose 405 rejection or documented read-only legacy fallthrough
  AND none of these methods may create, cast, close, reset or delete
  AND response type follows the chosen route/method contract
  AND assert_unchanged(before); no current-choice row is added
```
