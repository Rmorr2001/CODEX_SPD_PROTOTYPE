# Chapter decisions

Owns React `/app/polls`: actual current motion, aggregate Aye/Nay results and saved
closed-motion results. PARLEYPRO's `/api/v1/polls/` read model requires ACTIVE.
EXEC and ACTIVE together enable a real legacy creation link. Ballots and motion
creation/closure remain in `/poll/` and `/poll/start_vote/`; this increment has no
write API, radio inputs, invented multiple-choice poll or fake deadline.

The current tally is the existing global `Brother_votes` aggregate, not a
per-poll historical relation. Closed totals are the counts saved on each motion.
UI explains snapshot results and offers a real Refresh read. Zero votes produce
zero-width bars, not percentages of an invented threshold. No voter identities
are exposed. `content.ts` validates contracts; shared `api/read.ts` handles access,
failure/cancellation/timeout behavior. No new configuration keys are needed.

`test/decisions.spec.ts` checks actual data/links, executive vs ordinary ACTIVE
controls, ALUMNI denial and exceptional zero/empty/failure states. Build and run
Playwright per frontend README. Backend contract tests are in PARLEYPRO/test.
