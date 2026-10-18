"""Mounted HOME/AUTHENTICATE boundaries and the explicitly unmounted MISC callable."""
from unittest.mock import patch, sentinel
from urllib.parse import parse_qs, urlsplit

from django.contrib.admin.models import LogEntry
from django.test import RequestFactory, Client
from django.urls import URLPattern, URLResolver, get_resolver, resolve
from django.conf import settings

from MISC.models import AnnouncementAlert, DayLightSavingsAlert
from MISC.views import daylight_savings_alert
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import login_actor
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from .support import misc_time as at_time, announcement, setting, instant


class IntegrationTests(RegressionTestCase):
    def setUp(self):
        super().setUp()
        clock = at_time(instant("2026-01-01T12:00:00Z"))
        clock.__enter__()
        self.addCleanup(clock.__exit__, None, None, None)

    def tearDown(self):
        try:
            self.assertFalse(LogEntry.objects.exists())
        finally:
            super().tearDown()

    def reader(self, username="reader", roles=()):
        actor = make_user(username=username, roles=roles)
        login_actor(self.client, actor)
        return actor

    def assert_identity(self, actor):
        self.assertEqual(self.client.session.get("_auth_user_id"), str(actor.pk))

    def test_dashboard_selects_only_active_announcements(self):
        actor = self.reader(roles=("ACTIVE",))
        a = announcement("Spring notice", "Bring paper")
        b = announcement("Hidden notice", "Hidden content", is_active=False)
        c = announcement("Meeting notice", "Room 4")
        before = snapshot_scope([a, b, c, actor, actor.brother_profile])
        roles = list(actor.brother_profile.roles.values_list("pk", flat=True))
        response = self.client.get("/auth/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({r.pk for r in response.context["announcements"]}, {a.pk, c.pk})
        self.assertContains(response, "Spring notice", count=1)
        self.assertContains(response, "Meeting notice", count=1)
        self.assertNotContains(response, "Hidden notice")
        self.assertNotContains(response, "Hidden content")
        assert_unchanged(before)
        self.assertEqual(list(actor.brother_profile.roles.values_list("pk", flat=True)), roles)
        self.assert_identity(actor)

    def test_next_dashboard_read_reflects_activation_change(self):
        actor = self.reader()
        a, b = announcement("Old notice", "Old"), announcement("New notice", "New", is_active=False)
        first = self.client.get("/auth/dashboard/")
        self.assertEqual({r.pk for r in first.context["announcements"]}, {a.pk})
        a.is_active, b.is_active = False, True
        a.save()
        b.save()
        before = snapshot_scope([a, b])
        response = self.client.get("/auth/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({r.pk for r in response.context["announcements"]}, {b.pk})
        assert_unchanged(before)
        self.assert_identity(actor)

    def test_dashboard_empty_or_inactive_only_has_no_table(self):
        actor = self.reader()
        for inactive in (False, True):
            if inactive:
                announcement("Hidden", "No", is_active=False)
            before = snapshot_scope(list(AnnouncementAlert.objects.all()))
            for _ in range(2):
                response = self.client.get("/auth/dashboard/")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(list(response.context["announcements"]), [])
                self.assertNotContains(response, "announcement-table")
                self.assertNotContains(response, "close-button")
            self.assertEqual(AnnouncementAlert.objects.count(), int(inactive))
            assert_unchanged(before)
            self.assert_identity(actor)

    def test_resolver_contains_no_misc_view(self):
        def callbacks(patterns):
            for item in patterns:
                if isinstance(item, URLResolver):
                    yield from callbacks(item.url_patterns)
                elif isinstance(item, URLPattern):
                    yield item.callback
        for urlconf in ("SPDWEBAPP_CORE.urls", "railway_demo.urls"):
            with self.subTest(urlconf=urlconf):
                self.assertNotIn(daylight_savings_alert, list(callbacks(get_resolver(urlconf).url_patterns)))
                self.assertEqual(resolve("/auth/dashboard/", urlconf=urlconf).url_name, "dashboard")
                self.assertEqual(resolve("/", urlconf=urlconf).url_name, "home")
        import MISC.urls
        self.assertFalse(getattr(MISC.urls, "urlpatterns", []))
        self.assertFalse(AnnouncementAlert.objects.exists())
        self.assertFalse(DayLightSavingsAlert.objects.exists())

    def test_direct_view_context_messages_without_public_endpoint(self):
        row = setting("Ignored", is_active=False)
        before = snapshot_scope([row])
        variants = [
            (instant("2026-03-08T08:00:00Z"), "Daylight Saving Time is on March 08, 2026. "
             "Clocks will move forward one hour!"),
            (instant("2026-11-01T08:00:00Z"), "Daylight Saving Time is on November 01, 2026. "
             "Clocks will move back one hour!"),
            (None, "No upcoming Daylight Saving Time changes found."),
        ]
        factory = RequestFactory()
        for method in (factory.get, factory.post):
            for date, message in variants:
                request = method("/")  # Direct callable only: no claimed MISC route.
                with patch("MISC.views.get_next_dst_change", return_value=date), \
                        patch("MISC.views.render", return_value=sentinel.rendered) as render:
                    result = daylight_savings_alert(request)
                self.assertIs(result, sentinel.rendered)
                render.assert_called_once_with(request, "dls_alert.html",
                                               {"message": message, "show_alert": True})
        assert_unchanged(before)

    def test_eligible_roles_receive_global_active_content(self):
        a = announcement("Global", "Everyone eligible")
        b = announcement("Hidden", "No", is_active=False)
        before = snapshot_scope([a, b])
        for index, roles in enumerate([(), ("ACTIVE",), ("ALUMNI",), ("PRESIDENT",), ()]):
            actor = self.reader(username=f"reader-{index}", roles=roles)
            user_before = snapshot_scope([actor, actor.brother_profile])
            response = self.client.get("/auth/dashboard/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual({r.pk for r in response.context["announcements"]}, {a.pk})
            self.assertContains(response, "Global", count=1)
            self.assertNotContains(response, "Hidden")
            self.assertEqual(set(actor.brother_profile.roles.values_list("name", flat=True)), set(roles))
            self.assert_identity(actor)
            assert_unchanged(user_before)
        assert_unchanged(before)

    def test_anonymous_dashboard_redirect_discloses_no_fragment(self):
        a, s = announcement("Member-only notice"), setting("Clock")
        before = snapshot_scope([a, s])
        response = self.client.get("/auth/dashboard/")
        self.assertEqual(response.status_code, 302)
        target = urlsplit(response.headers["Location"])
        self.assertEqual(target.path, urlsplit(settings.LOGIN_URL).path)
        self.assertEqual(parse_qs(target.query)["next"], ["/auth/dashboard/"])
        for text in (b"Member-only notice", b"clockButton", b"announcement-row"):
            self.assertNotIn(text, response.content)
        self.assertNotIn("_auth_user_id", self.client.session)
        assert_unchanged(before)

    def test_any_new_member_combination_redirects_before_alert_render(self):
        row = announcement("No redirect disclosure")
        before = snapshot_scope([row])
        variants = [("NEW_MEMBER",), ("NEW_MEMBER", "ACTIVE"), ("NEW_MEMBER", "PRESIDENT")]
        for index, roles in enumerate(variants):
            actor = self.reader(username=f"new-reader-{index}", roles=roles)
            user_before = snapshot_scope([actor, actor.brother_profile])
            response = self.client.get("/auth/dashboard/")
            self.assertEqual((response.status_code, response.headers["Location"]), (302, "/newmember/"))
            self.assertNotIn(b"announcement-row", response.content)
            self.assertNotIn(b"clockButton", response.content)
            self.assertNotIn(b"No redirect disclosure", response.content)
            self.assertEqual(set(actor.brother_profile.roles.values_list("name", flat=True)), set(roles))
            self.assert_identity(actor)
            assert_unchanged(user_before)
        assert_unchanged(before)

    def test_home_has_no_announcement_or_clock_integration(self):
        row, s = announcement("Do not show on home"), setting("Do not show clock")
        before = snapshot_scope([row, s])
        actor = self.reader()
        # Preserve a separate anonymous browser after logging in the default client.
        anonymous = Client()
        for client in (anonymous, self.client):
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            for text in ("announcement-row", "clockButton", row.title, s.name):
                self.assertNotContains(response, text)
        self.assert_identity(actor)
        assert_unchanged(before)

    def test_orm_and_reader_actions_do_not_create_admin_logs(self):
        row, s = announcement("Initial"), setting("Clock")
        actor = self.reader()
        before = snapshot_scope([s, actor, actor.brother_profile])
        row.content = "Changed"
        row.save()
        saved = snapshot_scope([row])
        for _ in range(2):
            response = self.client.get("/auth/dashboard/")
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Changed")
        assert_unchanged(before)
        assert_unchanged(saved)
        self.assert_identity(actor)
        self.assertFalse(actor.brother_profile.roles.exists())
