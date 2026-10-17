# Philanthropy regression testing

Wave 1 is a source-inspected proposal, pending coordinator verification. No tests
were implemented or executed in this wave. The [regression specification](regression-spec.md)
covers submissions, approval/denial, chair edits, academic-year statistics,
individual history, XLSX exports, the `hours_remaining` tag and domain admin.

Follow the [shared testing map](../../../docs/testing/README.md) and
[Wave 1 contract](../../../docs/testing/wave-1-agent-prompt.md).

`../tests.py` is an empty Django scaffold. Existing assertions in
`../../railway_demo/tests.py:54–77,99–109` check a few page statuses and submission
existence; they do not establish business regression coverage. See the spec for gaps.

Proposed singular-directory layout, to create only in Wave 2:

```text
test/
  README.md
  regression-spec.md
  __init__.py
  assertions.py           # reusable business/state/workbook assertions
  test_requests.py       # P01, permissions and CSRF adapters
  test_approvals.py       # P02, transitions and audit
  test_edits.py           # P03 and failure boundaries
  test_statistics.py     # P04, P07 pure helper and ORM cases
  test_history.py        # P05
  test_exports.py        # P06 XLSX values/types
  test_admin.py          # C03 domain ModelAdmin
```

Use an isolated environment installed according to [root guidance](../../../AGENTS.md)
and [demo setup](../../railway_demo/README.md). No real credentials, members,
uploads or network are needed. Shared synthetic user/profile factories and a
controlled clock must be reconciled with other domains before implementation.
Use real ORM records; use PostgreSQL and independent connections for race claims.

Current documented commands, from repository root (not run by this agent):

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py check
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test railway_demo
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY
```

The last command currently targets an empty domain scaffold. Proposed commands
after implementation/discovery verification:

```sh
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY.test
DJANGO_SETTINGS_MODULE=railway_demo.settings .venv/bin/python SPDWEBAPP/manage.py test PHILANTHROPY.test.test_exports
```

Resolve package discovery alongside existing `tests.py`; do not count a zero-test
run as success. The coordinator alone runs the shared baseline. No coverage,
lint, type-check, or CI result is claimed. Fractional hours, approval transition
policy, edit authority, history visibility and export scope remain decisions.
