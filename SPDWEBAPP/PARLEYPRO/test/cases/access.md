# Access and CSRF workflow

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

Shared decorator callable tests stay
[AUTHENTICATE-owned](../../../AUTHENTICATE/test/regression-spec.md).
These cases assert route integration, not another shared helper/harness.

<a id="pp-04a"></a>

### PP-04a — test_anonymous_create_requires_login

Parent: `PP-04` | Operation: `PP-V01-CREATE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:35–50`

```text
GIVEN no actor is authenticated; B owns closed H and a Nay choice
  AND before = snapshot_scope([B, H, B_choice])
WHEN client GETs /poll/start_vote/ and separately POSTs {Vote_Poll_Name: "Motion"}
THEN both responses are 302 to the business login URL with next=/poll/start_vote/
  AND no form submission creates a poll
  AND assert_unchanged(before)
  AND no choice is inserted or reset
  AND the authenticated session identity remains absent
```

<a id="pp-04b"></a>

### PP-04b — test_create_denies_missing_profile_or_required_role

Parent: `PP-04` | Operation: `PP-V01-CREATE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:35–36`; `SPDWEBAPP/PARLEYPRO/pp_decorators.py:30–48`

```text
GIVEN A variants have no profile, or roles (), ("EXEC",), ("ACTIVE",)
  AND ("ALUMNI",), ("NEW_MEMBER",), ("PHIL_CHAIR",), ("EXEC", "ALUMNI")
  AND B owns closed H; before = snapshot_scope([A, B, H], relations=("roles",))
WHEN A GETs create and separately POSTs {Vote_Poll_Name: "Motion"}
  AND HTTP_REFERER is /auth/login/
THEN each response is 302 to /auth/login/ with missing-profile/role error message
  AND no poll or choice row is created; assert_unchanged(before)
  AND authenticated session identity remains A
  AND missing EXEC or ACTIVE is not supplied by any unrelated role
```

<a id="pp-04c"></a>

### PP-04c — test_create_allows_exact_pair_and_extra_roles

Parent: `PP-04` | Operation: `PP-V01-CREATE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:35–45`; `SPDWEBAPP/PARLEYPRO/pp_decorators.py:35–36`

```text
GIVEN A variants have roles ("EXEC", "ACTIVE") or ("EXEC", "ACTIVE", "ALUMNI")
  AND no poll is open; B owns closed H; before = snapshot_scope([A, B, H])
WHEN A GETs /poll/start_vote/ then POSTs {Vote_Poll_Name: "Role motion"}
THEN GET is 200 with unbound form; POST is 302 to reverse("poll")
  AND exactly one new poll belongs to A with name Role motion
  AND its counts are 0/0 and end is NULL
  AND assert_unchanged(before)
  AND no vote choices are created or reset
```

<a id="pp-04d"></a>

### PP-04d — test_superuser_without_profile_cannot_create_public_poll

Parent: `PP-04` | Operation: `PP-V01-CREATE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:35–36`; `SPDWEBAPP/PARLEYPRO/pp_decorators.py:30–48`

```text
GIVEN make_user(username="a", with_profile=False, is_superuser=True) creates A
  AND B owns closed H; before = snapshot_scope([A, B, H])
WHEN A GETs create and separately POSTs {Vote_Poll_Name: "Privileged motion"}
  AND HTTP_REFERER is /auth/login/
THEN both responses are 302 to /auth/login/ with profile-not-found message
  AND no public poll or choice row is created
  AND assert_unchanged(before)
  AND Django superuser status does not supply public domain roles
```

<a id="pp-05a"></a>

### PP-05a — test_create_rejects_missing_or_bad_csrf

Parent: `PP-05` | Operation: `PP-V01-CREATE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:15–50`; `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:32–37`

```text
GIVEN A has only EXEC and ACTIVE; B owns closed H and has a Nay choice
  AND no poll is open; client = csrf_client()
  AND login_actor(client, A); before = snapshot_scope([A, B, H, B_choice])
WHEN client POSTs /poll/start_vote/ with {Vote_Poll_Name: "CSRF motion"}
  AND token is absent, then separately an invalid token with CSRF cookie present
THEN each response is 403 from CSRF middleware
  AND poll and choice row counts do not change
  AND assert_unchanged(before); no admin audit row exists
```

