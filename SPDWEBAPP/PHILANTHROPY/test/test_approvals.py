from datetime import date
from unittest.mock import patch

from django.contrib.admin.models import LogEntry
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from PHILANTHROPY.views_functions import (get_user_events_and_total_hours,
                                         philanthropy_approval_POST)
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import at_time, csrf_client, login_actor

from .support import (APPROVE, DASHBOARD, T1, Event, PhilanthropyCase,
                      history, make_event, messages)


class ApprovalTests(PhilanthropyCase):
    def setUp(self):
        super().setUp()
        self.b = make_user(username='b', roles=('ACTIVE',))
        self.c = make_user(username='chair', roles=('ACTIVE', 'PHIL_CHAIR'),
                           profile_fields={'firstName': 'Casey', 'lastName': 'Chair'})
        self.e = make_event(self.b, title='Pending service')
        self.f = make_event(self.b, title='Control approved', hours=7, status='approved')
        login_actor(self.client, self.c)

    def test_pending_list_contains_only_requested_rows_by_date(self):
        a = make_user(username='a', roles=('ACTIVE',))
        earlier = make_event(a, title='Earlier service', day=date(2026, 7, 1))
        self.e.philanthropy_event_date = date(2026, 7, 2)
        self.e.save()
        denied = make_event(self.b, title='Control denied', status='denied')
        before = self.capture(a, self.b, self.c, self.e, self.f, earlier, denied)
        response = self.client.get(APPROVE)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['pending_requests']), [self.e, earlier])
        for event in (self.e, earlier):
            self.assertContains(response, event.philanthropy_event_title)
            self.assertContains(response, event.user.brother_profile.firstName)
        self.assertNotContains(response, 'Control approved')
        self.assertNotContains(response, 'Control denied')
        self.unchanged(before)
        self.assertEqual(Event.objects.count(), 4)

    def decision(self, action, expected_status, expected_message):
        client = csrf_client()
        login_actor(client, self.c)
        token = self.token(client, APPROVE)
        before = self.capture(self.b, self.c, self.f)
        original = Event.objects.values().get(pk=self.e.pk)
        log_count = LogEntry.objects.count()
        with at_time(T1):
            response = client.post(APPROVE, {'event_id': self.e.pk, 'action': action,
                                             'csrfmiddlewaretoken': token})
        self.assertEqual(response.status_code, 200)
        self.assertIn(expected_message, messages(response))
        self.assertNotIn(self.e, response.context['pending_requests'])
        current = Event.objects.values().get(pk=self.e.pk)
        changed = {'philanthropy_approval_status', 'philanthropy_event_approver_name',
                   'philanthropy_event_submission_approval_date'}
        self.assertEqual(current['philanthropy_approval_status'], expected_status)
        self.assertEqual(current['philanthropy_event_approver_name'], 'Casey Chair')
        self.assertEqual(current['philanthropy_event_submission_approval_date'], T1)
        for field in original.keys() - changed:
            self.assertEqual(current[field], original[field], field)
        self.unchanged(before)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(LogEntry.objects.count(), log_count)
        self.assert_session_actor(client, self.c)

    def test_initial_approval_updates_only_decision_fields(self):
        self.decision('approve', 'approved', 'Event successfully approved!')

    def test_initial_denial_updates_only_decision_fields(self):
        self.decision('deny', 'denied', 'Event successfully denied!')

    def test_denied_event_remains_personal_but_not_approved_history(self):
        self.e.philanthropy_approval_status = 'denied'
        self.e.save()
        self.f.philanthropy_event_hours = 3
        self.f.save()
        a = make_user(username='a', roles=('ACTIVE',))
        other = make_event(a, title='Other owner', hours=7, status='approved')
        login_actor(self.client, self.b)
        before = self.capture(a, self.b, self.c, self.e, self.f, other)
        dashboard = self.client.get(DASHBOARD, {'year': '2026'})
        self.assertEqual(dashboard.status_code, 200)
        self.assertCountEqual(dashboard.context['user_events'], [self.e, self.f])
        self.assertEqual(dashboard.context['user_total_hours'], 3)
        self.assertEqual(dashboard.context['total_chapter_hours'], 10)
        response = self.client.get(history(self.b))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['lifetime_total'], 3)
        self.assertEqual(response.context['academic_year_totals'][0]['events'], [self.f])
        request = RequestFactory().get(DASHBOARD)
        request.user = self.b
        events, total = get_user_events_and_total_hours(
            request, date(2026, 7, 1), date(2027, 6, 30))
        self.assertCountEqual(events, [self.e, self.f])
        self.assertEqual(total, 3)
        self.unchanged(before)

    def test_bad_decision_event_ids_report_error_without_write(self):
        before = self.capture(self.b, self.c, self.e, self.f)
        for action in ('approve', 'deny'):
            for event_id in (None, '', 'abc', '999999'):
                with self.subTest(action=action, event_id=event_id):
                    data = {'action': action}
                    if event_id is not None:
                        data['event_id'] = event_id
                    response = self.client.post(APPROVE, data)
                    self.assertEqual(response.status_code, 200)
                    text = messages(response)
                    self.assertTrue(any('not found' in m or 'Error processing request:' in m
                                        for m in text))
                    self.assertFalse(any('successfully' in m for m in text))
                    if event_id == '999999':
                        self.assertIn('Event not found', text)
                    self.assertEqual(list(response.context['pending_requests']), [self.e])
                    self.unchanged(before)
                    self.assertEqual(Event.objects.count(), 2)

    def test_decision_helper_nonpost_is_noop(self):
        request = RequestFactory().get(APPROVE, {'event_id': self.e.pk, 'action': 'approve'})
        request.user = self.c
        request.session = {}
        request._messages = FallbackStorage(request)
        before = self.capture(self.b, self.c, self.e, self.f)
        self.assertIsNone(philanthropy_approval_POST(request))
        self.assertEqual(list(request._messages), [])
        self.unchanged(before)
        self.assertEqual(Event.objects.count(), 2)

    def test_decision_prewrite_save_failure_preserves_request(self):
        before = self.capture(self.b, self.c, self.e, self.f)
        for action in ('approve', 'deny'):
            with self.subTest(action=action):
                with patch.object(Event, 'save', side_effect=RuntimeError('synthetic')):
                    response = self.client.post(APPROVE, {'event_id': self.e.pk,
                                                          'action': action})
                self.assertEqual(response.status_code, 200)
                text = messages(response)
                self.assertTrue(any('Error processing request:' in m for m in text))
                self.assertFalse(any('successfully' in m for m in text))
                self.assertEqual(list(response.context['pending_requests']), [self.e])
                self.unchanged(before)
                self.assertEqual(Event.objects.count(), 2)
