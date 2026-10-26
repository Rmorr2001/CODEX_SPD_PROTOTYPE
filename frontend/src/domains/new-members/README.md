# New-member marks

Owns `/app/new-members`, replacing the temporary identity-domain handoff.
`NewMemberMarks.tsx` composes loading/access/retry states and the role-specific
panels. `content.ts` validates the read contract, signed values and safe legacy
links. `MarksPanels.tsx` renders actual records; `marks-responsive.css` owns
narrow layouts separately from base styles.

NEW_MEMBER receives its own approved total, standing, class average, latest
approved mark and approved history, even when also ACTIVE. ACTIVE receives class
approved totals/analytics and only its own pending/recent denied submissions.
NM_BOARD alone receives a review handoff, without class records or personal
reasons. No milestones, eligibility promises, progress percentages or attendance
are fabricated. See the backend [authoritative rules](../../../../SPDWEBAPP/NEWMEMBER/README.md).

The existing chapter site owns all writes: ACTIVE can request marks, NM_BOARD
can review and edit them; the additional NME denial rule remains there. Links
identify that destination, with the established Django origin during Vite
development. No new configuration keys or credentials are needed.

`test/marks.spec.ts` checks real native demo entry, actual personal/class reads,
role controls, legacy request/history handoff, session expiry, network retry,
refresh and 390px layout. Build first, then run the frontend README's browser
command with `--grep 'new member sees|active class totals|ordinary active|marks network'`.

The React page still has read-only marks parity: personal approved history/standing,
active class totals and own pending/recent-denied submissions. It has no React
create, approval, edit, other-member history or export APIs yet. Those actions
remain explicitly labeled legacy links, governed by existing server permissions.
Personal history now anchors to the history already rendered in React instead of
leaving the page. The duplicate latest-entry rail and empty class-grid column are
removed. No arithmetic or role policy changed.

Before migrating writes, specify shared validation/atomic operations, board
creation's existing auto-approval, eligible targets and batch behavior, and review
reversal/self-review/educator-only deny policy. Existing HTML handlers have weaker
validation and different deny paths; do not quietly copy those defects into APIs.