<a id="pp-05b"></a>

### PP-05b — test_cast_rejects_missing_or_bad_csrf

Parent: `PP-05` | Operation: `PP-V02-CAST` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:15–50`; `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:32–37`

```text
GIVEN A has only ACTIVE; B owns closed H and has a Nay choice
  AND A owns open P; client = csrf_client()
  AND login_actor(client, A); before = snapshot_scope([A, B, H, B_choice, P])
WHEN client POSTs /poll/ with {aye: "1"}
  AND token is absent, then separately an invalid token with CSRF cookie present
THEN each response is 403 from CSRF middleware
  AND poll and choice row counts do not change
  AND assert_unchanged(before); no admin audit row exists
```

<a id="pp-05c"></a>

### PP-05c — test_close_rejects_missing_or_bad_csrf

Parent: `PP-05` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:15–50`; `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:32–37`

```text
GIVEN A has only EXEC and ACTIVE; B owns closed H and has a Nay choice
  AND A owns open P; client = csrf_client()
  AND login_actor(client, A); before = snapshot_scope([A, B, H, B_choice, P])
WHEN client POSTs /poll/ with {end_vote: "1"}
  AND token is absent, then separately an invalid token with CSRF cookie present
THEN each response is 403 from CSRF middleware
  AND poll and choice row counts do not change
  AND assert_unchanged(before); no admin audit row exists
```

<a id="pp-05d"></a>

### PP-05d — test_token_authenticated_create_succeeds

Parent: `PP-05` | Operation: `PP-V01-CREATE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/templates/create_poll.html:11–24`; `SPDWEBAPP/PARLEYPRO/views.py:38–45`

```text
GIVEN A has only EXEC and ACTIVE; no poll is open; client = csrf_client()
  AND login_actor(client, A); B owns closed H
WHEN GET /poll/start_vote/ supplies a real cookie and rendered hidden CSRF token
  AND client POSTs {Vote_Poll_Name: "Token motion", csrfmiddlewaretoken: token}
THEN response is 302 to reverse("poll")
  AND exactly one open poll belongs to A with name Token motion and counts 0/0
  AND H, B, A's roles and all existing choices are unchanged
  AND the authenticated session identity remains A
```

<a id="pp-05e"></a>

### PP-05e — test_token_authenticated_cast_succeeds

Parent: `PP-05` | Operation: `PP-V02-CAST` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:32–37`; `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A has only ACTIVE and no choice; A owns open P; B has a Nay choice
  AND client = csrf_client(); login_actor(client, A)
  AND before = snapshot_scope([A, B, P, B_choice])
WHEN GET /poll/ supplies a real cookie and rendered hidden CSRF token
  AND client POSTs {aye: "1", csrfmiddlewaretoken: token} to /poll/
THEN response is 200; A has exactly one new Aye row
  AND assert_unchanged(before)
  AND P's saved counts/end and B's choice are unchanged
```

<a id="pp-05f"></a>

### PP-05f — test_token_authenticated_close_succeeds

Parent: `PP-05` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:32–37`; `SPDWEBAPP/PARLEYPRO/pp_functions.py:30–41`

```text
GIVEN A has only EXEC and ACTIVE, owns open P, and has an Aye choice
  AND client = csrf_client(); login_actor(client, A)
  AND before = snapshot_scope([A, P, A_choice])
WHEN GET /poll/ supplies a real cookie and rendered hidden CSRF token
  AND client POSTs {end_vote: "1", csrfmiddlewaretoken: token} under at_time(T)
THEN response is 200; P has saved counts 1/0 and end T
  AND A_choice is No Vote with the same PK and user
  AND only P's Vote_Poll_Count_Yes, Vote_Poll_Count_No, Vote_Poll_End change
  AND only A_choice.user_vote_choice changes; refreshed A and ownership links are unchanged
```

<a id="pp-05g"></a>

