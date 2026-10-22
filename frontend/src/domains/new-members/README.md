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
