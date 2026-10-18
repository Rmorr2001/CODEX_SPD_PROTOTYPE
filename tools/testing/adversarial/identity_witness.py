"""Show real business differences on fresh synthetic distinguishing fixtures."""
import ast
from contextlib import contextmanager
import inspect
import importlib
import json
from pathlib import Path
import sys
from identity_probe import ROOT, PROBES
from django.test import TestCase
from django.test.runner import DiscoverRunner
from django.test.utils import setup_test_environment, teardown_test_environment
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import login_actor
from AUTHENTICATE.models import Brother_Profile
from PARLEYPRO.models import Vote_Poll, Brother_votes
from NEWMEMBER.models import NewMember_Mark_Event_and_Request as Mark
from NEWMEMBER import views_functions as nm

@contextmanager
def mutation(name):
    _, module, name_, old, new = PROBES[name]
    f = inspect.unwrap(getattr(importlib.import_module(module), name_))
    tree = ast.parse(inspect.getsource(f).replace(old, new))
    tree.body[0].decorator_list = []
    scope = {}
    exec(compile(tree, '<demonstrator>', 'exec'), f.__globals__, scope)
    original = f.__code__
    try:
        f.__code__ = scope[name_].__code__
        yield
    finally:
        f.__code__ = original

class Demonstration(TestCase):
    def test_differences(self):
        a = make_user(username='synthetic-closer', roles=('ACTIVE', 'EXEC'),
                      profile_fields={'firstName': 'Alex', 'lastName': 'Able', 'pclass': 'Beta'})
        b = make_user(username='synthetic-creator', roles=('ACTIVE',))
        login_actor(self.client, a)
        payload = dict(username=a.username, email='a@example.invalid', firstName='Alex',
                       lastName='Able', hometown='Demo Town', pclass='Alpha')
        def profile_value():
            response = self.client.post('/auth/update_profile/', payload)
            return dict(response=response.json(), pclass=Brother_Profile.objects.get(user=a).pclass)
        clean = profile_value()
        Brother_Profile.objects.filter(user=a).update(pclass='Beta')
        with mutation('auth_pclass'):
            mutant = profile_value()
        assert clean['pclass'] == 'Alpha' and mutant['pclass'] == 'Beta'
        evidence['auth_pclass'] = dict(initial='Beta', submitted='Alpha', clean=clean, mutant=mutant)
        poll = Vote_Poll.objects.create(created_by=b, Vote_Poll_Name='Ownership sentinel')
        Brother_votes.objects.create(user=a, user_vote_choice='Aye')
        Brother_votes.objects.create(user=b, user_vote_choice='Aye')
        c = make_user(username='synthetic-nay', roles=('ACTIVE',))
        Brother_votes.objects.create(user=c, user_vote_choice='Nay')
        def page_counts():
            r = self.client.get('/poll/')
            return dict(aye=r.context['aye_votes'], nay=r.context['nay_votes'], status=r.status_code)
        clean = page_counts()
        with mutation('pp_page_swapped'):
            mutant = page_counts()
        assert clean == {'aye':2,'nay':1,'status':200} and mutant == {'aye':1,'nay':2,'status':200}
        evidence['pp_page_swapped'] = dict(clean=clean, mutant=mutant)
        original_name = poll.created_by.username
        self.client.post('/poll/', {'end_vote': '1'})
        poll.refresh_from_db()
        clean_creator = poll.created_by.username
        Vote_Poll.objects.filter(pk=poll.pk).update(Vote_Poll_End=None, created_by=b)
        with mutation('pp_closer_creator'):
            self.client.post('/poll/', {'end_vote': '1'})
        poll.refresh_from_db()
        assert clean_creator == original_name and poll.created_by_id == a.pk
        evidence['pp_closer_creator'] = dict(original_creator=original_name, closer=a.username,
                        clean_creator=clean_creator, mutant_creator=poll.created_by.username,
                        scope='POLICY_BLOCKED PP-16c: not a READY failure')
        t1 = make_user(username='synthetic-first', roles=('NEW_MEMBER',),
                       profile_fields={'firstName':'Tess', 'lastName':'Able'})
        t2 = make_user(username='synthetic-second', roles=('NEW_MEMBER',))
        Mark.objects.create(requesting_user=a, target_user=t1, mark_event_title='Fraction',
                    mark_value=1, mark_event_date='2026-10-16', mark_approval_status='approved')
        clean = nm.get_personal_stats(t1)['class_average']
        with mutation('nm_fraction'):
            mutant = nm.get_personal_stats(t1)['class_average']
        assert clean == .5 and mutant == 0
        evidence['nm_fraction'] = dict(member_totals=[1,0], clean=clean, mutant=mutant)
        def full_name():
            return nm.calculate_member_marks([t1.brother_profile])[0]['full_name']
        clean = full_name()
        with mutation('nm_display_name'):
            mutant = full_name()
        assert clean == 'Tess Able' and mutant == 'Tess'
        evidence['nm_display_name'] = dict(clean=clean, mutant=mutant)

(ROOT / "work/adversarial_identity").mkdir(parents=True, exist_ok=True)
evidence = {}
runner = DiscoverRunner(verbosity=2, interactive=False)
result = runner.run_tests(['__main__.Demonstration'])
assert result == 0
(ROOT/'work/adversarial_identity/demonstration.json').write_text(json.dumps(evidence,indent=2)+'\n')
print(json.dumps(evidence,indent=2))
