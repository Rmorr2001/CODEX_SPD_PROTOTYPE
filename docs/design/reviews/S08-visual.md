# S08 visual comparison

**Final verdict: YEAH / PASS.**

- **Screen:** Service hours, `/app/service`.
- **Spec:** [S08](../screen-specs.md#s08-service-hours).
- **Concept:** [chapter-tools board](../references/chapter-tools.png), middle.
- **Actual evidence opened:** [desktop](../evidence/S08-desktop.png),
  [mobile](../evidence/S08-mobile.png) and
  [mobile table scrolled](../evidence/S08-mobile-table.png), real built frontend
  against the seeded Django executive session on local port 8871. Not Railway.

The approved-hours summary, prominent red logging handoff, year selector and
event/status table reflect the concept's main hierarchy. Replacing its invented
quota ring with an absolute approved total is correct. A real zero approved
total and one pending record are clearly distinguished; the page does not
inflate the summary with pending hours or show an inert request form.

Desktop spacing, label contrast and the secondary chair-review panel are good.
At 390px the summary and actions stack cleanly, the year control fits, and the
page itself has no horizontal overflow. The dedicated table scroll region is
focusable/labeled, and the additional screenshot proves Hours/Status can be
reached without moving the whole page sideways.

## Initial finding and verified correction

The initial mobile table shows Event/Date with no visible clue that Hours/Status
are off screen; browser overlay scrollbars are absent in the capture. It can be
mistaken for a complete two-column table. The builder added “Scroll horizontally
to see hours and status” above the narrow-layout table and associated it with
the region using `aria-describedby`. Reopened all three refreshed screenshots:
the hint is legible in the initial mobile view, remains visible when scrolled,
and the Hours/Status cells are accessible in the scrolled viewport. Desktop
composition remains unchanged. The targeted mobile test now checks the hint
and actual status-column scrolling. This required finding is closed.

No other required visual changes remain.
