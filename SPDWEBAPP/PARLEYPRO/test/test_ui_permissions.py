"""Legacy controls reflect the same authorization as poll commands and REST reads."""
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from PARLEYPRO.models import Vote_Poll
from PARLEYPRO.operations import can_manage_polls


class PollUiPermissionsTests(RegressionTestCase):
    def setUp(self):
        super().setUp()
        self.active = make_user(username='active-ui', roles=('ACTIVE',))
        self.executive = make_user(username='executive-ui', roles=('ACTIVE', 'EXEC'))
        Vote_Poll.objects.create(created_by=self.executive, Vote_Poll_Name='UI permission motion')

    def test_active_has_ballot_without_create_or_close_controls(self):
        self.client.force_login(self.active)
        response = self.client.get('/poll/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['can_manage'])
        self.assertFalse(can_manage_polls(self.active))
        self.assertNotContains(response, 'Start New Vote')
        self.assertNotContains(response, 'End Vote')
        self.assertContains(response, 'name="aye"')
        self.assertContains(response, 'name="nay"')
        self.assertFalse(self.client.get('/api/v1/polls/').json()['can_manage'])
        self.assertEqual(self.client.post('/poll/', {'end_vote': 1}).status_code, 403)
        self.assertIsNone(Vote_Poll.objects.get().Vote_Poll_End)

    def test_active_executive_has_create_and_close_controls(self):
        self.client.force_login(self.executive)
        response = self.client.get('/poll/')
        self.assertTrue(response.context['can_manage'])
        self.assertTrue(can_manage_polls(self.executive))
        self.assertContains(response, 'Start New Vote', count=1)
        self.assertContains(response, 'End Vote', count=1)
        self.assertTrue(self.client.get('/api/v1/polls/').json()['can_manage'])

    def test_exec_only_and_anonymous_are_not_management_capabilities(self):
        actor = make_user(username='exec-only-ui', roles=('EXEC',))
        self.assertFalse(can_manage_polls(actor))
        from django.contrib.auth.models import AnonymousUser
        self.assertFalse(can_manage_polls(AnonymousUser()))
