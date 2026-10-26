"""Same-poll API/HTML compatibility and denied/failed transition preservation."""
import json
from unittest.mock import patch
from django.core.exceptions import PermissionDenied
from django.db import OperationalError
from django.test import Client
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from PARLEYPRO.models import Brother_votes, Vote_Poll
from PARLEYPRO.operations import close_poll


class PollTransactionTests(RegressionTestCase):
    def setUp(self):
        super().setUp()
        self.executive = make_user(username='executive', roles=('ACTIVE', 'EXEC'))
        self.member = make_user(username='member', roles=('ACTIVE',))
        self.other = make_user(username='other', roles=('ACTIVE',))
        self.client.force_login(self.executive)

    def send(self, path, data=None, method='post', client=None):
        return getattr(client or self.client, method)(path, json.dumps(data or {}), content_type='application/json')

    def open(self):
        response = self.send('/api/v1/polls/', {'title': 'Shared fictional motion'})
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()['id']

    def test_api_create_legacy_vote_api_change_legacy_close_preserves_same_poll(self):
        pk = self.open()
        self.assertContains(self.client.get('/poll/'), 'Shared fictional motion')
        self.client.force_login(self.member)
        self.assertEqual(self.client.post('/poll/', {'aye': '1'}).status_code, 200)
        choice = Brother_votes.objects.get(user=self.member)
        self.assertEqual(self.client.get('/api/v1/polls/').json()['own_choice'], 'Aye')
        self.assertEqual(self.send(f'/api/v1/polls/{pk}/vote/', {'choice': 'Nay'}, 'put').status_code, 200)
        choice.refresh_from_db()
        self.assertEqual(choice.user_vote_choice, 'Nay')
        self.assertEqual(self.client.get('/poll/').context['nay_votes'], 1)
        self.client.force_login(self.executive)
        self.assertEqual(self.client.post('/poll/', {'end_vote': '1'}).status_code, 200)
        detail = self.client.get(f'/api/v1/polls/{pk}/').json()
        self.assertEqual((detail['aye'], detail['nay']), (0, 1))
        self.assertIsNotNone(detail['ended_at'])
        self.assertEqual(Brother_votes.objects.get(pk=choice.pk).user_vote_choice, 'No Vote')

    def test_legacy_create_api_close_legacy_saved_results(self):
        response = self.client.post('/poll/start_vote/', {'Vote_Poll_Name': 'Legacy-created motion'})
        self.assertEqual(response.status_code, 302)
        pk = Vote_Poll.objects.get().pk
        self.send(f'/api/v1/polls/{pk}/vote/', {'choice': 'Aye'}, 'put')
        self.assertEqual(self.send(f'/api/v1/polls/{pk}/close/').status_code, 200)
        self.assertContains(self.client.get('/poll/past_polls/'), 'Legacy-created motion')
        self.assertEqual(Vote_Poll.objects.get(pk=pk).Vote_Poll_Count_Yes, 1)

    def test_member_cannot_close_through_api_html_or_shared_operation(self):
        pk = self.open()
        self.client.force_login(self.member)
        self.send(f'/api/v1/polls/{pk}/vote/', {'choice': 'Aye'}, 'put')
        self.assertEqual(self.send(f'/api/v1/polls/{pk}/close/').status_code, 403)
        self.assertEqual(self.client.post('/poll/', {'end_vote': '1'}).status_code, 403)
        with self.assertRaises(PermissionDenied):
            close_poll(self.member, pk)
        self.assertIsNone(Vote_Poll.objects.get(pk=pk).Vote_Poll_End)
        self.assertEqual(Brother_votes.objects.get(user=self.member).user_vote_choice, 'Aye')

    def test_single_open_creation_and_closed_target_are_conflicts(self):
        pk = self.open()
        self.assertEqual(self.send('/api/v1/polls/', {'title': 'Overlapping'}).status_code, 409)
        self.assertEqual(Vote_Poll.objects.count(), 1)
        self.send(f'/api/v1/polls/{pk}/close/')
        self.assertEqual(self.send(f'/api/v1/polls/{pk}/vote/', {'choice': 'Aye'}, 'put').status_code, 409)
        self.assertFalse(Brother_votes.objects.exists())
        next_pk = self.open()
        self.send(f'/api/v1/polls/{next_pk}/vote/', {'choice': 'Nay'}, 'put')
        self.assertEqual(self.send(f'/api/v1/polls/{pk}/close/').status_code, 200)
        self.assertEqual(Brother_votes.objects.get(user=self.executive).user_vote_choice, 'Nay')
        self.assertIsNone(Vote_Poll.objects.get(pk=next_pk).Vote_Poll_End)

    def test_ballot_is_owned_by_session_and_repeat_is_idempotent(self):
        pk = self.open()
        self.client.force_login(self.member)
        for _ in range(2):
            self.assertEqual(self.send(f'/api/v1/polls/{pk}/vote/', {'choice': 'Aye', 'user_id': self.other.pk}, 'put').status_code, 200)
        self.assertEqual(list(Brother_votes.objects.values_list('user_id', 'user_vote_choice')), [(self.member.pk, 'Aye')])

    def test_invalid_actions_and_malformed_json_do_not_write(self):
        pk = self.open()
        for data in ({}, {'choice': 'Yes'}, [], {'choice': '<script>'}):
            with self.subTest(data=data):
                self.assertEqual(self.send(f'/api/v1/polls/{pk}/vote/', data, 'put').status_code, 400)
        self.assertEqual(self.client.post('/api/v1/polls/', '{', content_type='application/json').status_code, 400)
        self.client.post('/poll/', {'aye': 1, 'nay': 1})
        self.assertFalse(Brother_votes.objects.exists())

    def test_real_csrf_required_for_every_write_route(self):
        pk = self.open()
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.executive)
        for path, method, data in [('/api/v1/polls/', 'post', {'title': 'Other'}),
                (f'/api/v1/polls/{pk}/vote/', 'put', {'choice': 'Aye'}),
                (f'/api/v1/polls/{pk}/close/', 'post', {})]:
            self.assertEqual(self.send(path, data, method, client).status_code, 403)
        client.get('/api/v1/session/')
        response = client.put(f'/api/v1/polls/{pk}/vote/', json.dumps({'choice': 'Aye'}),
            content_type='application/json', HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertEqual(response.status_code, 200)

    def test_failed_reset_rolls_back_saved_close_and_keeps_ballots(self):
        pk = self.open()
        self.send(f'/api/v1/polls/{pk}/vote/', {'choice': 'Nay'}, 'put')
        from django.db.models.query import QuerySet
        original = QuerySet.update
        def fail_reset(queryset, **values):
            if queryset.model is Brother_votes:
                raise OperationalError('synthetic reset failure')
            return original(queryset, **values)
        with patch.object(QuerySet, 'update', fail_reset):
            response = self.send(f'/api/v1/polls/{pk}/close/')
        self.assertEqual(response.status_code, 409)
        self.assertNotIn('synthetic', response.content.decode())
        self.assertIsNone(Vote_Poll.objects.get(pk=pk).Vote_Poll_End)
        self.assertEqual(Brother_votes.objects.get(user=self.executive).user_vote_choice, 'Nay')
