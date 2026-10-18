"""Disposable code-object mutants; tracked source and tests are never written."""
import ast
import contextlib
import inspect
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'SPDWEBAPP'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'SPDWEBAPP_CORE.testing.settings'
import django
django.setup()
from django.test.runner import DiscoverRunner

PROBES = {
    'auth_pclass': ('AUTHENTICATE', 'AUTHENTICATE.views', 'update_profile',
                    'brother_profile.pclass = pclass', 'pass # omitted pclass persistence'),
    'auth_foreign_photo': ('AUTHENTICATE', 'AUTHENTICATE.views', 'reset_photo',
                    'Brother_Profile.objects.get(user=request.user)',
                    'Brother_Profile.objects.get(user_id=request.POST.get("user_id", request.user.pk))'),
    'auth_foreign_majors': ('AUTHENTICATE', 'AUTHENTICATE.views', 'update_majors',
                    'Brother_Profile.objects.get(user=request.user)',
                    'Brother_Profile.objects.get(user_id=data.get("user_id", request.user.pk))'),
    'pp_closer_creator': ('PARLEYPRO', 'PARLEYPRO.pp_functions', 'handling_end_vote_request',
                    'current_poll.save()', 'current_poll.created_by = request.user\n        current_poll.save()'),
    'pp_page_swapped': ('PARLEYPRO', 'PARLEYPRO.views', 'poll_index',
                    "'nay_votes': nay_votes,\n        'aye_votes': aye_votes,",
                    "'nay_votes': aye_votes,\n        'aye_votes': nay_votes,"),
    'nm_fraction': ('NEWMEMBER', 'NEWMEMBER.views_functions', 'get_personal_stats',
                    'round(class_average, 1)', 'int(class_average)'),
    'nm_display_name': ('NEWMEMBER', 'NEWMEMBER.views_functions', 'calculate_member_marks',
                    'f"{member.firstName} {member.lastName}"', 'member.firstName'),
}

def run_suite(domain, phase, name):
    output = ROOT / 'work/adversarial_identity' / f'{name}-{phase}.log'
    started = time.monotonic()
    with output.open('w') as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        runner = DiscoverRunner(verbosity=2, interactive=False)
        result_holder = {}
        original = runner.run_suite
        def capture(suite, **kwargs):
            result = original(suite, **kwargs)
            result_holder['result'] = result
            return result
        runner.run_suite = capture
        status = runner.run_tests([domain + '.test'])
    result = result_holder['result']
    return dict(exit_status=status, tests_run=result.testsRun,
                failures=[t.id() for t, _ in result.failures],
                errors=[t.id() for t, _ in result.errors], skips=len(result.skipped),
                elapsed_seconds=round(time.monotonic()-started, 3), log=str(output.relative_to(ROOT)))

if __name__ == "__main__":
    (ROOT / "work/adversarial_identity").mkdir(parents=True, exist_ok=True)
    name = sys.argv[1]
    domain, modname, funcname, old, new = PROBES[name]
    import importlib
    module = importlib.import_module(modname)
    func = inspect.unwrap(getattr(module, funcname))
    source = inspect.getsource(func)
    assert source.count(old) == 1, source
    mutated = source.replace(old, new)
    tree = ast.parse(mutated)
    tree.body[0].decorator_list = []
    ns = {}
    exec(compile(tree, f'<adversarial:{name}>', 'exec'), func.__globals__, ns)
    code = func.__code__
    report = dict(name=name, domain=domain, target=f'{modname}.{funcname}', old=old, new=new)
    report['baseline'] = run_suite(domain, 'baseline', name)
    assert report['baseline']['exit_status'] == 0
    try:
        func.__code__ = ns[funcname].__code__
        report['mutant'] = run_suite(domain, 'mutant', name)
    finally:
        func.__code__ = code
    report['restored'] = run_suite(domain, 'restored', name)
    assert report['restored']['exit_status'] == 0
    report['classification'] = ('survives' if report['mutant']['exit_status'] == 0 else
                                'assertion kill' if report['mutant']['failures'] and not report['mutant']['errors'] else
                                'mixed assertion failure and error' if report['mutant']['failures'] else
                                'error (not assertion evidence)')
    out = ROOT / 'work/adversarial_identity' / (name + '.json')
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
