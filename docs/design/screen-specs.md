# Screen specifications

Use the [screen/image map and agent gates](screen-plan.md) with these contracts.
All endpoint names are proposed until their builder delivers them. Concept names,
dates, requirements, faces and numerical values are fictional design placeholders.
Real seeded records and current backend rules replace them. Each slice may deliver
a React read-only view plus clearly labeled links to functioning legacy write forms.

## S01 Home

**Reference:** public board, left. **Route:** `/app/`. **Owner:** HOME.

- Black public header and typographic ΣΦΔ identity; large editorial hero
  “Engineering a stronger brotherhood.”, red Join CTA, secondary chapter/about
  link; three readable Engineering / Brotherhood / Service pillars below.
- `GET /api/v1/public/home/` exposes configured `BannerImage` URL and safe
  `RushFormLink` URL, not profile records. Use named serialized fields and a
  documented response shape. Repository `charter_class.webp` is an acceptable
  fallback with accurate alt text when no configured banner exists.
- The generated upcoming-events row has no corresponding event model. Omit it
  or replace with honest chapter-purpose content; do not invent a schedule.
- Until S02/S03 exist, route CTA links to `/ourHistory/` and `/rush/`; replace
  internal destinations when their React screens pass. Configured interest link
  may be external; allow http(s) or safe local paths, reject script/protocol-
  relative URLs. Missing configuration gets a meaningful recruitment fallback.
- Acceptance: public GET succeeds anonymously without member data; configured
  and missing/unsafe URL/image cases; hero/image and all links render against
  actual fixture server; mobile layout has no horizontal overflow; original `/`
  remains unchanged. Existing `/app/connection` still reaches real status API.

## S02 About and Brotherhood

**Reference:** public board, middle. **Route:** `/app/about`. **Owner:** HOME.

- Editorial “Built together.” introduction, repository chapter/group imagery,
  chapter history excerpt and executive-board cards, red section labels.
- Reuse public HOME API or add a focused public about endpoint. Whitelist
  existing public executive names, displayed role, safe image URL and public
  ACTIVE count; preserve desired order from `executive_board`. No personal
  contact fields, roles-internal dumps, fabricated major/class or new statistics.
- Copy is grounded in existing `ourHistory.html` and `codeOfEthics.html`.
  Link full legacy history/ethics as supporting pages; no need to rewrite them.
- Acceptance: correct executive order with missing roles and multi-role members;
  empty board message and image fallback; dynamic active count matches fixture;
  links to recruitment and supporting legacy pages work; desktop/mobile review.

## S03 Join and Recruitment

**Reference:** public board, right. **Route:** `/app/join`. **Owner:** HOME.

- Strong recruitment hero, red interest-form CTA, “What to expect” purpose
  cards, configured ordered RushSlide images/captions and recruitment guidance.
- Read `RushFormLink` and `RushSlide` through public HOME adapter; preserve
  slide `order` and existing caption. Use safe external-link rules from S01.
- There is no schedule/RSVP model or verified officer email contract. Replace
  art's dated timeline/contact with actual configured content or honest guidance;
  no fabricated events, signup confirmation or example contact address.
- Acceptance: empty slides, missing interest URL, populated ordered slides,
  accessible image/control labels, safe CTA navigation, responsive stacked layout.

## A01 Session and Access States

**Reference:** derived from public/member shells; no generated login panel.
**Route:** `/app/login` or shared signed-out panel. **Owner:** AUTHENTICATE.

- Minimal session read endpoint returns authenticated flag and only the caller's
  safe identity/roles/capabilities when authenticated; never session keys, auth
  credentials or a list of members. Preserve cookie-based SessionAuthentication.
- Sign in opens `/auth/login/`; demo persona selection opens functioning legacy
  demo UI, whose `/demo/enter/` POST stays CSRF-protected. Accounts have unusable
  seeded passwords: do not show a made-up shared password or automatic login.
- React member screens show a clear sign-in state for anonymous callers and
  access-denied state for insufficient roles, with no confidential data flash.
  Handle session expiry during reads and retry after genuine sign-in.
- Preserve safe local return navigation only; do not inherit unchecked external
  `next` redirects. Logout navigates to actual legacy logout, then reloads session.
- Acceptance: anonymous vs signed-in vs missing-profile states; ACTIVE, ALUMNI,
  NEW_MEMBER, executive demo roles; direct API calls enforce permissions, not
  only hidden UI; sign-in link/action works through real server.

## S04 Member Dashboard

**Reference:** member board, left. **Route:** `/app/dashboard`.
**Owner:** AUTHENTICATE with MISC announcement data.

- Establish black member rail and white/red workspace; greeting from real
  session identity, active announcement feed and configured dashboard links in
  their existing `order`. Preserve original site access and connection screen.
- GET adapter returns whitelisted active `AnnouncementAlert` and DashboardLink
  fields, safe links and explicit capabilities. Do not invent event/to-do models.
  Only add statistic cards backed by a documented authorized read contract.
- Existing `dashboard` redirects NEW_MEMBER to `/newmember/`; React sends those
  members to `/app/new-members` when ready, or clearly links current legacy page
  while S09 is pending. Do not pretend all users have the same dashboard policy.
- Acceptance: authentication denied, active/inactive announcements, stable link
  order and safe URLs, empty feed/links, genuine caller greeting and new-member
  landing behavior, responsive member navigation and original-route regression.

## S05 Member Directory

**Reference:** member board, middle. **Route:** `/app/members`.
**Owner:** AUTHENTICATE.

- Searchable member cards/list with active/alumni tabs and meaningful role
  filters supported by real Role data. Optional selected-member detail panel.
