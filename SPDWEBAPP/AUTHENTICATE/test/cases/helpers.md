# Helpers cases

[Case index](../case-index.md) · [Inventory](../regression-spec.md) ·
[Shared fixtures](../../../../docs/testing/fixture-contract.md) · [Decisions](../decisions.md)

[Fresh actor/file fixture legend](../fixture-notes.md) applies independently to every case.

Pure helper cases use SimpleTestCase; cleanup uses real Major rows and A/B
relations. The command is operator-invoked, not a mounted HTTP endpoint.

Every case is a design only. Refresh named rows/relations and check file bytes
separately. Unlisted fields on named A/B rows stay unchanged, including hashes,
User first_name/last_name and staff/superuser flags; admin LogEntry is asserted
only for admin writes. Compare session identity, not whole CSRF/session blobs.

<a id="auth-a11-01a"></a>

### AUTH-A11-01a — test_filter_clean_and_whitelist_inputs

Parent: `AUTH-A11-01` | Operation: `AUTH-A11` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/utils.py:4–84; SPDWEBAPP/AUTHENTICATE/management/commands/clean_majors.py:4–13`

```text
GIVEN pure string variants: 'engineering', 'BIOLOGY', 'biological   engineering', ''
WHEN call contains_profanity for each input
THEN returns False for each listed value
  AND input strings are unchanged
  AND no ORM or filesystem operation occurs
```

<a id="auth-a11-01b"></a>

### AUTH-A11-01b — test_filter_independent_blacklist_substring

Parent: `AUTH-A11-01` | Operation: `AUTH-A11` | Priority: P2
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/utils.py:4–84; SPDWEBAPP/AUTHENTICATE/management/commands/clean_majors.py:4–13`

```text
GIVEN pure strings: 'fuck', 'FUCK', 'xxfuckxx'; no whitelist substring
WHEN call contains_profanity for each input
THEN returns True for each listed input
  AND filter is case-insensitive and currently matches substring
  AND no ORM or filesystem operation occurs
```

<a id="auth-a11-02a"></a>

### AUTH-A11-02a — test_filter_whitelist_cannot_hide_bad_term

Parent: `AUTH-A11-02` | Operation: `AUTH-A11` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [F-FILTER-BYPASS](../decisions.md#f-filter-bypass); [Q-FILTER](../decisions.md#q-filter)
Source: `SPDWEBAPP/AUTHENTICATE/utils.py:4–84; SPDWEBAPP/AUTHENTICATE/management/commands/clean_majors.py:4–13`

```text
GIVEN pure input is 'biology fuck'
WHEN call contains_profanity on that input
THEN Q-FILTER chooses token/phrase moderation rule and exact expected boolean
  AND a whitelist must not silently exempt unrelated rejected terms
  AND no ORM or filesystem operation occurs
```

<a id="auth-a11-02b"></a>

### AUTH-A11-02b — test_filter_benign_substring_and_types

Parent: `AUTH-A11-02` | Operation: `AUTH-A11` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-FILTER](../decisions.md#q-filter); [Q-PARSE](../decisions.md#q-parse)
Source: `SPDWEBAPP/AUTHENTICATE/utils.py:4–84; SPDWEBAPP/AUTHENTICATE/management/commands/clean_majors.py:4–13`

```text
GIVEN inputs: 'classical engineering', None, 7
WHEN call contains_profanity independently on each input
THEN Q-FILTER chooses false-positive handling for 'ass' inside 'classical'
  AND Q-PARSE defines typed rejection rather than incidental AttributeError
  AND no ORM or file state changes
```

<a id="auth-a11-02c"></a>

### AUTH-A11-02c — test_unused_cleaner_definition

Parent: `AUTH-A11-02` | Operation: `AUTH-A11` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [F-UNDEFINED-FILTER](../decisions.md#f-undefined-filter); [Q-FILTER](../decisions.md#q-filter)
Source: `SPDWEBAPP/AUTHENTICATE/utils.py:4–84; SPDWEBAPP/AUTHENTICATE/management/commands/clean_majors.py:4–13`

```text
GIVEN clean_profanity_from_user_fields is unused by mounted routes
  AND inputs: 'engineering', 'fuck', 'biology'
WHEN call the helper directly
THEN Q-FILTER chooses repair with documented boolean semantics versus removal
  AND retained helper must not raise NameError for inappropriate_words
  AND no ORM/file writes occur; removal is a separate authorized code change
```

<a id="auth-a11-03a"></a>

### AUTH-A11-03a — test_cleanup_catalog_and_global_links

Parent: `AUTH-A11-03` | Operation: `AUTH-A11` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-FILTER](../decisions.md#q-filter)
Source: `SPDWEBAPP/AUTHENTICATE/utils.py:4–84; SPDWEBAPP/AUTHENTICATE/management/commands/clean_majors.py:4–13`

```text
GIVEN Major rows Physics, biology, fuck exist; A/B both linked to fuck
  AND capture all three catalog rows and A/B links
WHEN call clean_existing_majors()
THEN Q-FILTER chooses destructive delete versus retention/soft-delete
  AND if current deletion retained: return 1, delete fuck and both links only
  AND Physics/biology, A/B User/profile/role rows and files remain unchanged
```

<a id="auth-a11-03b"></a>

### AUTH-A11-03b — test_cleanup_repeat_noop

Parent: `AUTH-A11-03` | Operation: `AUTH-A11` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-FILTER](../decisions.md#q-filter)
Source: `SPDWEBAPP/AUTHENTICATE/utils.py:4–84; SPDWEBAPP/AUTHENTICATE/management/commands/clean_majors.py:4–13`

```text
GIVEN first cleanup completed under Q-FILTER; only Physics/biology remain
WHEN call clean_existing_majors() again
THEN under deletion policy return 0; alternative policy must define no-op count
  AND no further catalog/link changes
  AND A/B identity/profile/roles and files remain unchanged
```

<a id="auth-a11-04a"></a>

### AUTH-A11-04a — test_cleanup_command_count_output

Parent: `AUTH-A11-04` | Operation: `AUTH-A11` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-FILTER](../decisions.md#q-filter)
Source: `SPDWEBAPP/AUTHENTICATE/utils.py:4–84; SPDWEBAPP/AUTHENTICATE/management/commands/clean_majors.py:4–13`

```text
GIVEN catalog includes Physics and fuck, linked by A/B
WHEN call_command('clean_majors') with stdout captured
THEN Q-FILTER defines allowed cleanup effects
  AND if deletion retained, stdout reports 'Removed 1 inappropriate entries.'
  AND return count/catalog/link effects agree; A/B Users/profiles/roles unchanged
```

<a id="auth-a11-04b"></a>

### AUTH-A11-04b — test_cleanup_second_delete_failure

Parent: `AUTH-A11-04` | Operation: `AUTH-A11` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-ATOMIC](../decisions.md#q-atomic); [Q-FILTER](../decisions.md#q-filter); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/utils.py:4–84; SPDWEBAPP/AUTHENTICATE/management/commands/clean_majors.py:4–13`

```text
GIVEN two independently rejected majors link A/B
  AND inject second delete failure after first delete completes
WHEN call clean_existing_majors through command with captured stdout/stderr
THEN Q-ATOMIC chooses rollback versus explicit partial-deletion report
  AND Q-ERROR forbids false completed-success count; inspect fresh rows and links
  AND unrelated catalog, A/B Users/profiles/roles and files stay unchanged
```
