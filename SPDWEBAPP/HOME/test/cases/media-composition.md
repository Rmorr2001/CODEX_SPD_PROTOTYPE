# Media and composition

See [decisions](../regression-spec.md).

### HOME-T06a — test_media_serves_synthetic_image_bytes

Parent: `HOME-T06` | Operation: `HOME-O15` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:36–41`

```text
GIVEN business settings with DEBUG=False and temporary_media containing banners/a.webp
  AND a BannerImage references those synthetic bytes
WHEN anonymous GETs /media/banners/a.webp
THEN response is 200 with those exact streamed bytes and image/webp content type
  AND the media mount remains active with DEBUG=False
  AND no external fetch is performed
  AND banner reference, sentinel row and file bytes are unchanged
  AND anonymous identity is unchanged
```

### HOME-T06b — test_missing_media_and_directories_do_not_disclose

Parent: `HOME-T06` | Operation: `HOME-O15` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:36–41`

```text
GIVEN temporary_media contains banners/a.webp and an empty subdirectory
  AND a nonsecret canary outside MEDIA_ROOT is known only to the fixture
WHEN anonymous GETs /media/absent.webp and /media/subdirectory/
THEN both responses are 404 with no directory listing
  AND responses contain no canary or detailed filesystem paths
  AND banner row and file bytes are unchanged
  AND no missing file is created
  AND anonymous identity is unchanged
```

### HOME-T06c — test_lexical_media_traversal_is_denied

Parent: `HOME-T06` | Operation: `HOME-O15` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:36–41`

```text
GIVEN temporary_media and an outside-root synthetic canary file
  AND before = snapshot_scope([sentinel_profile], files=[inside_file, outside_file])
WHEN anonymous requests /media/../outside.txt and /media/%2e%2e/outside.txt
  AND /media/%2Foutside.txt and /media/a/%2e%2e/%2e%2e/outside.txt
THEN no response returns outside canary bytes or filesystem/configuration details
  AND each normalized request is 404 or denied before file serving
  AND assert_unchanged(before) holds for the named rows and files
  AND no actual runtime configuration path is requested
```

### HOME-T06d — test_media_symlink_cannot_escape_root

Parent: `HOME-T06` | Operation: `HOME-O15` | Priority: P0
Status: `NEEDS_FIX` | Blockers: lexical serve containment permits symlinks; symlink-capable fixture FS
Source: `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:36–41`

```text
GIVEN temporary_media contains link.webp symlinked to an outside synthetic canary file
  AND an unrelated inside image and profile are captured
WHEN anonymous GETs /media/link.webp
THEN response must not return outside canary bytes
  AND response must deny access without disclosing the resolved path
  AND symlink, target bytes, inside image and profile stay unchanged
  AND no actual private file or setting is used
  AND the code fix must resolve containment before following links
```

### HOME-T06e — test_public_board_and_media_visibility_policy

Parent: `HOME-T06` | Operation: `HOME-O05, HOME-O15` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q1 public fields; Q6 public media audience
Source: `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:36–41; SPDWEBAPP/HOME/templates/HOME/executive_board.html:86–109`

```text
GIVEN a synthetic officer has name, major, example.invalid email and profile image
  AND a second authenticated actor owns a different profile
WHEN anonymous, the officer and the other actor GET board and image URLs
THEN Q1 chooses public fields versus redacted/authenticated board fields
  AND Q6 chooses public media versus an authentication/ownership boundary
  AND final status and field assertions follow those audience decisions
  AND no request mutates either profile, its roles or image bytes
  AND no real member data is disclosed by the fixture
```

### HOME-T07a — test_public_templates_reference_local_assets

Parent: `HOME-T07` | Operation: `HOME-O15, HOME-O16` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/main.html:8–20,54–70`

```text
GIVEN business settings and synthetic content images in temporary_media
  AND the repository static manifest is inspected without fetching CDN URLs
WHEN anonymous GETs each of the five public routes
THEN responses are 200 with local CSS, favicon and default-image references
  AND PARLEYPRO.CSS retains its case-sensitive path
  AND static referenced file paths exist in the public repository manifest
  AND external Bootstrap, FontAwesome and script URLs are markup only
  AND content rows, image bytes and identity remain unchanged
```

