# S09 visual comparison

**Verdict: YEAH / PASS for personal and active/board views.**

- **Screen:** New-member marks, `/app/new-members`.
- **Spec:** [S09](../screen-specs.md#s09-new-member-marks).
- **Concept:** [chapter-tools board](../references/chapter-tools.png), right.
- **Actual evidence opened:** [personal desktop](../evidence/S09-desktop.png),
  [personal mobile](../evidence/S09-mobile.png),
  [active/board desktop](../evidence/S09-active-desktop.png) and
  [active/board mobile](../evidence/S09-active-mobile.png).
- **Provenance:** built frontend against local seeded Django on port 8871 using
  genuine new-member/executive demo cookie sessions; not the Railway release.

The design keeps the concept's summary-first hierarchy, distinct record cards
and restrained red review panel, while correctly replacing nonexistent
milestones, progress percentages and initiation eligibility with actual signed
marks, approved totals, standing, class analytics and history. The personal
screen's strong total/standing grouping makes the record's meaning clear.

Personal and class views remain visually distinct: the first emphasizes the
caller's approved history and recent entry; the second separates class totals,
the caller's pending submissions and board review actions. Pending versus
approved is stated in text rather than conveyed only by color. Handoff actions
explicitly open the chapter site instead of pretending review writes occur here.

At 390px summary metrics, dated histories, signed values and status badges remain
visible in stacked cards. The active summary uses a compact two-column layout;
names and history links fit, and review actions remain legible. There are no
hidden table columns, clipped statuses or missing glyphs in the captures.

The accepted black navigation, red active location, pale workspace and clear
typography stay consistent with prior member screens. No required visual
revisions remain. Permission and numerical correctness rely on the separate
code/tests gate, not these screenshots alone.
