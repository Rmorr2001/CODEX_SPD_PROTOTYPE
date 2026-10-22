# S07 visual comparison

**Verdict: YEAH / PASS.**

- **Screen:** Chapter decisions, `/app/polls`.
- **Spec:** [S07](../screen-specs.md#s07-chapter-decisions).
- **Concept:** [chapter-tools board](../references/chapter-tools.png), left panel.
- **Actual evidence opened:** [desktop](../evidence/S07-desktop.png) and
  [mobile](../evidence/S07-mobile.png), real built frontend against seeded Django
  and an executive demo session at port 8871. Not live Railway evidence.

The page preserves the concept's clear current/closed division, red-edged open
motion card, red primary voting action and legible result bars in the accepted
black/white member shell. The explanatory side panel is visually secondary to
the current decision. Current and closed results each have count/percentage
labels, so their meaning does not depend on color alone.

The actual Aye/Nay motion system appropriately replaces the generated
multiple-choice volunteering ballot. The red action says “Vote in chapter site,”
rather than presenting nonfunctional React radio buttons or a pretend submit.
Current tally versus saved closed totals is explained, and the snapshot/refresh
label avoids implying an automatic live feed or inventing a closing deadline.

At 390px the current card, vote action, history and explanatory/tools panel stack
cleanly. The open/closed badges remain visible, motion names fit and all bars,
counts and action links are legible without horizontal clipping. The refresh
control remains near the heading. No required visual revision remains.

Optional copy polish: singularize labels such as “1 closed motion” and “1 vote.”
The current plural wording does not affect comprehension or use.
