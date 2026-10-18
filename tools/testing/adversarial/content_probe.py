"""Independent, process-local probes. No tracked source or tests are changed."""
import ast
import contextlib
import inspect
import io
import json
import os
from pathlib import Path
import sys
import textwrap
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'SPDWEBAPP'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'SPDWEBAPP_CORE.testing.settings'
import django
django.setup()
from django.test.runner import DiscoverRunner
from django.test import TestCase
from django.test.signals import template_rendered
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.test import Client
from SPDWEBAPP_CORE.testing.factories import make_user
from PHILANTHROPY import views as phviews, views_functions as phfuncs
from PHILANTHROPY.test.support import make_event
from HOME import views as homeviews
from MISC.models import AnnouncementAlert
from AUTHENTICATE import views as authviews
from railway_demo.management.commands import seed_railway_demo as seed


def inner(fn):
    while hasattr(fn, '__wrapped__'):
        fn = fn.__wrapped__
    return fn


@contextlib.contextmanager
def rewrite(fn, old, new):
    fn = inner(fn)
    source = textwrap.dedent(inspect.getsource(fn))
    if source.count(old) != 1:
        raise AssertionError(f'Expected unique mutation fragment: {old!r}')
    tree = ast.parse(source.replace(old, new))
    tree.body[0].decorator_list = []
    namespace = {}
    exec(compile(tree, f'<adversarial:{fn.__name__}>', 'exec'), fn.__globals__, namespace)
    original = fn.__code__
    fn.__code__ = namespace[fn.__name__].__code__
    try:
        yield
    finally:
        fn.__code__ = original


class SortingWitness(TestCase):
    def test_descending_progress_reverses_creation_order(self):
        a = make_user(username='first', roles=('ACTIVE',))
        b = make_user(username='later', roles=('ACTIVE',))
        make_event(a, hours=2, status='approved')
        make_event(b, hours=7, status='approved')
        self.client.force_login(a)
        response = self.client.get('/philanthropy/', {'year': '2026'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([p['user'].pk for p in response.context['brothers_progress']], [b.pk, a.pk])


class NameWitness(TestCase):
    def test_progress_preserves_member_display_name(self):
        user = make_user(username='named', roles=('ACTIVE',),
                         profile_fields={'firstName': 'Alex', 'lastName': 'Synthetic'})
        self.client.force_login(user)
        response = self.client.get('/philanthropy/', {'year': '2026'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['brothers_progress'][0]['full_name'], 'Alex Synthetic')
        self.assertContains(response, 'Alex Synthetic')


class BoardWitness(TestCase):
    def test_external_vp_is_correct_profile(self):
        president = make_user(username='president', roles=('ACTIVE', 'EXEC', 'PRESIDENT'))
        vp = make_user(username='vp', roles=('ACTIVE', 'EXEC', 'EXT_VP'))
        response = self.client.get('/executive-board/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([(title, row.pk) for title, row in response.context['exec_board_brothers']],
                         [('President', president.brother_profile.pk), ('External Vice President', vp.brother_profile.pk)])


PROBES = {
 'ph_sort': ('PHILANTHROPY', lambda: rewrite(phviews.philanthropy_dashboard,
     "sorted(brothers_progress, key=lambda x: x['total_hours'], reverse=True)",
     'brothers_progress'), '__main__.SortingWitness'),
 'ph_name': ('PHILANTHROPY', lambda: rewrite(phfuncs.collect_philanthropy_statistics,
     ''''full_name': f"{brother.firstName} {brother.lastName}",''',
     "'full_name': '',"), '__main__.NameWitness'),
 'ph_owner': ('PHILANTHROPY', lambda: rewrite(phfuncs.philanthropy_approval_POST,
     'event.save()', 'event.user = request.user\n                event.save()'), None),
 'home_board': ('HOME', lambda: rewrite(homeviews.executive_board,
     'Brother_Profile.objects.filter(roles=role)',
     "Brother_Profile.objects.filter(roles=role if role_code != 'EXT_VP' else Role.objects.get(name='PRESIDENT'))"),
     '__main__.BoardWitness'),
 'home_media': ('HOME', lambda: rewrite(seed.seed_home,
     'shutil.copyfile(source, media / "rush_slides/demo-slide.webp")', 'pass  # dropped second media copy'), None),
 'misc_filter': ('MISC', lambda: rewrite(authviews.dashboard,
     'AnnouncementAlert.objects.filter(is_active=True)', 'AnnouncementAlert.objects.all()'), None),
 'misc_audit': ('MISC', lambda: patch.object(admin.site._registry[AnnouncementAlert], 'log_change', lambda *a, **k: None), None),
}


def run(labels, logfile):
    stream = io.StringIO()
    runner = DiscoverRunner(verbosity=1, interactive=False)
    result_info = {}
    original = runner.run_suite
    def collect(suite, **kwargs):
        result = original(suite, **kwargs)
        result_info.update(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                           skipped=len(result.skipped),
                           failure_ids=[test.id() for test, _ in result.failures],
                           error_ids=[test.id() for test, _ in result.errors])
        return result
    runner.run_suite = collect
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        result_info['exit'] = runner.run_tests(labels)
    logfile.write_text(stream.getvalue())
    return result_info


def main():
    key = sys.argv[1]
    domain, mutation, witness = PROBES[key]
    destination = ROOT / 'work/adversarial_hours'
    destination.mkdir(parents=True, exist_ok=True)
    report = {'probe': key, 'domain': domain, 'settings': os.environ['DJANGO_SETTINGS_MODULE']}
    labels = [domain + '.test']
    report['baseline'] = run(labels, destination / (key + '-baseline.log'))
    if witness:
        report['witness_baseline'] = run([witness], destination / (key + '-witness-baseline.log'))
    with mutation():
        report['mutant'] = run(labels, destination / (key + '-mutant.log'))
        if witness:
            report['witness_mutant'] = run([witness], destination / (key + '-witness-mutant.log'))
    report['restored'] = run(labels + ([witness] if witness else []), destination / (key + '-restored.log'))
    (destination / (key + '.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
