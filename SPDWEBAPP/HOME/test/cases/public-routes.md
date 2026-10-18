# Public route access and membership

See [inventory and decisions](../regression-spec.md).

### HOME-T01a — test_public_routes_render_for_narrow_actors

Parent: `HOME-T01` | Operation: `HOME-O01, HOME-O02, HOME-O03, HOME-O04, HOME-O05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/views.py:8–61`

```text
GIVEN business settings and synthetic public content with images in temporary_media
  AND before = snapshot_scope(content rows, actor roles, files) before any GET
  AND actors are anonymous, roles=(), ACTIVE, NEW_MEMBER, ALUMNI or EXEC
  AND each signed-in actor is created by make_user with an explicit username
WHEN each actor GETs /, /ourHistory/, /codeOfEthics/, /rush/, /executive-board/
THEN each response is 200 and uses its matching HOME template
  AND the named public navigation links resolve
  AND assert_unchanged(before) holds for content rows, actor roles and image bytes
  AND the signed-in actor identity is unchanged
```

### HOME-T01b — test_home_without_banner_omits_banner_image

Parent: `HOME-T01` | Operation: `HOME-O01` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/home.html:6–33`

```text
GIVEN no BannerImage and no RushFormLink rows
  AND a sentinel RushSlide and synthetic media file
WHEN anonymous GETs /
THEN response is 200 with the chapter heading and rush navigation link
  AND no Fraternity Banner image element is rendered
  AND no banner row is created by rendering
  AND the slide, its file bytes and anonymous identity are unchanged
  AND absent interest-link behavior is assessed separately by HOME-T04a
```

### HOME-T01c — test_history_empty_profile_count_is_zero

Parent: `HOME-T01` | Operation: `HOME-O02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/views.py:15–21`

```text
GIVEN no Brother_Profile rows and no ACTIVE Role row
  AND a sentinel RushFormLink points to https://example.invalid/rush
WHEN anonymous GETs /ourHistory/
THEN response is 200 with num_actives equal to integer 0
  AND the history paragraph renders 0 active members
  AND no profile or role is inserted
  AND the sentinel link is unchanged
  AND anonymous session identity is unchanged
```

### HOME-T01d — test_rush_without_slides_renders_empty_slideshow

Parent: `HOME-T01` | Operation: `HOME-O04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/rush.html:23–36`

```text
GIVEN no RushSlide rows and one HTTPS RushFormLink
  AND temporary_media contains a sentinel image
WHEN anonymous GETs /rush/
THEN response is 200 with Rush Information and no mySlides elements
  AND both interest buttons use the stored HTTPS URL
  AND previous/next controls remain present as current markup
  AND no slide is created and the link and sentinel bytes are unchanged
  AND no JavaScript execution is claimed by this server test
```

### HOME-T01e — test_board_without_officers_has_empty_message

Parent: `HOME-T01` | Operation: `HOME-O05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/views.py:33–61`

```text
GIVEN an ACTIVE-only profile and an EXEC-only profile with no office roles
  AND a sentinel BannerImage and temporary file
WHEN anonymous GETs /executive-board/
THEN response is 200 with No Executive Board members found
  AND exec_board_brothers is empty
  AND no card is created for either profile
  AND both profiles, role relations and banner bytes are unchanged
  AND no position attribute is persisted
```

### HOME-T01f — test_public_shell_without_actor_profile_uses_fallback

Parent: `HOME-T01` | Operation: `HOME-O16` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/navbar.html:26–76`

```text
GIVEN make_user(username="profileless", with_profile=False)
  AND login_actor authenticates that user in business settings
WHEN the actor GETs /
THEN response is 200 with username profileless
  AND the navbar uses images/default_profile.png
  AND no Brother_Profile is created
  AND a sentinel content row and file are unchanged
  AND authenticated identity remains profileless
```

### HOME-T02a — test_active_count_uses_distinct_role_membership

Parent: `HOME-T02` | Operation: `HOME-O02` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/views.py:15–21`

```text
GIVEN make_user users a with ACTIVE and b with ACTIVE plus EXEC
  AND c has ALUMNI and d has no roles
WHEN anonymous GETs /ourHistory/ twice
THEN both responses are 200 with num_actives equal to 2
  AND each ACTIVE profile contributes once
  AND c and d contribute zero
  AND all four profiles and their role relations are unchanged
  AND no files or authenticated identity are changed
```

### HOME-T02b — test_mixed_and_null_user_count_policy

Parent: `HOME-T02` | Operation: `HOME-O02` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q2: count all ACTIVE profiles or only eligible active users
Source: `SPDWEBAPP/HOME/views.py:15–21`

```text
GIVEN an ACTIVE plus ALUMNI profile and an ACTIVE profile with user=None
  AND a separate ACTIVE-only profile
WHEN anonymous GETs /ourHistory/
THEN response must not modify any profile or role relation
  AND current source count is 3, recorded only as characterization
  AND Q2 chooses 3 or excludes mixed-status and/or null-user profiles
  AND the final count assertion follows the chosen eligibility rule
  AND unrelated content and file bytes remain unchanged
```

### HOME-T02c — test_board_role_order_and_multi_office_pairs

Parent: `HOME-T02` | Operation: `HOME-O05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/views.py:35–55`

```text
GIVEN nine office Role rows in reverse insertion order
  AND ACTIVE plus EXEC holders for each office; A holds PRESIDENT and PHIL_CHAIR
  AND B also holds PRESIDENT; no profile carries INT_VP
WHEN anonymous GETs /executive-board/ twice
THEN both responses are 200 with each holder-office pair exactly once
  AND order is PRESIDENT, EXT_VP, AFFAIRS_DIRECTOR, BUSINESS_MGR
  AND then RECRUITMENT_CHAIR, PHIL_CHAIR, RISK_MGR, SOCIAL_CHAIR
  AND no INT_VP card appears; no order between two PRESIDENT holders is asserted
  AND profiles and roles remain unchanged with no persisted position field
```

### HOME-T02d — test_board_eligibility_and_holder_tie_policy

Parent: `HOME-T02` | Operation: `HOME-O05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q2: office alone versus ACTIVE/EXEC; tie ordering
Source: `SPDWEBAPP/HOME/views.py:49–55`

```text
GIVEN A has only PRESIDENT and B has ACTIVE plus EXEC plus PRESIDENT
  AND C has only EXEC and D has PRESIDENT plus PHIL_CHAIR
WHEN anonymous GETs /executive-board/
THEN profiles and role relations remain unchanged
  AND C has no office-derived card
  AND Q2 chooses whether A and D require additional ACTIVE or EXEC membership
  AND Q2 chooses deterministic holder tie order or explicitly unordered ties
  AND final card membership/order assertions follow that decision
```
