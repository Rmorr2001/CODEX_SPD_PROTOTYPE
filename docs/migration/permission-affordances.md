# Permission-control correction

Parent live QA on1417a71 confirmed real cross-interface polls and service-hour
transactions. It also found two misleading affordances: ordinary ACTIVE members
saw legacy poll creation/closure controls; chairs saw decision buttons on their
own pending service requests even though the shared operation rejects them.

## Correction

- PARLEYPRO's public can_manage_polls capability uses the same ACTIVE+EXEC
  role boundary as create/close. Legacy HTML, REST list/detail responses and
  React controls now derive management availability from that shared rule.
- PHILANTHROPY's decision_is_available predicate expresses the existing pending,
  non-self transition rule after role authorization. The operation still rejects
  forged decisions. The authorized review API exposes a boolean can_decide for
  each queue row; React validates it before displaying decision buttons.
- Both review interfaces retain own requests but show Another chair must review
  instead of approve/deny controls. Chair edits retain their existing permission.
- No model/migration, role grant, self-review/reversal policy, data scope, notes,
  account or marks workflow changes are introduced.

The older legacy forgery test now obtains its real CSRF token from the existing
session bootstrap endpoint: when every request is non-decidable, the HTML queue
correctly has no action form to generate a token. Real CSRF checking and unchanged
record/audit assertions remain in place.

## Tests and release

New domain-local test_ui_permissions.py modules check allowed/denied capabilities,
HTML affordances, REST fields, forged writes and unchanged data. The new browser
permission-affordances.spec.ts checks both legacy/React role presentations against
real synthetic data, using request IDs because multiple seeded events share titles.
The first browser run exposed the old title-only test selector's ambiguity; the
corrected selector targets the actual request ID instead of weakening assertions.

Run the root regression audit, demo tests, mutation probes, production build,
formatting, schema fail-on-warn, migration-drift check and browser checks against
synthetic server and built image. Actual final results are recorded in the
companion verification JSON. Public live QA is parent-owned; this consumer's
public demo hostname remains outside its allowlist. No direct deployment is
triggered in parallel with the branch-following workflow.


Final local verification:503 backend tests,393/393 READY mappings,163 targeted
poll/service tests,13 demo tests and13 assertion mutation kills all passed.
52 Playwright checks passed once against each target (synthetic server and
rebuilt Docker image). TypeScript/Vite, formatting, schema fail-on-warn,
migration drift and diff/file-size review passed. See
[verification evidence](permission-affordances-verification.json). No migration
or domain permission policy changed. Task-owned QA container removed afterward.
