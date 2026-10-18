"""Dashboard data selection; unresolved roster audience stays out of READY tests."""
from datetime import datetime, timezone
from AUTHENTICATE.models import DashboardLink
from MISC.models import AnnouncementAlert
from SPDWEBAPP_CORE.testing.helpers import at_time
from .support import IdentityCase, set_roles

CLOCK = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)


class DashboardTests(IdentityCase):
    def test_dashboard_non_newmember_render(self):
        roles = [(), ("ACTIVE",), ("EXEC",), ("PHIL_CHAIR",), ("NM_BOARD",), ("NME",),
                 ("EXEC", "ACTIVE"), ("PHIL_CHAIR", "ACTIVE"), ("ALUMNI",), ("ALUMNI", "ACTIVE")]
        self.login()
        for role_set in roles:
            with self.subTest(roles=role_set), at_time(CLOCK):
                set_roles(self.a, role_set)
                before = self.pair_snapshot()
                response = self.client.get("/auth/dashboard/")
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "AUTHENTICATE/dashboard.html")
                self.assertNotIn("Location", response)
                self.assert_pair_unchanged(before)

    def test_dashboard_links_and_active_announcements(self):
        set_roles(self.a, ("ACTIVE",))
        second = DashboardLink.objects.create(text="Second", link="/second/", order=2)
        first = DashboardLink.objects.create(text="First", link="/first/", order=1)
        with at_time(CLOCK):
            active = AnnouncementAlert.objects.create(title="Active", content="Visible content", is_active=True)
            AnnouncementAlert.objects.create(title="Hidden", content="Secret inactive content", is_active=False)
            self.login()
            before = self.pair_snapshot()
            links = list(DashboardLink.objects.order_by("pk").values())
            announcements = list(AnnouncementAlert.objects.order_by("pk").values())
            response = self.client.get("/auth/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["dashboard_links"]), [first, second])
        self.assertEqual(list(response.context["announcements"]), [active])
        self.assertContains(response, 'href="/first/"')
        self.assertContains(response, 'href="/second/"')
        self.assertLess(response.content.index(b">First<"), response.content.index(b">Second<"))
        self.assertContains(response, "Visible content")
        self.assertNotContains(response, "Secret inactive content")
        self.assertEqual(list(DashboardLink.objects.order_by("pk").values()), links)
        self.assertEqual(list(AnnouncementAlert.objects.order_by("pk").values()), announcements)
        self.assert_pair_unchanged(before)

    def test_dashboard_empty_content(self):
        set_roles(self.a, ("ACTIVE",))
        self.login()
        before = self.pair_snapshot()
        with at_time(CLOCK):
            response = self.client.get("/auth/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["dashboard_links"]), [])
        self.assertEqual(list(response.context["announcements"]), [])
        for href in ("/auth/roster/", "/philanthropy/", "/poll/"):
            self.assertContains(response, f'href="{href}"')
        self.assertFalse(DashboardLink.objects.exists())
        self.assertFalse(AnnouncementAlert.objects.exists())
        self.assert_pair_unchanged(before)
