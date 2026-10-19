"""Require clean/restored passes and assertion kills for thirteen bounded mutants."""
import ast
import inspect
import json
import os
import sys
import textwrap
from importlib import import_module
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[2]


class Probe(NamedTuple):
    domain: str
    case_id: str
    module: str
    function: str
    old: str
    new: str
    description: str
    full_domain: bool = False


PROBES = [
    Probe("AUTHENTICATE", "AUTH-A04-01a", "AUTHENTICATE.views", "update_profile",
          "brother_profile.firstName = firstname", "brother_profile.firstName = firstname + ' mutant'",
          "Corrupt the saved own-profile first name"),
    Probe("PARLEYPRO", "PP-15b", "PARLEYPRO.pp_functions", "count_all_current_votes",
          "return aye_votes, nay_votes", "return aye_votes + 1, nay_votes",
          "Inflate the Aye tally by one"),
    Probe("PHILANTHROPY", "PH-C17a", "PHILANTHROPY.views_functions", "get_academic_year_dates",
          "date(start_year, 7, 1)", "date(start_year, 8, 1)",
          "Move academic-year start from July to August"),
    Probe("NEWMEMBER", "NM-05-01b", "NEWMEMBER.views_functions", "get_personal_stats",
          "mark_approval_status='approved'", "mark_approval_status='requested'",
          "Include requested marks instead of approved personal marks"),
    Probe("HOME", "HOME-T02a", "HOME.views", "ourHistory",
          "roles__name='ACTIVE'", "roles__name='ALUMNI'",
          "Count alumni instead of active profiles"),
    Probe("MISC", "MISC-T15b", "MISC.utils", "get_next_dst_change",
          "datetime(year, 3, 8, 2, 0)", "datetime(year, 3, 1, 2, 0)",
          "Select the first March Sunday instead of the second"),
    Probe("AUTHENTICATE", "AUTH-A04-01a", "AUTHENTICATE.views", "update_profile",
          "brother_profile.pclass = pclass", "pass  # omitted class persistence",
          "Discard the submitted profile class", True),
    Probe("PARLEYPRO", "PP-26a", "PARLEYPRO.views", "poll_index",
          "'nay_votes': nay_votes,\n        'aye_votes': aye_votes,",
          "'nay_votes': aye_votes,\n        'aye_votes': nay_votes,",
          "Reverse the current-page Aye and Nay counts", True),
    Probe("HOME", "HOME-T02c", "HOME.views", "executive_board",
          "Brother_Profile.objects.filter(roles=role)",
          "Brother_Profile.objects.filter(roles=role if role_code != 'EXT_VP' else Role.objects.get(name='PRESIDENT'))",
          "Display the president under External Vice President", True),
    Probe("PHILANTHROPY", "PH-C18a", "PHILANTHROPY.views", "philanthropy_dashboard",
          "sorted(brothers_progress, key=lambda x: x['total_hours'], reverse=True)",
          "brothers_progress", "Remove descending dashboard progress ordering", True),
    Probe("NEWMEMBER", "NM-05-01b", "NEWMEMBER.views_functions", "get_personal_stats",
          "round(class_average, 1)", "int(class_average)",
          "Truncate the fractional personal class average", True),
    Probe("NEWMEMBER", "NM-05-01a", "NEWMEMBER.views_functions", "calculate_member_marks",
          'f"{member.firstName} {member.lastName}"', "member.firstName",
          "Drop the surname from new-member progress", True),
    Probe("PHILANTHROPY", "PH-C18a", "PHILANTHROPY.views_functions", "collect_philanthropy_statistics",
          '\'full_name\': f"{brother.firstName} {brother.lastName}",', "'full_name': '',",
          "Blank the philanthropy progress member name", True),
]


def mutated_code(function, old, new):
    """Compile only the target function; preserve its globals and live route binding."""
    source = textwrap.dedent(inspect.getsource(function))
    if old not in source:
        raise ValueError(f"Mutation no longer matches {function.__name__}")
    tree = ast.parse(source.replace(old, new, 1))
    node = tree.body[0]
    node.decorator_list = []
    ast.fix_missing_locations(tree)
    namespace = {}
    exec(compile(tree, function.__code__.co_filename, "exec"), function.__globals__, namespace)
    code = namespace[node.name].__code__
    if code.co_freevars != function.__code__.co_freevars:
        raise ValueError("Mutation changes closure layout")
    return code


def clean(result):
    """A completed run must have no unsuccessful or unexecuted outcomes."""
    return result["tests_run"] > 0 and not any(result[key] for key in (
        "failures", "errors", "skips", "expected_failures", "unexpected_successes"))


def evaluate(probe, run, test_ids):
    """Observe a bounded mutant, restoring its code even if the runner raises."""
    labels = [probe.domain] if probe.full_domain else test_ids
    function = inspect.unwrap(getattr(import_module(probe.module), probe.function))
    baseline = run(labels)
    original = function.__code__
    try:
        function.__code__ = mutated_code(function, probe.old, probe.new)
        mutant = run(labels)
    finally:
        function.__code__ = original
    restored = run(labels)
    caught = (clean(baseline) and clean(restored)
              and baseline["tests_run"] == mutant["tests_run"] == restored["tests_run"]
              and mutant["failures"] > 0
              and not any(mutant[key] for key in (
                  "errors", "skips", "expected_failures", "unexpected_successes")))
    return {"domain": probe.domain, "case_id": probe.case_id, "test_ids": test_ids,
            "suite_labels": labels, "scope": "domain" if probe.full_domain else "mapped cases",
            "mutation": probe.description, "baseline": baseline, "mutant": mutant,
            "restored": restored, "caught_by_assertions": caught}


def main():
    setting = "SPDWEBAPP_CORE.testing.settings"
    if os.environ.get("DJANGO_SETTINGS_MODULE", setting) != setting:
        raise SystemExit("Mutation probes require standalone regression settings")
    os.environ["DJANGO_SETTINGS_MODULE"] = setting
    sys.path.insert(0, str(ROOT / "SPDWEBAPP"))
    import django
    django.setup()
    from django.test.runner import DiscoverRunner

    class CapturingRunner(DiscoverRunner):
        def run_suite(self, suite, **kwargs):
            self.observed = super().run_suite(suite, **kwargs)
            return self.observed

    def run(labels):
        runner = CapturingRunner(verbosity=0, interactive=False)
        runner.run_tests(labels)
        result = runner.observed
        return {"tests_run": result.testsRun, "failures": len(result.failures),
                "errors": len(result.errors), "skips": len(result.skipped),
                "expected_failures": len(result.expectedFailures),
                "unexpected_successes": len(result.unexpectedSuccesses),
                "failure_ids": [test.id() for test, _ in result.failures]}

    records = []
    for probe in PROBES:
        mapping = json.loads((ROOT / "SPDWEBAPP" / probe.domain / "test/case-map.json").read_text())
        record = evaluate(probe, run, mapping[probe.case_id])
        records.append(record)
        outcome = "caught and restored" if record["caught_by_assertions"] else "FAILED EFFECTIVENESS CHECK"
        print(f"{probe.domain} / {probe.description}: {outcome}")
    output = ROOT / "work/mutation-results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"probes": records}, indent=2) + "\n")
    if not all(record["caught_by_assertions"] for record in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
