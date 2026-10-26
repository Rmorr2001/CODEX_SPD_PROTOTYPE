from unittest.mock import patch

from django.test import TransactionTestCase
from django.utils.html import escape

from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import at_time, csrf_client, login_actor, temporary_media

from .support import (DASHBOARD, SUBMIT, T1, Event, PhilanthropyCase,
                      PhilanthropyAssertions, make_event, messages, payload)


class RequestFixtures:
    def setUp(self):
        super().setUp()
        self.a = make_user(username='a', roles=('ACTIVE',))
        self.b = make_user(username='b', roles=('ACTIVE',))
        self.f = make_event(self.b, title='Other', hours=7, status='approved')
        login_actor(self.client, self.a)


    def assert_success(self, response, title='Park', hours=2):
        self.assertRedirects(response, DASHBOARD, fetch_redirect_response=False)
        self.assertIn('Philanthropy hours submitted successfully!', messages(response))
        self.assertEqual(Event.objects.count(), 2)
        event = Event.objects.exclude(pk=self.f.pk).get()
        self.assert_requested(event, self.a, title=title, hours=hours)
        self.assert_session_actor(self.client, self.a)
        return event


    def assert_rejected(self, data):
        before = self.capture(self.a, self.b, self.f)
        response = self.client.post(SUBMIT, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'philanthropy_request.html')
        text = messages(response)
        self.assertTrue(any(message.startswith('Error submitting hours:') for message in text))
        self.assertFalse(any('submitted successfully' in message for message in text))
        self.assertEqual(Event.objects.count(), 1)
        self.assertFalse(Event.objects.filter(user=self.a).exists())
        self.assertEqual(list(self.media_root.rglob('*')), [])
        self.unchanged(before)
        self.assert_session_actor(self.client, self.a)
        return response, text



class RequestTests(RequestFixtures, PhilanthropyCase):
    def test_submission_form_exposes_three_fields(self):
        client = csrf_client()
        login_actor(client, self.a)
        before = self.capture(self.a, self.b, self.f)
        response = client.get(SUBMIT)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'philanthropy_request.html')
        for field in ('event_title', 'hours', 'event_date', 'csrfmiddlewaretoken'):
            self.assertContains(response, f'name="{field}"')
        self.assertContains(response, 'min="0.5"')
        self.assertContains(response, 'step="0.01"')
        self.assertIn('csrftoken', client.cookies)
        self.unchanged(before)
        self.assertEqual(Event.objects.count(), 1)


    def test_integer_submission_persists_exact_values(self):
        client = csrf_client()
        login_actor(client, self.a)
        token = self.token(client, SUBMIT)
        before = self.capture(self.a, self.b, self.f)
        with at_time(T1):
            response = client.post(SUBMIT, payload(event_title='Park cleanup',
                                                   csrfmiddlewaretoken=token))
        event = self.assert_success(response, title='Park cleanup')
        self.assertEqual(event.philanthropy_event_submission_request_date, T1)
        self.unchanged(before)
        self.assert_session_actor(client, self.a)


    def test_submitted_owner_status_and_audit_are_ignored(self):
        before = self.capture(self.a, self.b, self.f)
        data = payload(user=self.b.pk, user_id=self.b.pk, status='approved',
                       philanthropy_approval_status='approved',
                       philanthropy_event_approver_name='Forged', last_edited_by=self.b.pk,
                       last_edited_at='2000-01-01T00:00:00Z',
                       philanthropy_event_submission_request_date='2000-01-01T00:00:00Z',
                       philanthropy_event_submission_approval_date='2000-01-01T00:00:00Z')
        with at_time(T1):
            response = self.client.post(SUBMIT, data)
        event = self.assert_success(response)
        self.assertEqual(event.philanthropy_event_submission_request_date, T1)
        self.unchanged(before)


    def test_submission_rejects_below_minimum_hours(self):
        for value in ('0', '-1', '0.49'):
            with self.subTest(hours=value):
                _, text = self.assert_rejected(payload(hours=value))
                self.assertTrue(any('Must request at least 0.5 hours.' in m for m in text))


    def test_integral_float_string_preserves_integer_hours(self):
        before = self.capture(self.a, self.b, self.f)
        self.assert_success(self.client.post(SUBMIT, payload(hours='2.0')))
        self.unchanged(before)


    def test_submission_parse_errors_leave_no_event(self):
        for value in (None, '', '   ', 'abc'):
            with self.subTest(hours=value):
                data = payload(hours=value)
                if value is None:
                    data.pop('hours')
                self.assert_rejected(data)


    def test_hundred_character_title_round_trips(self):
        before = self.capture(self.a, self.b, self.f)
        self.assert_success(self.client.post(SUBMIT, payload(event_title='x' * 100)),
                            title='x' * 100)
        self.unchanged(before)


    def test_unicode_and_html_title_render_as_text(self):
        title = 'Δ cleanup <script>alert("demo")</script>'
        before = self.capture(self.a, self.b, self.f)
        event = self.assert_success(self.client.post(SUBMIT, payload(event_title=title)),
                                    title=title)
        after_submit = self.capture(event)
        response = self.client.get(DASHBOARD, {'year': '2026'})
        self.assertContains(response, escape(title))
        self.assertNotContains(response, '<script>alert("demo")</script>')
        self.unchanged(after_submit)
        self.unchanged(before)


    def test_submit_prewrite_save_failure_is_reported_without_row(self):
        with patch.object(Event, 'save', side_effect=RuntimeError('synthetic failure')):
            self.assert_rejected(payload())



class AutocommitRequestTests(RequestFixtures, PhilanthropyAssertions, TransactionTestCase):
    """Caught save errors must use real-request autocommit, not TestCase atomicity."""

    def setUp(self):
        self.media_root = self.enterContext(temporary_media())
        super().setUp()

    def test_submission_nonfinite_hours_create_no_record(self):
        for value in ('NaN', 'nan', 'Infinity', '-Infinity', '1e309'):
            with self.subTest(hours=value):
                self.assert_rejected(payload(hours=value))


    def test_missing_submission_keys_and_bad_dates_do_not_write(self):
        for key in ('event_title', 'event_date'):
            with self.subTest(omitted=key):
                data = payload()
                data.pop(key)
                self.assert_rejected(data)
        for value in ('', 'not-a-date', '2026-02-30'):
            with self.subTest(date=value):
                self.assert_rejected(payload(event_date=value))
