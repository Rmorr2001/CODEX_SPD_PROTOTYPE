# Wave 2 implementation findings

Frozen inventory baseline: `4b103f6`; domain designs retain source baseline
`7e25ac2` and refinement baseline `c8bbc4e`.

All **76 frozen READY IDs** have one nonempty fully qualified unittest method in
[case-map.json](case-map.json). Both explicit-package and app-label discovery run
76 methods and pass. The 81 non-READY designs remain unchanged in status:
78 POLICY_BLOCKED and 3 NEEDS_FIX; they are not executed, skipped or credited.
No production code/schema/configuration change was made.

## Coordinator-approved clarifications

1. Credential/demo login writes `User.last_login` through Django's
   `user_logged_in` receiver (`django/contrib/auth/__init__.py`,
   `django/contrib/auth/models.py:update_last_login`). AUTH-A01-01c's broad
   unchanged-User wording omitted this framework effect. The coordinator approved
   asserting A.last_login equals controlled `2026-10-01T12:00:00Z`, preserving B's
   last_login and all other identity/hash/profile/privilege fields. Login tests
   control the entire request/session lifecycle rather than expiring an Oct 1
   session against the actual Oct 18 clock. Demo login likewise checks the real
   last_login effect without dropping other unchanged-state assertions.
2. AUTH-C03-05a assumed DashboardLink order was in the ordinary admin change form.
   Installed `adminsortable2/admin.py:156–161` removes the ordering field;
   `:166–173,242–267` mount the sortable update endpoint and apply `updatedItems`
   JSON through bulk_update. The coordinator approved testing Major's normal
   change form and its CHANGE LogEntry, then the actual sortable endpoint.
   Observed response: HTTP 200, `Updated 1 items`; Second(order=0) precedes First,
   its PK is retained and no fabricated standard reorder LogEntry is asserted.
3. The frozen success payload P used hometown `Columbia`. Real requests returned
   HTTP 200 `{success:false,message:"Input contains inappropriate language."}`.
   `AUTHENTICATE/utils.py:30–39` rejects substring `bi`, present in `columbia`.
   Safe-settings helper inspection confirmed all other P fields passed and
   `Demo Town` passed. The coordinator explicitly approved replacing the success
   fixture's hometown with `Demo Town` for AUTH-A04-01a/b/c and AUTH-S02b.
   Tests retain the exact successful response, field, ownership and privilege
   assertions. Case payload definitions were updated; filter/moderation policy
   remains blocked and production filtering is unchanged.

These are visible specification/fixture clarifications approved by the
coordinator, not silent reclassifications, skips, expected failures or runtime fixes.

## Actual execution

From repository root, using the already available isolated environment:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE.test --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test AUTHENTICATE --noinput
```

- Explicit package: 76 tests, 5.306 seconds, **OK**, system checks no issues.
- App label: 76 tests, 5.682 seconds, **OK**, system checks no issues.
- Static AST/mapping audit: exact 76 frozen READY keys map to 76 distinct,
  assertion-bearing methods; every Python test file is below 600 lines.
- The empty `AUTHENTICATE/tests.py` was removed once package discovery was established.

Earlier runs failed while completing test setup: HTTPS form POSTs needed a real
trusted Referer as well as cookie/form token; scoped clock freezing expired
sessions after leaving the frozen clock; sequential denied-message variants
needed independent clients; and the original hometown fixture exposed clarification
3 above. These were corrected without changing production behavior. Final counts
above report the clean completed runs, not partial or failed attempts.

The coordinator owns combined-suite execution, original nine-demo-suite validation,
executable mapping audit, mutation probes and the exception/blocker registry.
Useful mutation targets are ALL-versus-ANY role checking, password current-session
retention and image thumbnail dimensions. No source mutation probe was performed
by this agent. Existing blocked redirects, malformed inputs, file/DB partial
writes, image validation/destructive reads, major uniqueness, roster visibility,
missing-profile and custom-admin-prefix policies remain unresolved in the design.
