# Wave 2 observed findings

Frozen baseline: `4b103f6`. Application behavior is unchanged.

## NM-C03-03a — delete redirect specification error (approved clarification)

Frozen setup grants staff view+delete permissions and expects a changelist redirect.
The initial explicit package run executed 50 tests: 1 failure, 18 errors.
This case observed `/admin/` after successful deletion, while expecting the marks
changelist. Standard Django `ModelAdmin.response_delete` checks
`has_change_permission(request, None)` before choosing a changelist redirect;
otherwise it redirects to `admin:index` (`django/contrib/admin/options.py:1958–1970`
in the installed dependency). NEWMEMBER `admin.py:6–15` has no override.

Coordinator explicitly approved the transport correction: assert `reverse('admin:index')` for the
existing minimal view+delete fixture. Retain confirmation, deletion, unrelated-row,
user/profile/role, session and deletion-log assertions. Do not grant extra change
permission merely to fit the incorrect redirect expectation. No production fix or
business policy change is required. The test now asserts this redirect. This is a documented expectation clarification,
not a dropped case or a readiness reclassification.

## Shared business-template composition (reported to coordinator)

The other 18 initial errors include `NoReverseMatch: demo_enter`. Business settings
include `railway_demo.context.demo_state`; that processor always returns
`demo_enabled=True` (`SPDWEBAPP/railway_demo/context.py:1–2`). The real base template
includes the demo banner at `HOME/templates/HOME/main.html:27`; the banner reverses
`demo_enter`, which is absent from business URL composition. The coordinator removed this processor from business settings and retains it in
demo settings. Domain tests continue to exercise real template rendering.

The 38 non-READY designs remain blocked at their frozen statuses. No unsafe
behavior is promoted to a passing contract.

## Final domain validation

The coordinator approved the NM-C03-03a clarification before the assertion changed.
After the shared processor correction, explicit package discovery passed 50 tests
in 7.450 seconds. App-label discovery passed the same 50 tests in 6.883 seconds.
After expanding shared state snapshots to include roles, majors, user permissions
and groups, the final package run passed all 50 tests in 10.753 seconds.
Each run reported zero system-check issues; passing runs had no failures, errors,
skips or expected failures.

Commands, from the repository root:

```sh
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test NEWMEMBER.test --noinput
DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.testing.settings /workspace/work/spd-mizzou-venv/bin/python SPDWEBAPP/manage.py test NEWMEMBER --noinput
```

A read-only discovery audit compared the case designs directly with frozen Git
baseline `4b103f6`: all 50 READY IDs map to exactly 50 discovered unittest IDs,
with no missing IDs, orphan methods or empty mappings. Owned Python files parse
and each stays below 600 lines. The obsolete assertion-free `NEWMEMBER/tests.py`
is deleted. No domain READY exceptions remain unresolved; all 38 non-READY
designs retain their original blockers. Combined runs and mutation evidence are
coordinator-owned and are not claimed here.