- Read API reflects existing roster's excluded ALUMNI set vs alumni roster's
  included ALUMNI set, distinct profiles and last-name ordering. Serialize only
  id/display name, roles, majors, safe image and pclass; no usernames, email,
  hometown or arbitrary User model serialization in directory responses.
- Search/filter is real on returned data, with explicit no-results state;
  pagination is needed only if implemented end-to-end, never decorative arrows.
- Acceptance: anonymous denied; dual/multi-role memberships and alphabetical
  order match source; filters/search and clearing them work; no contact leakage;
  missing images/majors/empty roster render; narrow mobile layout stays usable.

## S06 My Profile

**Reference:** member board, right. **Route:** `/app/profile`.
**Owner:** AUTHENTICATE.

- Own profile identity, photo, names, username/email, hometown, pclass and majors
  only where currently available. Whitelist current-user fields; no arbitrary
  user lookup or cross-user editing selector.
- This read-only increment has a clear “Edit in chapter site” link to
  `/auth/profile/` for updates, photo/major/password workflows. Use display
  fields, not inert editable inputs and fake Save buttons.
- Generated graduation year, notification preferences and combined activity
  timeline are unsupported; omit them. A service summary requires an actual
  authorized service read contract, otherwise omit it rather than fake a ring.
- Acceptance: real own data and image fallback; no-profile error; no access to
  another caller's profile by parameter injection; successful legacy edit link;
  no unsupported or deceptively editable fields; keyboard/mobile readability.

## S07 Chapter Decisions

**Reference:** tools board, left. **Route:** `/app/polls`.
**Owner:** PARLEYPRO.

- Current-poll card, clear Open/Closed indicators, aggregate Aye/Nay counts
  and closed poll history; visual result bars include text values.
- Actual model is a motion with Aye/Nay votes, not multiple-choice volunteering
  options. Current poll is newest `Vote_Poll_End IS NULL`; current votes live in
  the global `Brother_votes` store, not a per-poll historical identity relation.
  Closed results use stored poll counts. Explain the scope faithfully.
- API and screen require ACTIVE; start/end controls require EXEC **and** ACTIVE.
  Link “Vote in chapter site” to `/poll/` and eligible creation to
  `/poll/start_vote/`; label action boundaries explicitly. Do not submit ballots
  to a dummy React endpoint or expose individual vote identities.
- Acceptance: ACTIVE allowed/ALUMNI denied; no poll and zero votes; exact newest
  current selection and closed order/counts; role-sensitive creation link;
  stable zero-safe bars, actual legacy vote flow link and no fabricated deadline.

## S08 Service Hours

**Reference:** tools board, middle. **Route:** `/app/service`.
**Owner:** PHILANTHROPY.

- Own approved-hours summary, academic-year selector, event/date/hours/status
  table and red “Log hours in chapter site” linking `/philanthropy/request/`.
  Chair approval link to `/philanthropy/approve/` requires PHIL_CHAIR + ACTIVE.
- GET requires ACTIVE and reuses approved-only totals/year boundaries from
  domain helper: July 1–June 30, own events including their existing statuses.
  Validate year input and reject malformed or unreasonable values explicitly.
- Art's 20/40-hour requirement is not authoritative. Prefer an absolute approved
  total rather than percentage; existing helper goal10 is a current statistic,
  not permission to introduce a new semester requirement. UI labels requested
  as “Pending” while preserving its actual status value and approved/denied.
- There is no notes field on the request model. Omit it and any inert form.
  Preserve existing minimum0.5 request validation on legacy destination.
- Acceptance: wrong role denied, year boundary and approved-only arithmetic,
  empty events, fractional hours, zero totals, malformed year400, correct status
  text, working request and authorized review/history links, mobile table use.

## S09 New-member Marks

**Reference:** tools board, right; retain hierarchy, adapt semantics.
**Route:** `/app/new-members`. **Owner:** NEWMEMBER.

- Title “New-member marks”, real personal approved mark total/standing or
  authorized active-member analytics, dated history and role-appropriate links.
  No milestone/checklist/attendance/initiation eligibility engine exists.
- API whitelists role-specific read fields; NEW_MEMBER sees its existing
  personal stats, ACTIVE gets supported existing analytics/submissions,
  NM_BOARD gets a review capability link. Do not publicly serialize disciplinary
  reasons, all pending marks or full profiles as a shortcut to a pretty screen.
- Use actual helpers: approved sums, negative totals, current standing label,
  ordering and submission filtering. NM_BOARD approves/edits; denying an edited
  mark additionally requires NME. ACTIVE submits requests. Link these exact
  legacy forms; do not reinterpret marks as positive completed milestones.
- Acceptance: new-member personal view vs active view, zero/negative/positive
  totals, denied/old submissions policy from helpers, unauthorized API and review
  access, no invented progress percentage or eligibility promise, actual links
  to marks/history/request/approval with their existing permissions preserved.

## A02 Shared Feedback States

- Every async screen: semantic loading status, explicit no-data/no-results
  message, error alert with real retry and cancellation/timeout handling.
  A failed API response must never silently substitute invented sample data.
- 403/unauthenticated responses are distinct from transport failures. No stale
  restricted content remains visible after session loss. API unknown paths stay
  JSON404; unknown `/app/*` routes show a useful page with public navigation.
- Verify keyboard focus, visible active navigation, contrast, field/link labels,
  390px no-overflow and desktop hierarchy. Links styled as buttons still navigate;
  buttons perform a real supported interaction. Use `aria-live` sparingly.
- Necessary legacy extras remain linked: ethics, full history, executive board,
  alumni roster, profile/photo/majors/password updates, poll creation/past polls,
  service histories/requests/approvals/exports, marks histories/requests/review/
  exports. Do not claim all legacy transactions have been ported into React.
