# Adversarial review probes

Diagnostic artifacts for [the independent review](../../../docs/testing/adversarial-review.md)
of `cb69127`. Seven reviewed defects now also run as required kills in CI's 13-probe
`tools/testing/probe_regressions.py` gate. These scripts retain their historical
diagnostic role and report both detected defects and any remaining survivors;
a zero script exit status is not a migration-approval verdict. Read the JSON and
report classification. No application source file is edited.

From the repository root, after installing `requirements-test.txt` into `.venv`:

```sh
.venv/bin/python tools/testing/adversarial/identity_probe.py auth_pclass
.venv/bin/python tools/testing/adversarial/identity_probe.py pp_page_swapped
.venv/bin/python tools/testing/adversarial/identity_probe.py nm_fraction
.venv/bin/python tools/testing/adversarial/identity_probe.py nm_display_name
.venv/bin/python tools/testing/adversarial/identity_probe.py auth_foreign_majors
.venv/bin/python tools/testing/adversarial/identity_probe.py auth_foreign_photo
.venv/bin/python tools/testing/adversarial/identity_probe.py pp_closer_creator
.venv/bin/python tools/testing/adversarial/identity_witness.py
.venv/bin/python tools/testing/adversarial/content_probe.py ph_sort
.venv/bin/python tools/testing/adversarial/content_probe.py ph_name
.venv/bin/python tools/testing/adversarial/content_probe.py ph_owner
.venv/bin/python tools/testing/adversarial/content_probe.py home_board
.venv/bin/python tools/testing/adversarial/content_probe.py home_media
.venv/bin/python tools/testing/adversarial/content_probe.py misc_filter
.venv/bin/python tools/testing/adversarial/content_probe.py misc_audit
```

Scripts select standalone synthetic settings and write ignored JSON/logs under
`work/adversarial_identity/` or `work/adversarial_hours/`. Each probe runs the whole
affected domain suite before, during and after a process-local code-object or
admin-hook mutation. `finally` restores the target. The separate identity witness
asserts differing clean/mutant values; content survivors have their own clean,
mutant and restored witnesses. Fresh in-memory SQLite is created per runner.
These scripts need no network, runtime configuration, deployed database or secrets.

The historical [JSON snapshot](../../../docs/testing/evidence/adversarial-review.json)
and reviewer reports record outcomes at the reviewed commit. [Part 1 hardening](../../../docs/testing/part-1-hardening.md) turns the seven
reviewed survivors into assertion kills; do not weaken tests to retain their
historical results. Scripts require their unique source
fragments to match, so later refactoring may require updating the diagnostic seam.
Raw reviewer scripts were preserved here with portable repository-root discovery,
output-directory creation and the identity witness import path adjusted.
