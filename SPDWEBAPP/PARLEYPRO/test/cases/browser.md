# Browser live-result behavior

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

Browser/fake-timer/intercept facilities are additional prerequisites, not installed tools.
Intercept fetch without network, and do not substitute mocked business logic.

<a id="pp-40a"></a>

### PP-40a — test_live_updates_from_initial_zero_render_without_missing_node_error

Parent: `PP-40` | Operation: `PP-V04-LIVE` | Priority: P2
Status: `INFRA_BLOCKED` | Blockers: Browser runner and intercepted fetch facility; DEF-07
Source: `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:49–64,114–147`

```text
GIVEN a browser runner and synthetic ACTIVE A with the only open P
  AND initial counts are zero and the page renders No votes yet
WHEN live updates are enabled and intercepted JSON becomes {aye_votes: 1, nay_votes: 0}
  AND a later response returns {aye_votes: 0, nay_votes: 0}
THEN no null-node JavaScript exception may occur
  AND displayed counts/proportions become 1/0 then 0/0 without stale visible results
  AND P/choices/profile/session identity are unchanged by the intercepted reads
  AND DEF-07 requires guarded/created result nodes before this can pass
```

<a id="pp-40b"></a>

### PP-40b — test_no_open_poll_live_updates_have_explicit_ui_policy

Parent: `PP-40` | Operation: `PP-V04-PAGE` | Priority: P2
Status: `POLICY_BLOCKED` | Blockers: POL-01/POL-03; browser runner; DEF-07
Source: `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:70–76,100–147`

```text
GIVEN a browser runner; ACTIVE A has no open poll and a residual Aye choice
  AND page renders No active poll at the moment and no result bars
WHEN live updates are enabled and an intercepted response contains 1/0
THEN POL-01/POL-03 must choose suppressing live fetch/display or showing global counts
  AND either choice must avoid missing-node errors and protected-data disclosure
  AND displayed content and request behavior follow that selected policy
  AND no poll or choice is created, reset or reconstructed by browser reads
  AND A's server session identity remains unchanged
```

<a id="pp-40c"></a>

### PP-40c — test_live_preference_persists_and_controls_fetch_cadence

Parent: `PP-40` | Operation: `PP-V04-LIVE` | Priority: P2
Status: `INFRA_BLOCKED` | Blockers: Browser runner; fake timers and intercepted fetch
Source: `SPDWEBAPP/PARLEYPRO/templates/poll_index.html:85–108,152–155`

```text
GIVEN a browser runner with a controllable timer and ACTIVE A viewing open P
  AND Aye/Nay bars exist; localStorage has no liveUpdateEnabled entry
WHEN checkbox is enabled, the page reloads and fake timer advances 1500 milliseconds
THEN localStorage stores "true", checkbox restores checked and fetch occurs when enabled
  AND disabling stores "false" and subsequent ticks do not issue live-result fetches
  AND intercepted JSON contains integer aye_votes/nay_votes and updates existing bars
  AND actual timer interval is 1500 milliseconds, not the five-second comment
  AND server polls/choices/session identity and unrelated localStorage are unchanged
```
