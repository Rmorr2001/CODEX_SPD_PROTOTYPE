# Service hours

Owns `/app/service`: actual own approved-hours total, academic-year selector and
own event/status table. URL `?year=YYYY` preserves the selected year on refresh.
The PHILANTHROPY read API requires ACTIVE; approval links additionally require
PHIL_CHAIR. Requested status displays as Pending. Date-only events retain their
calendar day across browser time zones. The narrow table scrolls horizontally
inside a named, focusable region without overflowing the page.

Log-hours and approval actions open real existing chapter-site forms. No inert
form, notes field, artificial requirement, goal ring or completion percentage is
introduced. Existing IntegerField fractional truncation remains a backend
limitation; this UI shows the stored values. See PHILANTHROPY/README for the exact
read contract and legacy boundary. Shared API helpers handle cancellation,
timeouts and access/failure states; contracts remain validated in `content.ts`.

`test/service.spec.ts` covers actual seeded values, statuses/year changes,
approval roles, alumni denial, failed read/retry, mobile horizontal table use and
real request-form navigation. Build and run per frontend README. No new config.
