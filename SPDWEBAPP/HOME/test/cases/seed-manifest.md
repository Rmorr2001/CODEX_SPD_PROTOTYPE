# Fictional seed manifest and repeatability

D02 delivery belongs to HOME; implementation stays in railway_demo.
See [decisions](../regression-spec.md) and the shared fixture contract.
No seed case uses a real account or runs in this documentation wave.

## Identity manifest

All profiles use hometown Example City and pclass Beta Omicron, one shared major
Engineering (demo), and no profile image. User email is `<username>@example.invalid`.
All groups are `railway-demo:<username>`. Source: seed_railway_demo.py:16–29,57–68.

| Username | First / last | Exact roles |
| --- | --- | --- |
| demo-executive | Alex / Example | ACTIVE, EXEC, PRESIDENT, PHIL_CHAIR, NM_BOARD, NME |
| demo-active | Jordan / Sample | ACTIVE |
| demo-3 | Taylor / Demo | ACTIVE, EXEC, EXT_VP |
| demo-4 | Casey / Example | ACTIVE, EXEC, PHIL_CHAIR |
| demo-5 | Morgan / Sample | ACTIVE, EXEC, RECRUITMENT_CHAIR |
| demo-6 | Riley / Demo | ACTIVE, EXEC, RISK_MGR |
| demo-7 | Jamie / Example | ACTIVE, EXEC, SOCIAL_CHAIR |
| demo-8 | Avery / Sample | ACTIVE, EXEC, BUSINESS_MGR |
| demo-9 | Quinn / Demo | ACTIVE, EXEC, AFFAIRS_DIRECTOR |
| demo-newmember | Cameron / Example | NEW_MEMBER |
| demo-11 | Drew / Sample | NEW_MEMBER |
| demo-alumni | Hayden / Demo | ALUMNI |

The exact role manifest implies nine ACTIVE profiles and no INT_VP holder.
Use owning-domain assertions only for seeded field/relationship shape, never duplicate
full approval/voting permission rules or treat the executive as narrow-role proof.

### HOME-T16a — test_first_seed_creates_exact_fictional_identities

Parent: `HOME-T16` | Operation: `HOME-O11, HOME-O12` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:16–70`

```text
GIVEN empty demo test DB and temporary_media with public synthetic source image
  AND an outside sentinel file has captured nonsecret bytes
  AND at_time fixes 2026-10-01T12:00:00Z
WHEN call_command("seed_railway_demo") runs
THEN output announces 12 fictional members without credentials
  AND exactly 12 users/profiles match this file’s identity manifest
  AND each has unusable password, nonstaff/nonsuperuser flags and example.invalid email
  AND each has its own railway-demo:<username> group, null photo and shared demo major
  AND outside sentinel bytes are unchanged and runtime config is never read
```

### HOME-T16b — test_first_seed_creates_public_content_and_media

Parent: `HOME-T16` | Operation: `HOME-O11, HOME-O13` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:73–87`

```text
GIVEN empty demo DB, temporary_media and a synthetic public source image
  AND DEMO_PUBLIC_DOMAIN="demo.example.invalid"
WHEN call_command("seed_railway_demo") runs
THEN command succeeds with one banner, link and sample slide
  AND references are banners/demo-banner.webp and rush_slides/demo-slide.webp
  AND both files equal source bytes; slide caption is Chapter life — sample slide, order 0
  AND link is https://demo.example.invalid/rush/
  AND outside canary bytes and unrelated source files remain unchanged
```

### HOME-T16c — test_first_seed_creates_alert_and_dashboard_manifest

Parent: `HOME-T16` | Operation: `HOME-O13` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:88–91`

```text
GIVEN demo DB has no seed rows and temporary public source image/media
  AND unrelated user sentinel and outside file bytes are captured before seeding
WHEN command seed_railway_demo runs
THEN output reports success
  AND Welcome to the seeded demo alert is active with the exact fictional notice text
  AND Demo chapter notice daylight alert is inactive
  AND dashboard links are Executive Board:/executive-board/:0
  AND Rush Information:/rush/:1 and Member profile:/auth/profile/:2
  AND outside sentinel file and unrelated user fields remain unchanged
  AND notice content is the exact fictional notice literal at source line 88
```

### HOME-T16d — test_first_seed_populates_hours_and_votes

Parent: `HOME-T16` | Operation: `HOME-O14` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:94–103`

```text
GIVEN empty demo DB/media and at_time("2026-10-01T12:00:00Z")
  AND an outside synthetic sentinel file has captured bytes
WHEN command seed_railway_demo runs
THEN command succeeds with 9 service rows for the first 9 manifest users
  AND title is Demo: community service; hours are 3+index; date is 2026-09-28
  AND indices 0,3,6 are requested with no approver and Nay vote
  AND other indices are approved by Alex Example with Aye vote
  AND exactly 9 Brother_votes rows link to those users
  AND unrelated sentinel files are unchanged; approval-rule tests stay with domain owners
```

### HOME-T16e — test_first_seed_populates_newmember_marks

Parent: `HOME-T16` | Operation: `HOME-O14` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:104–109`

```text
GIVEN empty demo DB/media and at_time("2026-10-01T12:00:00Z")
  AND an outside synthetic sentinel file has captured bytes
WHEN command seed_railway_demo runs
THEN command succeeds with 4 marks for demo-newmember and demo-11
  AND requester is demo-executive and mark date is 2026-09-29
  AND each target has approved value 3 with approver Alex Example
  AND each target has requested value 1 with no approver
  AND titles are Demo: chapter participation (approved) or (requested)
  AND sentinel files remain unchanged; owner-domain rules are not duplicated
