# S01 correctness review

**Verdict: PASS after corrections.** The initial review requested the two small,
reproducible functional fixes below; both are now resolved.

Scope: [S01 specification](../screen-specs.md#s01-home), `/app/`,
`HOME/api.py`, its public contract tests, React public layout/home/client, and
updated foundation/browser tests. This is a review of local seeded application
behavior, not Railway verification. Generated events were correctly replaced
with chapter-purpose content; original Django views/models/routes are retained.

## Required fixes

1. **Our purpose navigation does not scroll.** Clicking the public-header link
   uses React Router `Link` and changes the URL to `/app#purpose` while leaving
   `window.scrollY === 0`. On a 1440×1000 viewport the target section remains
   759px below the viewport top. Reproduced with Playwright on the real fixture
   server at `http://127.0.0.1:8871/app/`. Use native fragment navigation for the
   same-page link or explicit hash-scroll handling that also works after routing
   from another public page. Add a browser assertion of the target position,
   rather than only asserting the URL fragment.
2. **The configured-link filter accepts a missing hostname.**
   `safe_public_url('https://:80')` returns the malformed URL unchanged because
   the filter checks `netloc` but not `hostname`. A configured interest link can
   therefore become an unusable recruitment CTA. Require a nonempty hostname
   for absolute HTTP(S) links and cover this case in `test_public_api.py`.

## Verified strengths and checks

- Recheck: `PublicLayout` now scrolls the rendered hash target after navigation.
  Independently clicked Our purpose from `/app/connection` on the rebuilt local
  fixture: scroll advanced from 0 to 597px (the maximum scroll at 1440×1000),
  bringing the target into view at 162px. This is correct browser clamping near
  the document end. The builder added a cross-route browser position assertion.
- Recheck: absolute server URLs now require `parsed.hostname`; the client also
  parses and validates host/protocol/userinfo. `https://:80` is covered by the
  unsafe-configured-link regression. Independently reran the five API tests:
  **5 passed** after the fix.

- Independently ran the five HOME public API tests: **5 passed**, system check
  clean. Anonymous payload has only `banner_image` and `rush_interest_url`,
  missing values are explicit nulls, mutations return 405 and responses no-store.
- Existing public/home data, singleton model behavior, authentication defaults,
  legacy routes and connection API contracts remain intact.
- Server filter rejects executable schemes, protocol-relative URLs, backslashes,
  whitespace, malformed ports, invalid bracketed hosts and userinfo. Client
  checks JSON/media type and expected fields; failure preserves useful content
  and offers retry. Actual retries and mobile overflow have browser coverage.
- No decorative submit forms, invented events or fabricated transaction success.
  Recruitment/about/member actions are real legacy links pending their screens.
- Modified application source files are below the 400-line limit; tests are
  below 600 lines. Domain ownership, singular `test/`, README and explicit
  serialized contract are present.

Frontend build/format and 11 browser tests are builder-reported checks; this
review independently exercised the navigation reproduction and Python tests.
Visual contrast/composition review belongs to the comparison report.
