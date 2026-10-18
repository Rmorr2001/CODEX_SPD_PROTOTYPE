# MISC Wave 2 findings

Frozen inventory `4b103f6`: 80 READY and 23 non-READY designs.
All 80 READY IDs map one-to-one to 80 discoverable, passing unittest methods in
[case-map.json](case-map.json). No source-contradiction exception was needed;
no skip/xfail or weak replacement assertion is credited.

## Scoped evidence

- `manage.py test MISC.test --noinput`: 80 tests, OK; no system-check issues.
- `manage.py test MISC --noinput`: 80 tests, OK; same package/app-wide discovery.
- Both use `DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings` and
  `/workspace/work/spd-mizzou-venv/bin/python`, from repository root.
- Static mapping checks match all 80 frozen READY IDs/names to methods; no duplicates.
- Tests keep original applications, templates, role checks, real ORM, admin and middleware.
- The obsolete empty `MISC/tests.py` is removed; all executable tests use singular `test/`.

## Setup corrections, not READY exceptions

Initial business-page requests exposed the shared harness including the unconditional
`railway_demo.context.demo_state` processor (always demo_enabled=True) without a
mounted demo_enter route. The coordinator removed it from business settings and
kept it in demo settings. Real pages now render without application changes.

Authentication fixtures snapshot after force_login; later fixture logins may change
last_login. Other actor/profile fields, role sets and request session identities
remain asserted. Django LogEntry caches its default callable at the field level;
`audit_time` patches the consumed `_get_default` callable in addition to the shared
Django clock. DST uses a real datetime subclass at the actual MISC import and
returns the frozen instant in the requested timezone. These are clock/fixture
seams, not mocked business behavior or weakened timestamp assertions.

Deletion confirmation compares object PK links, because multiple DST records have
identical string representations. Snapshot and queryset assertions still prove
exact selection and unchanged unselected rows. Crafted `_saveasnew` reaches add
permission checks even with no button; authorized cloning and denied cloning have
separate tests. Unavailable bulk actions retain the observed stock changelist
response while asserting no writes; detail-delete denial asserts 403.

## Retained blockers

The frozen design files and case-index retain these classifications unchanged:

- INFRA_BLOCKED (1): `MISC-T11b`.
- NEEDS_FIX (2): `MISC-T10a`, `MISC-T13a`.
- POLICY_BLOCKED (20): `MISC-T01c`, `MISC-T04c`, `MISC-T08a`, `MISC-T08b`, `MISC-T10b`, `MISC-T12b`, `MISC-T13b`, `MISC-T14a`, `MISC-T16c`, `MISC-T16d`, `MISC-T16e`, `MISC-T17c`, `MISC-T20a`, `MISC-T22h`, `MISC-T26f`, `MISC-T27d`, `MISC-T28a`, `MISC-T28b`, `MISC-T29d`, `MISC-T30a`.

D1 executable stored override HTML and D2 physical fall DST instant are concrete
unfixed defects. Q1–Q11 cover ordering, singleton/default selection, harmless
markup, physical/exact-at semantics, future validation, outage handling,
unmapped-view lifecycle, missing-profile transport, activation/deactivation UI,
conflict policy and cumulative audit. The one infrastructure-only case needs
browser capture. PostgreSQL race cases remain primarily policy-blocked and no
SQLite race guarantee is claimed.

No new endpoint, runtime fix, schema/config/dependency change, secret access,
network request, Git mutation or deployment was made. Coordinator owns combined
validation, the existing demo suite and temporary mutation-effectiveness probes.
