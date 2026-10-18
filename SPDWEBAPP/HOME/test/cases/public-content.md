# Public content and client controls

See [inventory and decisions](../regression-spec.md).

### HOME-T03a — test_slide_order_preserves_all_ties

Parent: `HOME-T03` | Operation: `HOME-O04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/views.py:28–31`

```text
GIVEN slides A, B, C, D have order -1, 0, 3, 3 and synthetic images
  AND each caption is a distinct plain string
WHEN anonymous GETs /rush/
THEN response is 200 and lists A before B before both C and D
  AND all four slides appear exactly once
  AND no C-versus-D tie order is asserted
  AND refreshed slide fields and file bytes are unchanged
  AND anonymous identity remains unchanged
```

### HOME-T03b — test_slide_caption_and_image_attributes_escape_markup

Parent: `HOME-T03` | Operation: `HOME-O04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/rush.html:27–31`

```text
GIVEN a slide caption contains <script>alert(1)</script> and double quotes
  AND its intentional ORM image name contains a quote and ampersand
WHEN anonymous GETs /rush/
THEN response is 200 and caption text is HTML-escaped
  AND no injected script element or image attribute appears
  AND the image src remains one encoded attribute
  AND caption, image reference and sentinel file bytes remain unchanged
  AND no URL is followed over the network
```

### HOME-T03c — test_board_fields_escape_injected_markup

Parent: `HOME-T03` | Operation: `HOME-O05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/executive_board.html:86–109`

```text
GIVEN an ACTIVE plus EXEC plus PRESIDENT profile with markup in firstName and lastName
  AND a major and synthetic email containing quote/markup payloads via deliberate ORM setup
WHEN anonymous GETs /executive-board/
THEN response is 200 with escaped name, alt text, major and email text
  AND mailto remains one escaped attribute without injected elements
  AND the profile, user email and major relation are unchanged
  AND synthetic image bytes and anonymous identity remain unchanged
  AND public disclosure permission is separately blocked by HOME-T06e
```

### HOME-T03d — test_shell_errors_messages_and_username_escape

Parent: `HOME-T03` | Operation: `HOME-O16` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/main.html:31–44`

```text
GIVEN make_user(username="<b>actor</b>") and login_actor
  AND a message containing <script>alert(1)</script> is queued
WHEN actor GETs /?error=<img%20src=x%20onerror=alert(1)>
THEN response is 200 with escaped error, message and navbar username
  AND no injected script/image element is emitted from those values
  AND user and content rows and file bytes remain unchanged
  AND authenticated identity is unchanged
  AND message consumption and CSRF metadata may differ
```

### HOME-T03e — test_configured_interest_link_renders_in_three_buttons

Parent: `HOME-T03` | Operation: `HOME-O01, HOME-O04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/home.html:31–33; SPDWEBAPP/HOME/templates/HOME/rush.html:14–18,78–82`

```text
GIVEN RushFormLink.link is https://example.invalid/rush?a=1&b=2
  AND temporary_media has a banner and slide image
WHEN anonymous GETs / and /rush/
THEN both responses are 200
  AND home interest button and both rush buttons have the same decoded HTTPS href
  AND source markup escapes the query ampersand
  AND banner, slide and link rows and image bytes are unchanged
  AND no external request is made
```

### HOME-T03f — test_board_optional_fields_use_fallbacks

Parent: `HOME-T03` | Operation: `HOME-O05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/executive_board.html:86–109`

```text
GIVEN A has PRESIDENT with no image, majors or user email
  AND B has PHIL_CHAIR with a missing nonempty image reference
  AND both have ACTIVE and EXEC; C is a null-user office profile via explicit ORM setup
WHEN anonymous GETs /executive-board/
THEN response is 200; A uses default_profile.png and omits major/email sections
  AND B has the default-image onerror fallback markup
  AND C emits no email section without crashing
  AND all profiles, relations, image references and file bytes are unchanged
  AND C eligibility remains a separate Q2 decision
```

### HOME-T04a — test_missing_interest_link_fallback_policy

Parent: `HOME-T04` | Operation: `HOME-O01, HOME-O04` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q3: hide, disable or approved fallback destination
Source: `SPDWEBAPP/HOME/templates/HOME/rush.html:14–18,78–82`

```text
GIVEN no RushFormLink and no banner or slides
WHEN anonymous GETs / and /rush/
THEN no row or file is created by either render
  AND current source has inconsistent missing-link destinations
  AND Q3 chooses hidden buttons, disabled buttons or one safe fallback URL
  AND final href/button assertions follow that decision
  AND no external destination is fetched during this test
  AND anonymous identity remains unchanged
```

### HOME-T04b — test_empty_image_reference_does_not_crash_page

Parent: `HOME-T04` | Operation: `HOME-O01, HOME-O04` | Priority: P0
Status: `NEEDS_FIX` | Blockers: Q4: fallback appearance; defect empty field .url raises
Source: `SPDWEBAPP/HOME/templates/HOME/home.html:7–8; SPDWEBAPP/HOME/templates/HOME/rush.html:27–30`

```text
GIVEN a BannerImage or RushSlide has image="" through deliberate ORM setup
  AND a separate sentinel row and media file exist
