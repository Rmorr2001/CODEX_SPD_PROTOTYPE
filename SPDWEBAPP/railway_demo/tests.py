from pathlib import Path
from tempfile import TemporaryDirectory
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings
from AUTHENTICATE.models import Brother_Profile
from NEWMEMBER.models import NewMember_Mark_Event_and_Request
from PARLEYPRO.models import Vote_Poll
from PHILANTHROPY.models import Philanthropy_Hours_Event_and_Request


class RailwayDemoTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.media = TemporaryDirectory()
        cls.override = override_settings(MEDIA_ROOT=Path(cls.media.name))
        cls.override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.override.disable()
        cls.media.cleanup()

    @classmethod
    def setUpTestData(cls):
        call_command("seed_railway_demo")

    def test_seed_is_idempotent_and_populates_actual_models(self):
        call_command("seed_railway_demo")
        self.assertEqual(Brother_Profile.objects.count(), 12)
        self.assertEqual(Vote_Poll.objects.count(), 2)
        self.assertEqual(Philanthropy_Hours_Event_and_Request.objects.count(), 9)
        self.assertEqual(NewMember_Mark_Event_and_Request.objects.count(), 4)
        for user in User.objects.all():
            self.assertFalse(user.has_usable_password())
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)

    def test_seed_refuses_privileged_accounts_and_non_demo_settings(self):
        with override_settings(DEMO_MODE=False), self.assertRaises(CommandError):
            call_command("seed_railway_demo")
        User.objects.filter(username="demo-executive").update(is_staff=True)
        with self.assertRaises(CommandError):
            call_command("seed_railway_demo")

    def test_original_public_pages_render(self):
        for path in ("/", "/ourHistory/", "/codeOfEthics/", "/rush/", "/executive-board/", "/auth/login/"):
            self.assertEqual(self.client.get(path).status_code, 200, path)
        self.assertContains(self.client.get("/"), "Sigma Phi Delta: Beta-Omicron Chapter")

    def test_anonymous_member_pages_require_login(self):
        for path in ("/auth/dashboard/", "/auth/roster/", "/auth/profile/", "/philanthropy/"):
            self.assertEqual(self.client.get(path).status_code, 302, path)

    def test_executive_can_browse_existing_workflows(self):
        self.client.post("/demo/enter/", {"persona": "executive"})
        paths = ("/auth/dashboard/", "/auth/roster/", "/auth/alumni_roster/", "/auth/profile/",
                 "/poll/", "/poll/past_polls/", "/poll/start_vote/", "/poll/poll-results/",
                 "/philanthropy/", "/philanthropy/request/", "/philanthropy/approve/",
                 "/newmember/marks/", "/newmember/request/", "/newmember/approve/")
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 200, path)
        self.assertContains(self.client.get("/auth/roster/"), "Example")
        self.assertContains(self.client.get("/poll/"), "Demo: next service activity")

    def test_personas_follow_existing_role_boundaries(self):
        self.client.post("/demo/enter/", {"persona": "newmember"})
        self.assertRedirects(self.client.get("/auth/dashboard/"), "/newmember/")
        self.assertEqual(self.client.get("/newmember/marks/").status_code, 200)
        self.client.post("/demo/enter/", {"persona": "alumni"})
        self.assertEqual(self.client.get("/auth/alumni_roster/").status_code, 200)
        self.client.post("/demo/enter/", {"persona": "active"})
        self.assertEqual(self.client.get("/philanthropy/").status_code, 200)
        self.assertEqual(self.client.get("/philanthropy/approve/").status_code, 302)

    def test_demo_entry_is_bounded_and_csrf_protected(self):
        self.assertEqual(self.client.get("/demo/enter/").status_code, 405)
        self.assertEqual(self.client.post("/demo/enter/", {"persona": "unknown"}).status_code, 400)
        self.assertEqual(Client(enforce_csrf_checks=True).post("/demo/enter/").status_code, 403)
        with override_settings(DEMO_MODE=False):
            self.assertEqual(self.client.post("/demo/enter/").status_code, 404)
        User.objects.filter(username="demo-executive").update(is_staff=True)
        self.assertEqual(self.client.post("/demo/enter/").status_code, 503)

    def test_original_profile_updates_and_persona_entry_stays_available(self):
        self.client.post("/demo/enter/")
        response = self.client.post("/auth/update_profile/", {
            "username": "updated-demo-name", "firstName": "Alex", "lastName": "Example",
            "hometown": "Demo Town", "pclass": "Beta Omicron", "email": "demo@example.invalid",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(self.client.post("/demo/enter/").status_code, 302)
        self.assertEqual(self.client.get("/admin/").status_code, 403)

    def test_original_vote_flow_and_philanthropy_request_work(self):
        self.client.post("/demo/enter/", {"persona": "active"})
        self.assertEqual(self.client.post("/poll/", {"aye": "1"}).status_code, 200)
        from PARLEYPRO.models import Brother_votes
        user = User.objects.get(username="demo-active")
        self.assertEqual(Brother_votes.objects.get(user=user).user_vote_choice, "Aye")
        response = self.client.post("/philanthropy/request/", {
            "hours": "2", "event_title": "Demo test service", "event_date": "2026-10-01",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Philanthropy_Hours_Event_and_Request.objects.filter(user=user, philanthropy_event_title="Demo test service").exists())