```

### HOME-T16f — test_first_seed_populates_open_and_closed_polls

Parent: `HOME-T16` | Operation: `HOME-O14` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:110–114`

```text
GIVEN empty demo DB/media and at_time("2026-10-01T12:00:00Z")
  AND an outside synthetic sentinel file has captured bytes
WHEN command seed_railway_demo runs
THEN command succeeds with exactly two polls created by demo-executive
  AND Demo: next service activity has no end timestamp
  AND Demo: previous chapter motion ends 2026-09-24T12:00:00Z
  AND closed poll counts are Yes=8 and No=1
  AND no private poll or external service is used
  AND outside sentinel file remains unchanged
```

### HOME-T17a — test_repeat_seed_preserves_stable_row_identity

Parent: `HOME-T17` | Operation: `HOME-O11, HOME-O12, HOME-O13, HOME-O14` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:35–114`

```text
GIVEN one completed synthetic seed at 2026-10-01T12:00:00Z
  AND before = snapshot_scope(seed_rows, relations=[groups, roles, majors], files=images)
WHEN command runs twice more at that same at_time without edits
THEN each run reports success and every lookup-key record keeps its PK
  AND counts remain 12 users/profiles, 9 votes/hours, 4 marks and 2 polls
  AND exact fields, group/role/major relations and image bytes are unchanged
  AND no duplicate banner, link, slide, alert or dashboard link appears
  AND no new privilege or usable password is introduced
```

### HOME-T17b — test_repeat_seed_preserves_unrelated_synthetic_records

Parent: `HOME-T17` | Operation: `HOME-O11, HOME-O12, HOME-O13, HOME-O14` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:45–114`

```text
GIVEN a synthetic seed plus unrelated user/profile with no demo groups
  AND uniquely titled/captioned workflow, alert, dashboard and slide rows
  AND before = snapshot_scope(unrelated_rows, relations=unrelated_roles, files=[sentinel])
WHEN command seed_railway_demo runs again at the fixed clock
THEN command succeeds without new duplicate sample records
  AND assert_unchanged(before) holds for the unrelated records and relations
  AND unrelated file references and bytes remain unchanged
  AND seed-key collisions are excluded here and assessed by HOME-T20b
```

### HOME-T17c — test_member_field_role_and_photo_reset_policy

Parent: `HOME-T17` | Operation: `HOME-O12` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q11 approve reset versus preserve edited demo member fields
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:57–68`

```text
GIVEN a seeded unprivileged user retains its demo group and unusable password
  AND its name/email/hometown/pclass, roles, majors and photo were synthetically edited
WHEN command seed_railway_demo runs again
THEN Q11 chooses restoring manifest member fields versus preserving edits
  AND final user/profile/role/major assertions follow that decision
  AND no usable password or staff/superuser privilege may be introduced
  AND unrelated user, content rows and sentinel image bytes remain unchanged
  AND photo reference reset is distinct from Q7 physical-file retention
```

### HOME-T17d — test_seed_preserves_existing_home_rows

Parent: `HOME-T17` | Operation: `HOME-O13` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:81–89`

```text
GIVEN an existing custom banner/link and matching-caption sample slide with order 5
  AND an existing Demo chapter notice daylight alert is active
  AND their values and real custom image bytes are captured
WHEN command seed_railway_demo runs with isolated public source/media
THEN command succeeds without replacing these existing row fields
  AND banner/link PKs and values, slide image/order and daylight active flag are unchanged
  AND custom referenced image bytes remain unchanged
  AND reserved demo-file overwrite behavior is separately Q12-blocked
```

### HOME-T17e — test_alert_and_dashboard_refresh_policy

Parent: `HOME-T17` | Operation: `HOME-O13` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q11 approve refresh versus preserve edited matching-key content
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:88–91`

```text
GIVEN seeded announcement content/active flag and dashboard link/order were edited
  AND titles/text still match the reserved lookup keys
WHEN command seed_railway_demo runs again
THEN Q11 chooses source-default refresh versus preserving those edits
  AND exact content, is_active, link and order assertions follow that choice
  AND reserved rows must not duplicate
  AND unrelated alerts, dashboard rows and file bytes remain unchanged
  AND collision with unrelated matching-key content is separately HOME-T20b
```

### HOME-T17f — test_workflow_vote_and_date_refresh_policy

Parent: `HOME-T17` | Operation: `HOME-O14` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q11 approve resetting sample workflows versus preserving interactions
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:94–114`

```text
GIVEN seeded hours/status/approvers, marks, votes and poll counts/end were edited
  AND all reserved user/title lookup keys still match
WHEN command runs at at_time("2026-10-02T12:00:00Z")
THEN Q11 chooses reset to dated source defaults versus preserving interactions
  AND exact field and relative-date assertions follow that decision
  AND sample PKs remain nonduplicated under either approved outcome
  AND unrelated workflows, users, file bytes and actor identity remain unchanged
  AND owning domains retain full approval/vote transition tests
```

### HOME-T17g — test_group_bound_renamed_member_recovery_policy

Parent: `HOME-T17` | Operation: `HOME-O12` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q11 username reset; Q13 group identity ownership
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:49–62`

```text
GIVEN a seeded unprivileged unusable-password user is renamed by a synthetic edit
  AND its sole railway-demo:<original-username> group still uniquely identifies it
  AND no other user owns the original username
WHEN command seed_railway_demo runs again
THEN Q11/Q13 choose original username restoration or preserved rename
  AND exact username and identity assertions follow that choice
  AND no second user is silently created or reassigned
  AND unrelated users, group relations and file bytes remain unchanged
```