WHEN anonymous GETs / for banner or /rush/ for slide
THEN response must be 200 without a file-url exception
  AND no invalid image access should interrupt the whole page
  AND banner/slide references are not silently rewritten or deleted
  AND the sentinel row and file bytes are unchanged
  AND Q4 selects the final omitted-image or placeholder markup
```

### HOME-T04c — test_missing_nonempty_image_keeps_page_renderable

Parent: `HOME-T04` | Operation: `HOME-O01, HOME-O04` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/home.html:7–8; SPDWEBAPP/HOME/templates/HOME/rush.html:27–30`

```text
GIVEN banner or slide image is banners/absent.webp or rush_slides/absent.webp
  AND that nonempty name has no file in temporary_media
WHEN anonymous GETs the corresponding home or rush page
THEN response is 200 and emits that image URL
  AND rendering does not read the missing image bytes
  AND image reference and unrelated content are unchanged
  AND temporary_media remains without that file
  AND asset 404 behavior is separately HOME-T06b
```

### HOME-T04d — test_unsafe_interest_url_scheme_policy

Parent: `HOME-T04` | Operation: `HOME-O01, HOME-O04` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q3: allowed schemes and rejection/fallback; unsafe ORM link
Source: `SPDWEBAPP/HOME/templates/HOME/home.html:31; SPDWEBAPP/HOME/templates/HOME/rush.html:14,78`

```text
GIVEN deliberate ORM setup saves javascript:alert(1) as RushFormLink.link
  AND a sentinel slide/image exists
WHEN anonymous GETs / and /rush/
THEN no executable interest-link navigation should be offered
  AND Q3 chooses rejection at write time or a safe render fallback
  AND final response/href assertions depend on that choice
  AND reads must not mutate the stored link, slide or image bytes
  AND no unsafe URL is navigated or fetched
```

### HOME-T05a — test_public_head_and_irrelevant_query_are_read_only

Parent: `HOME-T05` | Operation: `HOME-O01, HOME-O02, HOME-O03, HOME-O04, HOME-O05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/views.py:8–61`

```text
GIVEN business settings, a signed-in ACTIVE actor and synthetic content/images
  AND before = snapshot_scope(named content rows, roles, file bytes) before requests
WHEN actor HEADs each public route and GETs each with ?unused=1
THEN HEAD is 200 with an empty body; GET is 200
  AND GET uses the route-specific HOME template
  AND no unknown query field changes persisted content
  AND assert_unchanged(before) holds for captured rows, roles and files
  AND authenticated identity is unchanged
```

### HOME-T05b — test_public_unsafe_method_policy

Parent: `HOME-T05` | Operation: `HOME-O01, HOME-O02, HOME-O03, HOME-O04, HOME-O05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q5: render on unsafe methods or GET/HEAD-only
Source: `SPDWEBAPP/HOME/views.py:8–61`

```text
GIVEN csrf_client has a real rendered cookie/token pair and signed-in ACTIVE actor
  AND each public route has synthetic content/images
WHEN actor POSTs, PUTs or DELETEs a public route with field caption="overwrite"
  AND the acquired valid CSRF token is supplied
THEN no caption, role, content row, image bytes or actor identity changes
  AND Q5 chooses current 200 rendering or method denial
  AND the final response assertion follows that decision
  AND missing/bad CSRF is a separate middleware case HOME-T05c
```

### HOME-T05c — test_public_unsafe_request_rejects_bad_csrf

Parent: `HOME-T05` | Operation: `HOME-O01, HOME-O02, HOME-O03, HOME-O04, HOME-O05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/main.html:27; SPDWEBAPP/HOME/views.py:8–61`

```text
GIVEN csrf_client in demo settings has GET / over HTTPS to acquire a token
  AND before = snapshot_scope(named content rows, files) before any POST
WHEN client POSTs each public route with absent token or incorrect token
THEN response is 403 from real CSRF middleware
  AND view-specific content is not rendered as a successful write
  AND captured content rows and files are unchanged
  AND session identity is unchanged
  AND no CSRF bypass from the default test client is assumed
```

### HOME-T05d — test_slideshow_and_panel_controls_are_local

Parent: `HOME-T05` | Operation: `HOME-O01, HOME-O04` | Priority: P1
Status: `INFRA_BLOCKED` | Blockers: browser with controlled timers and request interception
Source: `SPDWEBAPP/HOME/templates/HOME/rush.html:86–131; SPDWEBAPP/HOME/templates/HOME/home.html:133–164`

```text
GIVEN browser fixtures render zero, one or three synthetic slides and home panels
  AND timers are controlled and all outbound requests are locally intercepted
WHEN next/previous are clicked through boundaries and 10 seconds elapse
  AND each home panel toggle is clicked twice
THEN slideshow handles zero slides without exception and wraps existing slides
  AND panel open state changes only for its corresponding content
  AND these controls emit no backend mutation requests
  AND slide/content rows, file bytes and actor identity remain unchanged
```