### PP-05g — test_live_post_obeys_csrf_while_get_remains_read_only

Parent: `PP-05` | Operation: `PP-V04-LIVE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-08: allowed methods; POL-03: live audience
Source: `SPDWEBAPP/PARLEYPRO/views.py:61–68`

```text
GIVEN A has only ACTIVE; A owns open P and has an Aye choice
  AND client = csrf_client(); login_actor(client, A)
  AND before = snapshot_scope([A, P, A_choice])
WHEN client POSTs /poll/poll-results/ with absent or bad CSRF token
THEN each response is 403; assert_unchanged(before)
  AND POL-08 must choose allowed read-only POST or method rejection with a token
  AND POL-03 must confirm the audience for GET live results
  AND either choice must leave polls and choices unchanged
```

<a id="pp-17a"></a>

### PP-17a — test_active_nonexec_cannot_close_or_reset

Parent: `PP-17` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `NEEDS_FIX` | Blockers: DEF-01; denial transport choice is secondary to zero writes
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:23–41`

```text
GIVEN A has only ACTIVE; B owns open P and closed H
  AND A has Aye and B has Nay; before = snapshot_scope([A, B, P, H, A_choice, B_choice])
WHEN A POSTs /poll/ with {end_vote: "1"} using a real CSRF token
THEN response signals denial and includes the EXEC-required error message
  AND P remains open with its prior saved counts
  AND A_choice and B_choice retain their original values and PKs
  AND assert_unchanged(before)
  AND DEF-01 must be fixed before this safety design can pass
```

<a id="pp-17b"></a>

### PP-17b — test_close_route_denies_actors_without_active

Parent: `PP-17` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:15–25`; `SPDWEBAPP/PARLEYPRO/pp_decorators.py:21–48`

```text
GIVEN A variants are anonymous, no-profile, roles (), ("EXEC",), or ("ALUMNI",)
  AND B owns open P and closed H; B has an Aye choice
  AND before = snapshot_scope([B, P, H, B_choice])
WHEN each actor POSTs /poll/ with {end_vote: "1"} and Referer /auth/login/
THEN response is 302 to named login for anonymous or /auth/login/ for other denials
  AND authenticated denial has a missing-profile or missing-ACTIVE message
  AND assert_unchanged(before); P stays open and B_choice stays Aye
  AND no choice or poll row is created
```

<a id="pp-17c"></a>

### PP-17c — test_direct_close_helper_has_explicit_actor_boundary

Parent: `PP-17` | Operation: `PP-V03-CLOSE` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: POL-04: helper authorization boundary; current missing-profile crash
Source: `SPDWEBAPP/PARLEYPRO/pp_functions.py:16–25`

```text
GIVEN A variants are EXEC-only or authenticated without a profile
  AND A owns open P; B has a Nay choice
  AND before = snapshot_scope([A, B, P, B_choice])
WHEN handling_end_vote_request is called directly with request.user=A
THEN POL-04 must choose a checked service boundary or documented private-only caller
  AND an unauthorized caller must not close P or reset B_choice
  AND missing-profile handling must not become an endorsed incidental crash
  AND response/exception assertions depend on the selected callable contract
```

<a id="pp-29a"></a>

### PP-29a — test_page_and_history_require_active_role

Parent: `PP-29` | Operation: `PP-V04-HISTORY` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:15–17,51–58`; `SPDWEBAPP/PARLEYPRO/pp_decorators.py:21–48`

```text
GIVEN A variants are anonymous, no-profile, roles (), ("EXEC",), ("ALUMNI",)
  AND ("NEW_MEMBER",), ("PHIL_CHAIR",), or ("EXEC", "ALUMNI")
  AND B owns open P and closed H; before = snapshot_scope([B, P, H])
WHEN each actor GETs /poll/ and /poll/past_polls/ with Referer /auth/login/
THEN each response is 302 to login or the supplied same-origin Referer
  AND authenticated denials have missing-profile or missing-ACTIVE message
  AND assert_unchanged(before)
  AND no current choice row is created
```

<a id="pp-29b"></a>

### PP-29b — test_cast_denial_preserves_choices

