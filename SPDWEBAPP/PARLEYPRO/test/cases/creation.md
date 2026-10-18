# Creation workflow

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

<a id="pp-01a"></a>

### PP-01a — test_create_form_exposes_name_and_csrf

Parent: `PP-01` | Operation: `PP-V01-FORM` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:35–50`; `SPDWEBAPP/PARLEYPRO/templates/create_poll.html:11–24`

```text
GIVEN make_user(username="a", roles=("EXEC", "ACTIVE")) creates A
  AND no polls exist; before = snapshot_scope([A], relations=("roles",))
WHEN login_actor(client, A); GET /poll/start_vote/
THEN response is 200 and uses create_poll.html
  AND the unbound form exposes only Vote_Poll_Name
  AND label is Poll Name and the text input has class form-control
  AND a CSRF hidden field is rendered
  AND assert_unchanged(before); poll and choice row counts remain zero
```

<a id="pp-01b"></a>

### PP-01b — test_invalid_name_redisplay_escapes_html

Parent: `PP-01` | Operation: `PP-V01-CREATE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/forms.py:5–14`; `SPDWEBAPP/PARLEYPRO/templates/create_poll.html:14–19`

```text
GIVEN A has only EXEC and ACTIVE; B owns closed H
  AND before = snapshot_scope([A, B, H])
WHEN A POSTs /poll/start_vote/ with Vote_Poll_Name="<script>" repeated 30 times
THEN response is 200 with a bound max_length error
  AND redisplayed input escapes <script> rather than executing markup
  AND no poll is created
  AND assert_unchanged(before)
  AND no current choice or admin audit row is created
```

<a id="pp-02a"></a>

### PP-02a — test_create_saves_name_and_open_defaults

Parent: `PP-02` | Operation: `PP-V01-CREATE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:38–45`; `SPDWEBAPP/PARLEYPRO/models.py:12–18`

```text
GIVEN A has only EXEC and ACTIVE; B owns closed H and a Nay choice
  AND no poll is open; before = snapshot_scope([A, B, H, B_choice])
WHEN under at_time(2026-01-15T18:00:00Z), A POSTs /poll/start_vote/
  AND payload is {Vote_Poll_Name: "  Motion A  "}
THEN response is 302 with Location reverse("poll")
  AND exactly one new poll has name Motion A and creator A
  AND its counts are 0/0, end is NULL and start is 2026-01-15T18:00:00Z
  AND assert_unchanged(before); no current choice is created or reset
```

<a id="pp-02b"></a>

### PP-02b — test_create_ignores_forged_model_fields

Parent: `PP-02` | Operation: `PP-V01-CREATE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/forms.py:8`; `SPDWEBAPP/PARLEYPRO/views.py:41–44`

```text
GIVEN A has only EXEC and ACTIVE; B owns closed H with counts 4/2
  AND B has a Nay choice; before = snapshot_scope([A, B, H, B_choice])
WHEN A POSTs /poll/start_vote/ with Vote_Poll_Name="Motion B"
  AND created_by=B.id, id=H.id, Vote_Poll_Count_Yes=99, Vote_Poll_Count_No=88
  AND Vote_Poll_Start="2000-01-01", Vote_Poll_End="2000-01-02"
THEN response is 302 to reverse("poll")
  AND a different new poll belongs to A with counts 0/0 and end NULL
  AND its start is the controlled model clock, not the submitted date
  AND assert_unchanged(before)
```

<a id="pp-03a"></a>

### PP-03a — test_create_rejects_blank_name

Parent: `PP-03` | Operation: `PP-V01-CREATE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/forms.py:5–14`; `SPDWEBAPP/PARLEYPRO/models.py:13`

```text
GIVEN A has only EXEC and ACTIVE; B owns closed H and a Nay choice
  AND before = snapshot_scope([A, B, H, B_choice])
WHEN A POSTs /poll/start_vote/ separately with {}, {Vote_Poll_Name: ""}
  AND {Vote_Poll_Name: "   "}
THEN each response is 200 with a bound required error for Vote_Poll_Name
  AND the form does not create an open poll
  AND assert_unchanged(before)
  AND total poll and current-choice row counts are unchanged
```

<a id="pp-03b"></a>

### PP-03b — test_create_rejects_name_over_max_length

Parent: `PP-03` | Operation: `PP-V01-CREATE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/forms.py:5–14`; `SPDWEBAPP/PARLEYPRO/models.py:13`

```text
GIVEN A has only EXEC and ACTIVE; closed H exists; no poll is open
  AND before = snapshot_scope([A, H])
WHEN A POSTs /poll/start_vote/ with Vote_Poll_Name="x" repeated 201 times
THEN response is 200 and form.errors has the max_length code
  AND the submitted value is redisplayed
  AND no new poll is inserted
  AND assert_unchanged(before)
  AND no current-choice row is created
