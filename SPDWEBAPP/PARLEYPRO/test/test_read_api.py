"""Aggregate read adapters preserve current-store scope and saved closed-motion counts."""
from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from AUTHENTICATE.models import Brother_Profile, Role
from PARLEYPRO.models import Brother_votes, Vote_Poll


class DecisionsReadApiTests(TestCase):
    def member(self, username, *roles):
        user = User.objects.create(username=username)
        profile = Brother_Profile.objects.create(user=user, firstName='Alex', lastName='Example')
        for code in roles:
            profile.roles.add(Role.objects.get_or_create(name=code)[0])
        return user, profile

    def setUp(self):
        self.user, self.profile = self.member('active', 'ACTIVE')

    def poll(self, name, closed=False, aye=0, nay=0):
        return Vote_Poll.objects.create(Vote_Poll_Name=name, created_by=self.user,
            Vote_Poll_End=timezone.now() if closed else None,
            Vote_Poll_Count_Yes=aye, Vote_Poll_Count_No=nay)

    def test_anonymous_wrong_roles_and_missing_profile_are_denied(self):
        self.poll('Protected motion')
        self.assertEqual(self.client.get('/api/v1/polls/').status_code, 403)
        for username, roles in [('alumni', ('ALUMNI',)), ('exec-only', ('EXEC',))]:
            self.client.force_login(self.member(username, *roles)[0])
            response = self.client.get('/api/v1/polls/')
            self.assertEqual(response.status_code, 403)
            self.assertNotIn('Protected motion', response.content.decode())
        self.client.force_login(User.objects.create(username='missing'))
        self.assertEqual(self.client.get('/api/v1/polls/').status_code, 403)

    def test_newest_current_motion_uses_global_vote_store_without_voter_identities(self):
        self.client.force_login(self.user)
        self.poll('Older open')
        current = self.poll('Newest open', aye=99, nay=99)
        other, _ = self.member('other-voter', 'ALUMNI')
        Brother_votes.objects.create(user=self.user, user_vote_choice='Aye')
        Brother_votes.objects.create(user=other, user_vote_choice='Nay')
        response = self.client.get('/api/v1/polls/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        data = response.json()
        self.assertEqual(data['current']['id'], current.pk)
        self.assertEqual((data['current']['aye'], data['current']['nay']), (1, 1))
        self.assertEqual(set(data['current']), {'id', 'title', 'started_at', 'ended_at', 'aye', 'nay'})
        self.assertNotIn('other-voter', str(data))
        self.assertNotIn('user_vote_choice', str(data))

    def test_closed_order_and_stored_tallies_are_independent_of_current_store(self):
        self.client.force_login(self.user)
        older = self.poll('Older closed', closed=True, aye=4, nay=2)
        latest = self.poll('Newest closed', closed=True, aye=8, nay=1)
        Vote_Poll.objects.filter(pk=older.pk).update(Vote_Poll_End=timezone.now() - timedelta(days=2))
        Brother_votes.objects.create(user=self.user, user_vote_choice='Nay')
        data = self.client.get('/api/v1/polls/').json()
        self.assertIsNone(data['current'])
        self.assertEqual([motion['id'] for motion in data['closed']], [latest.pk, older.pk])
        self.assertEqual([(motion['aye'], motion['nay']) for motion in data['closed']], [(8, 1), (4, 2)])

    def test_empty_current_and_zero_vote_contracts(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/api/v1/polls/').json(), {'current': None, 'closed': [], 'can_manage': False})
        self.poll('No votes yet')
        data = self.client.get('/api/v1/polls/').json()
        self.assertEqual((data['current']['aye'], data['current']['nay']), (0, 0))

    def test_management_capability_requires_exec_and_active(self):
        self.client.force_login(self.user)
        self.assertFalse(self.client.get('/api/v1/polls/').json()['can_manage'])
        self.profile.roles.add(Role.objects.get_or_create(name='EXEC')[0])
        self.assertTrue(self.client.get('/api/v1/polls/').json()['can_manage'])
        self.profile.roles.remove(Role.objects.get(name='ACTIVE'))
        self.assertEqual(self.client.get('/api/v1/polls/').status_code, 403)

    def test_read_adapter_never_accepts_ballots(self):
        self.client.force_login(self.user)
        current = self.poll('Open motion')
        self.assertEqual(self.client.post('/api/v1/polls/', {'aye': 1}).status_code, 405)
        self.assertFalse(Brother_votes.objects.exists())
        current.refresh_from_db()
        self.assertIsNone(current.Vote_Poll_End)
