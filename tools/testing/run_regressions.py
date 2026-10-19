"""Run the real suite and reject missing, skipped or unsuccessful READY mappings."""
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from unittest import TextTestResult

ROOT = Path(__file__).resolve().parents[2]
DOMAINS = ("AUTHENTICATE", "PARLEYPRO", "PHILANTHROPY", "NEWMEMBER", "HOME", "MISC")
SETTINGS = "SPDWEBAPP_CORE.testing.settings"


def flatten(suite):
    for item in suite:
        if hasattr(item, "_tests"):
            yield from flatten(item)
        else:
            yield item


def read_mapping(inventory):
    """Resolve all frozen READY IDs to explicitly declared real unittest methods."""
    mapping, errors = {}, []
    ready = {case["id"]: case for case in inventory["cases"] if case["status"] == "READY"}
    for domain in DOMAINS:
        path = ROOT / "SPDWEBAPP" / domain / "test/case-map.json"
        if not path.exists():
            errors.append(f"Missing mapping: {domain}")
            continue
        entries = json.loads(path.read_text())
        for case_id, test_ids in entries.items():
            if case_id not in ready or ready[case_id]["domain"] != domain:
                errors.append(f"Unapproved or wrong-domain mapping: {case_id}")
            elif not isinstance(test_ids, list) or not test_ids or not all(isinstance(x, str) for x in test_ids):
                errors.append(f"Empty or invalid test IDs: {case_id}")
            else:
                mapping[case_id] = test_ids
    errors.extend(f"Unmapped READY case: {case_id}" for case_id in sorted(set(ready) - set(mapping)))
    return mapping, errors


class RecordedResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successful_ids = set()

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successful_ids.add(test.id())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "work/test-results.json")
    parser.add_argument("--verbosity", type=int, default=1)
    args = parser.parse_args()
    # Refuse accidentally inherited deployment settings rather than importing them.
    inherited = os.environ.get("DJANGO_SETTINGS_MODULE", SETTINGS)
    if inherited != SETTINGS:
        raise SystemExit("This audit requires SPDWEBAPP_CORE.testing.settings")
    os.environ["DJANGO_SETTINGS_MODULE"] = SETTINGS
    sys.path.insert(0, str(ROOT / "SPDWEBAPP"))
    import django
    django.setup()
    from django.test.runner import DiscoverRunner

    class AuditedRunner(DiscoverRunner):
        def get_resultclass(self):
            return RecordedResult

        def run_suite(self, suite, **kwargs):
            result = super().run_suite(suite, **kwargs)
            self.recorded_result = result
            return result

    inventory = json.loads((ROOT / "docs/testing/wave-2-inventory.json").read_text())
    mapping, errors = read_mapping(inventory)
    labels = [*DOMAINS, "SPDWEBAPP_CORE.testing",
              "SPDWEBAPP_CORE.api.test", "SPDWEBAPP_CORE.frontend.test"]
    probe = AuditedRunner(verbosity=0, interactive=False)
    discovered = [case.id() for case in flatten(probe.build_suite(labels))]
    for case_id, ids in mapping.items():
        errors.extend(f"Undiscovered test for {case_id}: {name}" for name in ids if name not in discovered)
    duplicates = [name for name, count in Counter(discovered).items() if count > 1]
    errors.extend(f"Duplicate discovered test: {name}" for name in duplicates)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)

    runner = AuditedRunner(verbosity=args.verbosity, interactive=False)
    failures = runner.run_tests(labels)
    result = runner.recorded_result
    verified = {case_id: ids for case_id, ids in mapping.items()
                if all(name in result.successful_ids for name in ids)}
    unsuccessful = sorted(set(mapping) - set(verified))
    report = {
        "inventory_baseline": inventory["baseline"], "ready_cases": len(mapping),
        "verified_ready_cases": len(verified), "discovered_tests": len(discovered),
        "tests_run": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "skipped": len(result.skipped),
        "expected_failures": len(result.expectedFailures),
        "unexpected_successes": len(result.unexpectedSuccesses),
        "unsuccessful_case_ids": unsuccessful,
        "successful_test_ids": sorted(result.successful_ids),
        "case_mapping": mapping,
        "blocked_designs": [case for case in inventory["cases"] if case["status"] != "READY"],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(f"READY cases verified: {len(verified)}/{len(mapping)}; report: {args.report}")
    if failures or unsuccessful or result.skipped or result.expectedFailures or result.unexpectedSuccesses:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
