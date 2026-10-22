# Public chapter pages

Owns the React presentation of HOME's public chapter content. `PublicLayout.tsx`
provides the red/black navigation and footer; `Home.tsx` owns `/app/` and
`content.ts` validates the public read API contract. `/app/connection` stays a
separate infrastructure diagnostic. Original Django routes remain available.

S01 follows the left panel of `docs/design/references/public-pages.png`. Chapter
copy and fallback imagery come from existing HOME templates and shared static
assets. The page does not invent event dates, member counts or recruitment rules.
S02 adds `/app/about` with a chapter-history excerpt, archival image and actual
executive cards/ACTIVE count from `/api/v1/public/about/`; names, displayed
positions and safe images are its complete public card contract. Contact fields
are excluded. Empty/failure states stay explicit; legacy history/ethics remain linked.

Public configured content comes from `/api/v1/public/home/`; missing content uses
repository imagery and the existing recruitment page. A failed read exposes a
retry message without hiding the editorial page. No credentials/configuration
keys are needed. Member-only records never belong in this API.

`test/` is the domain's browser test location. Run the built-app browser suite with
`npm run build --prefix frontend` followed by the frontend README's Playwright
command. Backend public contract tests: `manage.py test HOME.test.test_public_api`
with standalone testing settings. Future public pages extend this domain rather
than the application composition folder.

S03 adds `/app/join`, reading ordered recruitment images/captions and the validated
configured destination from `/api/v1/public/recruitment/`. Missing links point to
the original recruitment page with an explicit label. The page invents no dates,
RSVP form or recruitment email. `test/join.spec.ts` covers real data, empty/error
states, retry, internal navigation and mobile width.
