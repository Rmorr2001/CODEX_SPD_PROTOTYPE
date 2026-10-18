"""Prove six selected assertions reject bounded in-memory behavior mutations."""
import ast
import inspect
import json
import os
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROBES = [
    ("AUTHENTICATE", "AUTH-A04-01a", "AUTHENTICATE.views", "update_profile",
     "brother_profile.firstName = firstname", "brother_profile.firstName = firstname + ' mutant'",
     "Corrupt the saved own-profile first name"),
    ("PARLEYPRO", "PP-15b", "PARLEYPRO.pp_functions", "count_all_current_votes",
     "return aye_votes, nay_votes", "return aye_votes + 1, nay_votes",
     "Inflate the Aye tally by one"),
    ("PHILANTHROPY", "PH-C17a", "PHILANTHROPY.views_functions", "get_academic_year_dates",
     "date(start_year, 7, 1)", "date(start_year, 8, 1)",
     "Move academic-year start from July to August"),
    ("NEWMEMBER", "NM-05-01b", "NEWMEMBER.views_functions", "get_personal_stats",
     "mark_approval_status='approved'", "mark_approval_status='requested'",
     "Include requested marks instead of approved personal marks"),
    ("HOME", "HOME-T02a", "HOME.views", "ourHistory",
     "roles__name='ACTIVE'", "roles__name='ALUMNI'",
     "Count alumni instead of active profiles"),
    ("MISC", "MISC-T15b", "MISC.utils", "get_next_dst_change",
     "datetime(year, 3, 8, 2, 0)", "datetime(year, 3, 1, 2, 0)",
     "Select the first March Sunday instead of the second"),
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


def main():
    setting = "SPDWEBAPP_CORE.testing.settings"
    if os.environ.get("DJANGO_SETTINGS_MODULE", setting) != setting:
        raise SystemExit("Mutation probes require standalone regression settings")
    os.environ["DJANGO_SETTINGS_MODULE"] = setting
    sys.path.insert(0, str(ROOT / "SPDWEBAPP"))
    import django
    django.setup()
    from django.test.runner import DiscoverRunner
    from importlib import import_module

    class CapturingRunner(DiscoverRunner):
        def run_suite(self, suite, **kwargs):
            self.observed = super().run_suite(suite, **kwargs)
            return self.observed

    def run(test_id):
        runner = CapturingRunner(verbosity=0, interactive=False)
        runner.run_tests([test_id])
        result = runner.observed
        return {"tests_run": result.testsRun, "failures": len(result.failures),
                "errors": len(result.errors), "skips": len(result.skipped)}

    records = []
    for domain, case_id, module_name, name, old, new, description in PROBES:
        mapping = json.loads((ROOT / "SPDWEBAPP" / domain / "test/case-map.json").read_text())
        test_id = mapping[case_id][0]
        function = inspect.unwrap(getattr(import_module(module_name), name))
        baseline = run(test_id)
        original = function.__code__
        try:
            function.__code__ = mutated_code(function, old, new)
            mutant = run(test_id)
        finally:
            function.__code__ = original
        restored = run(test_id)
        caught = (baseline["tests_run"] == 1 and baseline["failures"] == baseline["errors"] == baseline["skips"] == 0
                  and mutant["tests_run"] == 1 and mutant["failures"] > 0 and mutant["errors"] == 0
                  and restored["tests_run"] == 1 and restored["failures"] == restored["errors"] == restored["skips"] == 0)
        records.append({"domain": domain, "case_id": case_id, "test_id": test_id,
                        "mutation": description, "baseline": baseline, "mutant": mutant,
                        "restored": restored, "caught_by_assertions": caught})
        print(f"{domain}: {'caught and restored' if caught else 'FAILED EFFECTIVENESS CHECK'}")
    output = ROOT / "work/mutation-results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"probes": records}, indent=2) + "\n")
    if not all(record["caught_by_assertions"] for record in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
