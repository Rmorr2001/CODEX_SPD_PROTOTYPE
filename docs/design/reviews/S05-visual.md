# S05 visual comparison

**Final verdict: YEAH / PASS.**

- **Screen:** Member directory, `/app/members`.
- **Spec:** [S05](../screen-specs.md#s05-member-directory).
- **Concept:** [member board](../references/member-pages.png), middle panel.
- **Actual evidence opened:** [desktop](../evidence/S05-desktop.png),
  [mobile](../evidence/S05-mobile.png) and
  [mobile selection](../evidence/S05-mobile-selection.png), real built frontend and local seeded
  Django cookie session on port 8871. Not live Railway evidence.

The desktop composition is a good match: searchable/filterable member grid,
selected red border, larger right-hand detail panel and consistent member rail.
Initials replace absent photographs honestly; actual roles/classes replace
invented contact and biography fields. The group controls and search labels are
clear, with good text contrast and restrained red accents.

## Initial finding and verified correction

At 390px the selected detail panel follows all eleven member cards, far below
the selected first card. Inspecting `Directory.tsx` confirms card clicks only
change selected state; there is no focus/scroll relationship or nearby expanded
detail. A mobile member tap can therefore appear to do nothing, even though
content has updated off screen.

The builder added an accessible control/detail relationship and focus/scroll on
deliberate narrow-layout selection, leaving initial load and filter changes
alone. Reopened the refreshed full-page desktop/mobile screenshots and the new
390x844 selection screenshot. Selecting Alex Example now brings the entire
updated detail panel into view with a visible red focus outline; the desktop
side-panel composition remains unchanged. Source/test inspection confirms the
mobile check asserts the chosen member, focused panel and at least 90% viewport
visibility. The required mobile finding is closed.

No other required visual changes. Mobile cards and filters otherwise stack
cleanly without clipping or horizontal overflow.