```

<a id="pp-03c"></a>

### PP-03c — test_create_accepts_name_length_boundaries_and_unicode

Parent: `PP-03` | Operation: `PP-V01-CREATE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/forms.py:5–14`; `SPDWEBAPP/PARLEYPRO/views.py:38–45`

```text
GIVEN A has only EXEC and ACTIVE; no poll is open in each isolated variant
  AND names are "x", "x" repeated 200 times, and "Réunion Δ"
WHEN A POSTs /poll/start_vote/ separately with each Vote_Poll_Name
THEN each response is 302 to reverse("poll")
  AND exactly one new poll stores that exact name and creator A
  AND counts are 0/0 and end is NULL
  AND A's attributes and roles are unchanged
  AND no choice row is created
```

<a id="pp-03d"></a>

### PP-03d — test_created_markup_name_is_escaped_on_page

Parent: `PP-03` | Operation: `PP-V04-PAGE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:22–27`; `SPDWEBAPP/PARLEYPRO/forms.py:8`

```text
GIVEN A has only EXEC and ACTIVE; no polls or choices exist
  AND name is "<b>Motion</b>"
WHEN A POSTs /poll/start_vote/ with {Vote_Poll_Name: name}, then GETs /poll/
THEN POST redirects to reverse("poll"); GET is 200
  AND the new poll stores the literal name, not sanitized text
  AND the rendered heading contains escaped markup, not a b element
  AND saved poll counts/end remain 0/0 and NULL after GET
  AND A's attributes and roles are unchanged
```

<a id="pp-06a"></a>

### PP-06a — test_create_while_another_poll_is_open

Parent: `PP-06` | Operation: `PP-V01-CREATE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-01: single-open invariant and target identity
Source: `SPDWEBAPP/PARLEYPRO/views.py:38–45`

```text
GIVEN A has only EXEC and ACTIVE; A owns open P; B has an Aye choice
  AND before = snapshot_scope([A, B, P, B_choice])
WHEN A POSTs /poll/start_vote/ with {Vote_Poll_Name: "Second motion"}
THEN POL-01 must choose rejection of a second open poll or explicit coexistence
  AND rejection must preserve P, B_choice and the poll row count
  AND coexistence must identify which poll future casts and closes target
  AND neither outcome may silently reset B_choice or rewrite P
  AND the response status/redirect follows the selected POL-01 outcome
```

<a id="pp-06b"></a>

### PP-06b — test_replayed_create_has_explicit_retry_semantics

Parent: `PP-06` | Operation: `PP-V01-CREATE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-01 and POL-02: repeat-create identity
Source: `SPDWEBAPP/PARLEYPRO/views.py:38–45`

```text
GIVEN A has only EXEC and ACTIVE; no poll is open; B has a Nay choice
  AND before = snapshot_scope([A, B, B_choice])
WHEN A submits {Vote_Poll_Name: "Retry motion"} twice to /poll/start_vote/
THEN POL-01/POL-02 must choose deduplication, rejection, or distinct polls
  AND response and resulting poll count follow that named retry rule
  AND no outcome changes creator/name/start/counts of the first saved poll
  AND assert_unchanged(before); choices must not reset as a retry side effect
  AND no idempotency guarantee is inferred from the current redirect
```

<a id="pp-39a"></a>

### PP-39a — test_create_storage_failure_preserves_existing_state

Parent: `PP-39` | Operation: `PP-V01-CREATE` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: POL-06: failure transport and retry contract
Source: `SPDWEBAPP/PARLEYPRO/views.py:41–45`

```text
GIVEN A has only EXEC and ACTIVE; B owns closed H and a Nay choice
  AND TransactionTestCase/autocommit; before = snapshot_scope([A, B, H, B_choice])
WHEN A POSTs {Vote_Poll_Name: "Failed motion"} to /poll/start_vote/
  AND an injected new-poll save failure occurs before its real database write
THEN no new poll or choice row exists; assert_unchanged(before)
  AND POL-06 must choose handled error response or documented failure transport
  AND no assertion treats the current unhandled exception as acceptable
  AND retry expectations remain separate from storage rollback assertions
```

<a id="pp-39b"></a>

### PP-39b — test_auto_add_uses_model_clock_after_view_clock

Parent: `PP-39` | Operation: `PP-V01-CREATE` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:43–44`; `SPDWEBAPP/PARLEYPRO/models.py:14`

```text
GIVEN A has only EXEC and ACTIVE; no polls or choices exist
  AND local patches of consumed clocks return T=2026-01-15T18:00:00Z to the view
  AND the actual model auto_now_add clock returns T+1 second
WHEN A POSTs /poll/start_vote/ with {Vote_Poll_Name: "Two clocks"}
THEN response is 302 to reverse("poll")
  AND the new poll start equals T+1 second, not the discarded T assignment
  AND creator A, counts 0/0 and end NULL are persisted
  AND A's roles and attributes remain unchanged
```
