# S04 and A01 visual comparison

**Verdict: YEAH / PASS for S04 and A01.**

- **Screens:** Dashboard `/app/dashboard`; session entry `/app/login`.
- **Specs:** [S04](../screen-specs.md#s04-member-dashboard) and
  [A01](../screen-specs.md#a01-session-and-access-states).
- **Concept:** [member board](../references/member-pages.png), left dashboard
  panel. A01 has no supplied concept; it derives from the accepted public shell.
- **Actual evidence opened:** [S04 desktop](../evidence/S04-desktop.png),
  [S04 mobile](../evidence/S04-mobile.png),
  [A01 desktop](../evidence/A01-desktop.png) and
  [A01 mobile](../evidence/A01-mobile.png).
- **Provenance:** real built frontend against local seeded Django at port 8871;
  authenticated dashboard uses the native CSRF-protected demo cookie session.
  These are not screenshots of the live Railway release.

## Dashboard

The black rail, red current page, white top bar, caller identity and pale main
surface follow the concept closely. Greeting, summary cards and two-column
announcement/resource panels create a clear hierarchy. Data is sparse but honest:
actual announcement/resource counts and caller role replace fictional hours,
meeting and to-do claims. The layout does not pad the page with invented records.

At 390px the rail becomes a wrapping top navigation; the active item remains
clear, the greeting and cards stack correctly and all member actions stay
visible. Text has strong contrast and the captured layout shows no clipping or
horizontal overflow. The initials avatar avoids nonexistent seeded portraits.

The small outlined navigation squares are intentional CSS marks, not broken
font glyphs. Distinct SVG icons and replacing the resource-list slash ornaments
with the shared SVG arrow would be optional refinements, not required fixes.

## Session entry

The large public-style serif introduction and restrained red-rule sign-in card
fit the established identity. Chapter-account sign-in and fictional demo entry
are clearly separated. The real select/button controls have readable labels,
generous sizing and good spacing; the mobile card fits within its page margins.
The page does not invent a shared password or visually imply a new credential
form has been migrated. No required visual revisions remain.

This comparison verifies rendering, not CSRF enforcement, permissions or session
correctness; those belong to the independent code/tests gate.

Reopened all four final screenshots after the copy/link review: the rail's
“Change demo role” action is visible in both layouts, demo guidance no longer
points to an absent control above, and reset wording now says changes “may be
reset.” The added action wraps cleanly on mobile. PASS remains unchanged.
