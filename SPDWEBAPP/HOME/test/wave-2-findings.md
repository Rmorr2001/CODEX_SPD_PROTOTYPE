# HOME Wave 2 findings and execution

Frozen baseline `4b103f6`: 97 designs, 63 READY and 34 non-READY.
Implemented 63 READY IDs as 63 discoverable methods, all passing in isolated
business settings. The historical source/design evidence remains in
[regression-spec.md](regression-spec.md) and [cases](case-index.md).
No blocked case was silently downgraded, skipped or converted into unsafe preservation.

## Approved semantic clarification

HOME-T17a originally said seeded fields remain exactly unchanged on repeat seeding.
`railway_demo/management/commands/seed_railway_demo.py:60–61` calls
`user.set_unusable_password()` on every run. Django intentionally randomizes that
unusable marker, so its bytes are not stable even though password login stays disabled.

The coordinator explicitly approved checking stable identity/business fields, PKs and
relations while asserting `has_usable_password() == False` before and after each run.
The test excludes only demo users' `password` field from row-byte comparisons.
An unrelated synthetic usable-password user and its original hash must stay unchanged.
The case remains implemented; no business policy or code was changed.

## Fixture corrections established during execution

- Optional board email assertions require explicit blank emails because the shared
  factory supplies synthetic example.invalid email values. Tests now set those fields
  explicitly, preserving the original no-email display contract.
- Django admin bulk deletion enters through changelist, which requires view/change
  permission in addition to deletion authority. The successful bulk-delete fixture has
  exactly view+delete permissions. Delete-only direct-object handling and absent action
  permissions are exercised separately. This does not infer grants from domain roles.
- Core media routes capture document_root when imported. A domain-local isolated
  URLconf binds the identical serve view/regex to per-test temporary media; no production
  configuration or actual uploaded file is requested.

## Verification

- `manage.py test HOME.test --noinput`: 63 discovered and passing, 15.240s.
- `manage.py test HOME --noinput`: 63 discovered and passing, 7.747s.
- Both use `DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings` and the interpreter
  `/workspace/work/spd-mizzou-venv/bin/python`; full commands are in the README.
- A read-only DiscoverRunner comparison established that both labels' method-ID sets
  equal the 63 entries in case-map.json. Static checks found no duplicate methods or
  missing READY IDs, and each Python file has fewer than 600 lines.
- `git diff --check` passed for HOME's owned paths. No application behavior, shared
  harness, configuration, dependencies or Git state was edited.

The initial complete run had two fixture failures described above; subsequent complete
runs pass. Combined-suite, original demo-suite and mutation results belong to the
coordinator and are not claimed here. No source coverage percentage was measured.

## Remaining source-backed risks

The 34 non-READY designs retain the existing Q1–Q14 dependencies. In particular,
`HOME/models.py:6–19` deletes singleton rows before saving and has no database singleton
constraint; failed/racing writes and cleanup policy remain outside passing contracts.
Seed command atomicity (`seed_railway_demo.py:35`) does not undo media copies at
lines 79–80. Identity/key collisions, public board/email/media policy, unsafe links,
symlink escape and raw reorder exception disclosure remain visible in the design index.
No new approval or fix is inferred from this suite passing.
