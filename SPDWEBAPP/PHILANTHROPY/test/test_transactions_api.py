"""Real API/HTML transactions, exact fractional projections and protected boundaries."""
import json
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch
from django.db import OperationalError
from django.test import Client
from django.utils import timezone
from openpyxl import load_workbook
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from PHILANTHROPY.models import Philanthropy_Hours_Event_and_Request as Event
from PHILANTHROPY.operations import submit_event


class ServiceTransactionTests(RegressionTestCase):
    def setUp(self):
        super().setUp()
        self.member = make_user(username='member', roles=('ACTIVE',))
        self.chair = make_user(username='chair', roles=('ACTIVE', 'PHIL_CHAIR'))
        self.other = make_user(username='other', roles=('ACTIVE',))
        self.client.force_login(self.member)
        today = timezone.localdate()
        self.year = today.year - (today.month <= 6)
        self.payload = {'event_title': 'Fictional cleanup', 'hours': '1.75', 'event_date': today.isoformat()}

    def send(self, path, data, method='post', client=None):
        return getattr(client or self.client, method)(path, json.dumps(data), content_type='application/json')

    def create(self):
        response = self.send('/api/v1/service/', self.payload)
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()['id']

    def test_react_submit_legacy_approve_updates_both_interfaces_and_xlsx(self):
        pk = self.create()
        event = Event.objects.get(pk=pk)
        self.assertEqual(event.philanthropy_event_hours, Decimal('1.75'))
        self.assertEqual(event.user_id, self.member.pk)
        self.assertEqual(self.client.get('/philanthropy/', {'year': self.year}).context['user_total_hours'], 0)
        self.client.force_login(self.chair)
        self.assertContains(self.client.get('/philanthropy/approve/'), 'Fictional cleanup')
        self.assertEqual(self.client.post('/philanthropy/approve/', {'event_id': pk, 'action': 'approve'}).status_code, 200)
        self.client.force_login(self.member)
        data = self.client.get(f'/api/v1/service/?year={self.year}').json()
        self.assertEqual((data['approved_hours'], data['events'][0]['status']), (1.75, 'approved'))
        self.assertEqual(self.client.get('/philanthropy/', {'year': self.year}).context['user_total_hours'], Decimal('1.75'))
        history = self.client.get('/api/v1/service/history/').json()
        self.assertEqual(history['approved_hours'], 1.75)
        chapter = self.client.get(f'/api/v1/service/chapter/?year={self.year}').json()
        self.assertEqual(chapter['approved_hours'], 1.75)
        response = self.client.get('/api/v1/service/export/')
        wb = load_workbook(BytesIO(response.content), data_only=False)
        self.addCleanup(wb.close)
        cells = [cell for row in wb.active for cell in row]
        self.assertTrue(any(c.value == 1.75 and c.data_type == 'n' for c in cells))
        self.assertTrue(any(c.value == 'Total: 1.75' for c in cells))

    def test_legacy_submit_api_deny_is_visible_without_approved_hours(self):
        self.assertEqual(self.client.post('/philanthropy/request/', self.payload).status_code, 302)
        event = Event.objects.get()
        self.client.force_login(self.chair)
        queue = self.client.get('/api/v1/service/review/').json()
        self.assertEqual(queue[0]['id'], event.pk)
        self.assertEqual(self.send(f'/api/v1/service/{event.pk}/decision/', {'action': 'deny'}).status_code, 200)
        self.client.force_login(self.member)
        data = self.client.get(f'/api/v1/service/?year={self.year}').json()
        self.assertEqual((data['events'][0]['status'], data['approved_hours']), ('denied', 0))
        self.assertEqual(list(self.client.get('/philanthropy/', {'year': self.year}).context['user_events'])[0].philanthropy_approval_status, 'denied')

    def test_api_chair_edit_and_legacy_edit_use_same_fractional_validation(self):
        pk = self.create()
        self.client.force_login(self.chair)
        edited = {**self.payload, 'hours': '2.25', 'event_title': 'Edited in React'}
        self.assertEqual(self.send(f'/api/v1/service/{pk}/', edited, 'patch').status_code, 200)
        self.assertContains(self.client.get(f'/philanthropy/edit/{pk}/'), 'Edited in React')
        legacy = {**edited, 'hours': '3.50'}
        self.assertEqual(self.client.post(f'/philanthropy/edit/{pk}/', legacy).status_code, 302)
        row = self.client.get(f'/api/v1/service/{pk}/').json()
        self.assertEqual((row['hours'], row['status']), (3.5, 'requested'))
        event = Event.objects.get(pk=pk)
        self.assertEqual(event.last_edited_by_id, self.chair.pk)
        self.assertIsNotNone(event.last_edited_at)

    def test_forged_owner_status_and_audit_cannot_bypass_pending_submission(self):
        response = self.send('/api/v1/service/', {**self.payload, 'user_id': self.other.pk,
            'philanthropy_approval_status': 'approved', 'last_edited_by': self.chair.pk})
        self.assertEqual(response.status_code, 201)
        event = Event.objects.get()
        self.assertEqual((event.user_id, event.philanthropy_approval_status), (self.member.pk, 'requested'))
        self.assertIsNone(event.last_edited_by_id)
        self.assertIsNone(event.philanthropy_event_submission_approval_date)

    def test_invalid_inputs_reject_before_any_insert_or_edit(self):
        for changes in ({'hours': '0.49'}, {'hours': 'NaN'}, {'hours': 'Infinity'},
                        {'hours': '1.755'}, {'event_date': '2026-02-30'}, {'event_title': 'x' * 101},
                        {'event_title': ''}):
            with self.subTest(changes=changes):
                self.assertEqual(self.send('/api/v1/service/', {**self.payload, **changes}).status_code, 400)
        self.assertEqual(self.send('/api/v1/service/', []).status_code, 400)
        self.assertFalse(Event.objects.exists())
        pk = self.create()
        self.client.force_login(self.chair)
        self.assertEqual(self.send(f'/api/v1/service/{pk}/', {**self.payload, 'hours': '1.755'}, 'patch').status_code, 400)
        self.assertEqual(Event.objects.get(pk=pk).philanthropy_event_hours, Decimal('1.75'))

    def test_decision_and_edit_permissions_enforced_before_writes(self):
        pk = self.create()
        self.assertEqual(self.client.get('/api/v1/service/review/').status_code, 403)
        self.assertEqual(self.send(f'/api/v1/service/{pk}/decision/', {'action': 'approve'}).status_code, 403)
        self.assertEqual(self.send(f'/api/v1/service/{pk}/', self.payload, 'patch').status_code, 403)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/api/v1/service/{pk}/').status_code, 403)
        self.client.logout()
        self.assertEqual(self.send('/api/v1/service/', self.payload).status_code, 403)
        self.assertEqual(self.client.get('/api/v1/service/export/').status_code, 403)
        self.assertEqual(Event.objects.get(pk=pk).philanthropy_approval_status, 'requested')

    def test_unresolved_self_review_reversal_and_unknown_actions_fail_closed(self):
        pk = self.create()
        self.client.force_login(self.chair)
        for action in ('unknown', ''):
            self.assertEqual(self.send(f'/api/v1/service/{pk}/decision/', {'action': action}).status_code, 400)
        self.assertEqual(self.send(f'/api/v1/service/{pk}/decision/', {'action': 'approve'}).status_code, 200)
        audit = Event.objects.get(pk=pk).philanthropy_event_submission_approval_date
        self.assertEqual(self.send(f'/api/v1/service/{pk}/decision/', {'action': 'deny'}).status_code, 409)
        self.assertEqual(Event.objects.get(pk=pk).philanthropy_event_submission_approval_date, audit)
        own = submit_event(self.chair, self.payload)
        self.assertEqual(self.send(f'/api/v1/service/{own.pk}/decision/', {'action': 'approve'}).status_code, 409)
        self.assertEqual(Event.objects.get(pk=own.pk).philanthropy_approval_status, 'requested')

    def test_csrf_denies_all_mutations_and_real_token_allows_submission(self):
        pk = self.create()
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.chair)
        for path, method, data in [('/api/v1/service/', 'post', self.payload),
            (f'/api/v1/service/{pk}/', 'patch', self.payload),
            (f'/api/v1/service/{pk}/decision/', 'post', {'action': 'approve'})]:
            self.assertEqual(self.send(path, data, method, client).status_code, 403)
        client.get('/api/v1/session/')
        response = client.post('/api/v1/service/', json.dumps(self.payload), content_type='application/json',
            HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertEqual(response.status_code, 201)

    def test_failed_update_does_not_change_pending_event_or_leak_database_error(self):
        pk = self.create()
        self.client.force_login(self.chair)
        from django.db.models.query import QuerySet
        with patch.object(QuerySet, 'update', side_effect=OperationalError('synthetic private failure')):
            response = self.send(f'/api/v1/service/{pk}/decision/', {'action': 'approve'})
        self.assertEqual(response.status_code, 409)
        self.assertNotIn('synthetic', response.content.decode())
        event = Event.objects.get(pk=pk)
        self.assertEqual(event.philanthropy_approval_status, 'requested')
        self.assertIsNone(event.philanthropy_event_submission_approval_date)

    def test_half_hour_survives_storage_without_rounding_or_truncation(self):
        event = submit_event(self.member, {**self.payload, 'hours': '0.50'})
        event.refresh_from_db()
        self.assertEqual(event.philanthropy_event_hours, Decimal('0.50'))

    def test_legacy_self_review_and_reversal_leave_all_events_and_audit_unchanged(self):
        from django.contrib.messages import get_messages
        pending = submit_event(self.chair, self.payload)
        reviewed = submit_event(self.member, {**self.payload, 'event_title': 'Reviewed sentinel'})
        self.client.force_login(self.chair)
        self.assertEqual(self.send(f'/api/v1/service/{reviewed.pk}/decision/', {'action': 'approve'}).status_code, 200)
        before = list(Event.objects.order_by('pk').values())
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.chair)
        client.get('/philanthropy/approve/')
        token = client.cookies['csrftoken'].value
        for event, action in [(pending, 'approve'), (pending, 'deny'),
                              (reviewed, 'deny'), (reviewed, 'approve')]:
            with self.subTest(event=event.pk, action=action):
                response = client.post('/philanthropy/approve/',
                    {'event_id': event.pk, 'action': action, 'csrfmiddlewaretoken': token})
                self.assertEqual(response.status_code, 200)
                messages = [str(message) for message in get_messages(response.wsgi_request)]
                self.assertTrue(any('review conflict' in message for message in messages))
                self.assertFalse(any('successfully' in message for message in messages))
                self.assertEqual(list(Event.objects.order_by('pk').values()), before)
