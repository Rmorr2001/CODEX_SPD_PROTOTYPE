# Seed refusals and partial failures

See [inventory and decisions](../regression-spec.md) and
[first-seed field assertions](seed-manifest.md#identity-manifest).

### HOME-T18a — test_seed_non_demo_refusal_has_no_side_effects

Parent: `HOME-T18` | Operation: `HOME-O11` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:35–39`

```text
GIVEN safe isolated business settings have DEMO_MODE=False
  AND a synthetic user/profile, content row and sentinel file exist
  AND before = snapshot_scope([user, profile, content], files=[sentinel])
WHEN call_command("seed_railway_demo") is invoked
THEN CommandError states only isolated demo settings permit the seed
  AND no success message is emitted
  AND no group, role, major, profile or workflow row is created
  AND assert_unchanged(before) holds for captured rows, relations and files
  AND no runtime secret or real environment value is read
```

### HOME-T18b — test_seed_refuses_credentialed_or_privileged_identity

Parent: `HOME-T18` | Operation: `HOME-O11, HOME-O12` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:49–56`

```text
GIVEN target demo account has a usable test password, is_staff, or is_superuser
  AND identity lookup uses canonical username or a unique renamed demo-group member
  AND unrelated rows, original password hash and file bytes are captured
WHEN command seed_railway_demo runs in demo mode for each separate variant
THEN CommandError refuses a credentialed or privileged account
  AND no success text or credential/hash value is printed
  AND user fields, password hash, profile and group relations remain unchanged
  AND unrelated rows/files and all prior DB state remain unchanged
```

### HOME-T18c — test_late_member_refusal_rolls_back_prior_member_writes

Parent: `HOME-T18` | Operation: `HOME-O11, HOME-O12` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:35–69`

```text
GIVEN demo-11 is credentialed or privileged and earlier demo users need refresh
  AND before = snapshot_scope(earlier_users, relations=[groups, roles, majors])
WHEN command reaches demo-11 after writing earlier users
THEN CommandError is raised without success output
  AND after command atomic scope exits, earlier DB fields and relations are restored
  AND later unvisited users remain unchanged and no partial new users remain
  AND seed_home has not run, so media bytes are unchanged
  AND original targeted account password hash is unchanged and never printed
```

### HOME-T19a — test_late_seed_db_failure_rolls_back_all_database_writes

Parent: `HOME-T19` | Operation: `HOME-O11, HOME-O13, HOME-O14` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:35–114`

```text
GIVEN TransactionTestCase and prior synthetic seed DB rows plus temp image files
  AND before = snapshot_scope(named_seed_rows, relations=[groups, roles, majors])
WHEN a late workflow upsert raises IntegrityError after member and home writes
THEN injected error propagates with no success message
  AND after atomic scope exits all captured DB fields and relations are restored
  AND no partial seed DB rows or role/group membership writes remain
  AND existing media bytes and any copy residue are inspected separately
  AND DB rollback alone is not claimed as filesystem rollback
```

### HOME-T19b — test_media_setup_failures_roll_back_prior_db_writes

Parent: `HOME-T19` | Operation: `HOME-O11, HOME-O13` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:35–40,75–80`

```text
GIVEN TransactionTestCase and a synthetic user/member snapshot before seeding
  AND source absent, mkdir failure, first-copy failure or second-copy failure
WHEN command seed_railway_demo runs in each separately injected failure variant
THEN the corresponding OSError propagates without success output
  AND command DB transaction restores prior member/group/role/major state
  AND no HOME or workflow DB seed rows remain partially committed
  AND unrelated sentinel files remain unchanged
  AND created directory/copied-file residue is recorded, not asserted rolled back
```

### HOME-T19c — test_failed_seed_file_compensation_policy

Parent: `HOME-T19` | Operation: `HOME-O11, HOME-O13` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q12 prior media protection and cleanup; Q7 file retention
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:35–40,75–80`

```text
GIVEN reserved demo image files already contain prior usable synthetic bytes
  AND a second-copy or late DB failure will occur after first copy overwrites them
WHEN command seed_railway_demo fails
THEN Q12 chooses restore-prior bytes, stage-and-commit copies or explicit disposable reset
  AND exact old/new/residue file assertions follow that choice
  AND no unrelated sentinel file may be removed or overwritten
  AND command DB writes must roll back independently
  AND no claim of filesystem atomicity follows from transaction.atomic
```

### HOME-T19d — test_seed_retry_after_partial_failure_finishes_once

Parent: `HOME-T19` | Operation: `HOME-O11, HOME-O13, HOME-O14` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:35–114`

```text
GIVEN an empty synthetic demo DB and media with a sentinel unrelated file
  AND first command fails at the second file copy with OSError
WHEN the injection is removed and command is retried at the same controlled clock
THEN retry succeeds with 12 profiles, 9 hours/votes, 4 marks and 2 polls
  AND field assertions reuse HOME-T16a through HOME-T16f without duplicating logic
  AND both reserved image files equal source bytes
  AND earlier partial directories/files do not prevent completion
  AND sentinel unrelated file bytes remain unchanged
  AND no prior usable reserved-file protection is asserted by this retry case
```

### HOME-T20a — test_ambiguous_group_or_username_collision_policy

Parent: `HOME-T20` | Operation: `HOME-O12` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q13 unique identity/refusal; Q11 reset contract
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:49–62`

```text
GIVEN one demo group has two unusable unprivileged users or a wrong-username member
  AND separately the canonical username is held by a different synthetic user
WHEN command runs with each ambiguous identity fixture
THEN Q13 chooses explicit collision refusal versus approved unique recovery criteria
  AND no unrelated identity or credentials may be silently taken over
  AND response/error and permitted target assertions follow that decision
  AND failure must roll back earlier DB writes
  AND unrelated group/user/profile relations and image bytes remain unchanged
```

### HOME-T20b — test_nonunique_seed_key_collision_policy

Parent: `HOME-T20` | Operation: `HOME-O13, HOME-O14` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q11 reserved sample keys; Q13 collisions and duplicate lookup rows
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:81–114`

```text
GIVEN unrelated content shares a reserved caption/title/text lookup key
  AND separate variants contain duplicate nonunique matching-key rows
WHEN command seed_railway_demo runs
THEN Q11/Q13 choose rejection, namespaced seed identity or approved refresh ownership
  AND exact exception/selection and row assertions follow that choice
  AND unrelated matching-key content must not be silently destroyed
  AND command failure rolls back all earlier DB writes
  AND unrelated files/relations remain unchanged; reserved copy compensation is Q12
```

### HOME-T20c — test_direct_seed_helper_guard_and_atomicity_policy

Parent: `HOME-T20` | Operation: `HOME-O12, HOME-O13, HOME-O14` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 supported internal helpers versus guarded public seed API
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:45–114`

```text
GIVEN isolated settings with DEMO_MODE=False and synthetic DB/media snapshots
  AND separate variants inject a late member/home/workflow failure
WHEN seed_members, seed_home or seed_workflows is called directly
THEN Q8 chooses unsupported internal-only use or explicit guard/transaction guarantees
  AND final error and rollback assertions follow that decision
  AND no real configuration, user, media or network resource may be touched
  AND unrelated sentinel records and file bytes must remain unchanged
  AND current lack of helper guards/atomicity is not a passing safe contract
```

### HOME-T20d — test_workflow_user_list_input_policy

Parent: `HOME-T20` | Operation: `HOME-O14` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q8 internal list contract; Q13 correct identity mapping
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:94–114`

```text
GIVEN synthetic user inputs are empty, shorter than 11, reordered or duplicated
  AND named unrelated workflows, user roles and media bytes are captured
WHEN seed_workflows(users) is called directly for each fixture
THEN Q8/Q13 choose validated identity mapping or explicitly unsupported caller inputs
  AND exact exception and permitted row assertions follow that choice
  AND wrong owners/targets must not silently receive workflow rows
  AND failure must not corrupt unrelated workflows, roles or files
  AND command-only rollback is distinguished from direct helper partial writes
```
