# S03 correctness review

**Verdict: PASS.** No required correctness fixes found.

Scope: [S03 specification](../screen-specs.md#s03-join-and-recruitment),
`/app/join`, HOME recruitment adapter/tests, React Join/client/styles, and
public navigation/CTA updates. Checks used the real seeded local fixture at
`http://127.0.0.1:8871`; they do not establish live Railway behavior.

## Independently verified

- **5 Python tests passed** with standalone settings:
  `manage.py test HOME.test.test_recruitment_api --noinput`. Public empty
  content is explicit; populated slides retain configured captions and order;
  unsafe/malformed/self-referencing interest links are suppressed; legitimate
  external destinations with an `/app/join/` path remain valid; POST is rejected.
- **3 Playwright tests passed** against the real built application (9.8s):
  `FRONTEND_TEST_URL=http://127.0.0.1:8871 PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium npm run test:e2e -- --grep join --reporter=line`.
  They check actual API content/slide captions/configured destination, refresh,
  mobile overflow, missing content, failed reads/retry and React Home → Join →
  About → Join navigation.
- The API exposes only interest URL and slide image/caption fields, reuses the
  validated public URL boundary, is read-only and sends `Cache-Control: no-store`.
  The client validates content type, shape, strings and safe URLs before render.
- Loading, image-unavailable, empty-gallery, missing-interest-link and read-error
  states are explicit. Buttons and links use meaningful labels; legacy recruitment
  remains available instead of a simulated signup or success message.
- Copy and repository imagery are consistent with existing chapter material.
  Generated event dates, contact emails and RSVP workflow were correctly omitted.
  The existing configured interest link may itself target the legacy recruitment
  page; this increment preserves that configuration and labels the action as a
  recruitment link, not as completed registration.
- Source files are under 400 lines and test files under 600. Domain README and
  singular `test/` documentation are present; `git diff --check` passed.

Build/typecheck/Prettier and affected Home tests are builder-reported checks.
The comparison report owns visual acceptance and screenshots. No original
Django transaction, schema, authorization or configuration was changed.