### HOME-T07b — test_collected_static_assets_are_served

Parent: `HOME-T07` | Operation: `HOME-O15` | Priority: P1
Status: `INFRA_BLOCKED` | Blockers: isolated static collection plus WhiteNoise integration facility
Source: `SPDWEBAPP/railway_demo/settings.py:26–30`

```text
GIVEN demo settings and isolated collected static files including default_profile.png
  AND a build-generated file-tree artifact supplied by the separate tooling gate
WHEN integration client GETs every emitted local CSS, image and explorer URL
THEN each existing collected asset returns 200 with its expected bytes/content type
  AND an absent static asset returns 404
  AND external CDN URLs are never fetched
  AND source/static/media files and named content rows remain unchanged
  AND this does not count generator checks as HOME business tests
```

### HOME-T07c — test_demo_shell_context_controls_banner

Parent: `HOME-T07` | Operation: `HOME-O16` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/templates/HOME/main.html:27–29; SPDWEBAPP/railway_demo/context.py:1–2`

```text
GIVEN one synthetic ACTIVE actor and content rows/images
  AND business and demo safe settings modes from the fixture contract
WHEN actor GETs / through each mode
THEN both responses are 200 with named navigation links resolving
  AND demo mode includes the persona banner and business mode omits it
  AND no setting value or traceback is rendered
  AND captured rows, roles and image bytes are unchanged
  AND actor identity is unchanged in each request
```

### HOME-T07d — test_explorer_cache_header_is_scoped

Parent: `HOME-T07` | Operation: `HOME-O16` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/static_headers.py:4–7`

```text
GIVEN headers contain X-Fixture: keep and Cache-Control: max-age=60
WHEN add_headers receives /static/railway_demo/file-tree.html
THEN Cache-Control becomes no-cache and X-Fixture remains keep
  AND path argument is not opened or read
WHEN separately called with /static/css/main.css or file-tree.html.extra
THEN both headers remain unchanged
  AND no database, session or file access occurs
  AND the callback is tested with SimpleTestCase
```

### HOME-T21a — test_seed_copies_only_public_source_asset

Parent: `HOME-T21` | Operation: `HOME-O11, HOME-O13` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:73–87`

```text
GIVEN demo settings with a synthetic BASE_DIR/static/images/colony_members.webp
  AND temporary_media and an outside nonsecret canary file
WHEN command seed_railway_demo runs with file-boundary spies wrapping real temp IO
THEN command succeeds and only the specified public source image is copied
  AND banners/demo-banner.webp and rush_slides/demo-slide.webp equal source bytes
  AND no profile photo, canary, config or credential file is read
  AND unrelated sentinel user and outside file bytes remain unchanged
  AND no network request occurs
```

### HOME-T21b — test_seed_interest_url_uses_local_demo_host

Parent: `HOME-T21` | Operation: `HOME-O13` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:83–86`

```text
GIVEN no RushFormLink and DEMO_PUBLIC_DOMAIN is demo.example.invalid or None
  AND a temporary public source image and isolated media
WHEN seed_home runs for each separate fixture
THEN call returns normally
  AND link is https://demo.example.invalid/rush/ or https://localhost/rush/
  AND no external submission destination is seeded
  AND copied file references exist and unrelated rows/files remain unchanged
  AND no URL is fetched and no secret configuration is loaded
```

### HOME-T21c — test_seed_config_input_boundary_policy

Parent: `HOME-T21` | Operation: `HOME-O11, HOME-O13, HOME-O16` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: Q14: reject malformed domain/path or normalize to approved values
Source: `SPDWEBAPP/railway_demo/settings.py:8–25; SPDWEBAPP/railway_demo/management/commands/seed_railway_demo.py:75–86`

```text
GIVEN synthetic domain values include a slash, scheme, empty string and wrong type
  AND synthetic MEDIA_ROOT values include a string and a Path
WHEN command uses those isolated settings without runtime environment reads
THEN Q14 chooses supported inputs and validation/normalization response
  AND no outside fixture path, configuration content or canary is disclosed
  AND rejected inputs must not mutate unrelated users, content or files
  AND approved inputs must produce only approved in-root files and local links
  AND static inspection confirms explicit clone config binding without opening it
```
