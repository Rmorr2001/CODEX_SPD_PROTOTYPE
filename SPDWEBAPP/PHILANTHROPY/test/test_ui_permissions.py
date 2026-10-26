"""Review affordances use server-authorized pending/non-self availability."""
from django.test import Client
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from PHILANTHROPY.models import Philanthropy_Hours_Event_and_Request as Event
from PHILANTHROPY.operations import decision_is_available, submit_event


class ReviewUiPermissionsTests(RegressionTestCase):
    def setUp(self):
        super().setUp()
        self.chair = make_user(username='chair-ui', roles=('ACTIVE', 'PHIL_CHAIR'))
        self.member = make_user(username='member-ui', roles=('ACTIVE',))
        data = {'event_title': 'Own request', 'hours': '0.5', 'event_date': '2026-10-26'}
        self.own = submit_event(self.chair, data)
        self.other = submit_event(self.member, {**data, 'event_title': 'Member request'})
        self.client.force_login(self.chair)

    def test_api_queue_cannot_offer_self_review_but_keeps_eligible_requests(self):
        response = self.client.get('/api/v1/service/review/')
        self.assertEqual(response.status_code, 200)
        available = {row['id']: row['can_decide'] for row in response.json()}
        self.assertEqual(available, {self.own.pk: False, self.other.pk: True})
        self.assertFalse(decision_is_available(self.chair.pk, self.own))
        self.assertTrue(decision_is_available(self.chair.pk, self.other))
        for action in ('approve', 'deny'):
            response = self.client.post(f'/api/v1/service/{self.own.pk}/decision/', {'action': action})
            self.assertEqual(response.status_code, 409)
        self.own.refresh_from_db()
        self.assertEqual(self.own.philanthropy_approval_status, 'requested')
        self.assertIsNone(self.own.philanthropy_event_submission_approval_date)

    def test_html_queue_hides_own_decisions_and_backend_still_rejects_forgery(self):
        response = self.client.get('/philanthropy/approve/')
        self.assertContains(response, 'Another chair must review.', count=1)
        self.assertContains(response, 'value="approve"', count=1)
        self.assertContains(response, 'value="deny"', count=1)
        events = {row.pk: row.can_decide for row in response.context['pending_requests']}
        self.assertEqual(events, {self.own.pk: False, self.other.pk: True})
        before = list(Event.objects.order_by('pk').values())
        self.client.post('/philanthropy/approve/', {'event_id': self.own.pk, 'action': 'approve', 'can_decide': 'true'})
        self.assertEqual(list(Event.objects.order_by('pk').values()), before)

    def test_nonchair_cannot_read_review_capabilities_and_closed_request_is_not_decidable(self):
        self.client.force_login(self.member)
        self.assertEqual(self.client.get('/api/v1/service/review/').status_code, 403)
        self.other.philanthropy_approval_status = 'approved'
        self.assertFalse(decision_is_available(self.chair.pk, self.other))