Parent: `PP-29` | Operation: `PP-V02-CAST` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:15–25`; `SPDWEBAPP/PARLEYPRO/pp_decorators.py:21–48`

```text
GIVEN A variants have no profile, roles (), ("EXEC",), ("ALUMNI",)
  AND ("NEW_MEMBER",), ("PHIL_CHAIR",), or are anonymous
  AND B owns open P and has Nay; before = snapshot_scope([B, P, B_choice])
WHEN each actor POSTs /poll/ with {aye: "1"} and Referer /auth/login/
THEN response is a denial redirect to login or the same-origin Referer
  AND B_choice stays Nay with its PK and P remains open with unchanged counts
  AND assert_unchanged(before)
  AND no A choice row is created
```

<a id="pp-29c"></a>

### PP-29c — test_active_and_extra_roles_can_read_and_cast

Parent: `PP-29` | Operation: `PP-V02-CAST` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/views.py:15–34,51–58`; `SPDWEBAPP/PARLEYPRO/pp_functions.py:60–71`

```text
GIVEN A variants have roles ("ACTIVE",) or ("ACTIVE", "ALUMNI")
  AND A owns open P; B owns closed H and has Nay
  AND before = snapshot_scope([A, B, P, H, B_choice])
WHEN A GETs /poll/ and /poll/past_polls/, then POSTs {aye: "1"} to /poll/
THEN all responses are 200; page shows P and history shows H
  AND exactly one A choice is Aye
  AND assert_unchanged(before)
  AND unrelated ALUMNI role neither removes access nor grants close permission
```

<a id="pp-38a"></a>

### PP-38a — test_route_denial_returns_to_safe_same_origin_referer

Parent: `PP-38` | Operation: `PP-SHARED-ROLE` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:26–48`; `SPDWEBAPP/PARLEYPRO/views.py:15–17,35–36,51–53`

```text
GIVEN A has no roles; B owns open P and has Nay
  AND before = snapshot_scope([A, B, P, B_choice])
WHEN A GETs /poll/, /poll/past_polls/ and /poll/start_vote/
  AND separately POSTs {Vote_Poll_Name: "Denied"} to create with Referer /auth/login/
THEN each response is 302 to /auth/login/ with a missing-role message
  AND authenticated session identity remains A
  AND assert_unchanged(before); no new poll or choice row appears
  AND primitive decorator tests remain AUTHENTICATE-owned
```

<a id="pp-38b"></a>

### PP-38b — test_route_denial_rejects_external_referer

Parent: `PP-38` | Operation: `PP-SHARED-ROLE` | Priority: P0
Status: `NEEDS_FIX` | Blockers: DEF-05; shared safe-redirect fix owned by AUTHENTICATE
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:26–48`

```text
GIVEN A has no roles; B owns open P; before = snapshot_scope([A, B, P])
  AND Referer variants are https://example.invalid/ and //example.invalid/
WHEN A GETs /poll/, /poll/past_polls/ and /poll/start_vote/
  AND client does not follow any redirect
THEN denial must not set Location to an external origin
  AND a safe local fallback must be used without mutating P
  AND assert_unchanged(before)
  AND AUTHENTICATE's shared DEF-05 fix is a dependency, not duplicated helper tests
```

<a id="pp-38c"></a>

### PP-38c — test_no_referer_denial_does_not_loop_back_to_denied_poll

Parent: `PP-38` | Operation: `PP-SHARED-ROLE` | Priority: P0
Status: `NEEDS_FIX` | Blockers: DEF-05; AUTHENTICATE safe fallback contract
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:28,44–48`

```text
GIVEN A has no roles; B owns open P; before = snapshot_scope([A, B, P])
  AND no HTTP_REFERER is supplied
WHEN A GETs /poll/ and the test follows redirects with a small bounded limit
THEN denial must terminate at a usable local destination, not an infinite /poll/ loop
  AND no response renders protected poll content
  AND assert_unchanged(before)
  AND A's session identity is unchanged
  AND the exact safe destination is delegated to AUTHENTICATE's shared contract
```
