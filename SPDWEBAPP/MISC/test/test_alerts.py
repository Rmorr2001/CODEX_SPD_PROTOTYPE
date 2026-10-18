"""Real inclusion tags, settings and explicitly injected utility boundaries."""
from unittest.mock import patch

from django.contrib.admin.models import LogEntry
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils import timezone

from MISC.models import AnnouncementAlert, DayLightSavingsAlert
from MISC.templatetags.dls_tags import dls_alert
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from .support import misc_time as at_time, setting, announcement, instant, Elements


def render_tag():
    return Template("{% load dls_tags %}{% dls_alert %}").render(Context())


class AlertTests(RegressionTestCase):
    def setUp(self):
        super().setUp()
        self.clock = at_time(instant("2026-01-01T12:00:00Z"))
        self.clock.__enter__()
        self.addCleanup(self.clock.__exit__, None, None, None)

    def tearDown(self):
        try:
            self.assertFalse(LogEntry.objects.exists())
        finally:
            super().tearDown()

    def test_tag_without_setting_shows_spring_message(self):
        result = dls_alert()
        self.assertTrue(result["show_alert"])
        self.assertEqual(str(result["next_change"].date()), "2026-03-08")
        self.assertTrue(timezone.is_aware(result["next_change"]))
        self.assertEqual(result["message"], "Next Daylight Saving Time: March 08, 2026. "
                         "Clocks will move forward one hour!")
        self.assertFalse(DayLightSavingsAlert.objects.exists())
        self.assertFalse(AnnouncementAlert.objects.exists())

    def test_tag_without_setting_shows_fall_message(self):
        with at_time(instant("2026-04-01T12:00:00Z")):
            result = dls_alert()
        self.assertTrue(result["show_alert"])
        self.assertEqual(str(result["next_change"].date()), "2026-11-01")
        self.assertTrue(timezone.is_aware(result["next_change"]))
        self.assertEqual(result["message"], "Next Daylight Saving Time: November 01, 2026. "
                         "Clocks will move back one hour!")
        self.assertFalse(DayLightSavingsAlert.objects.exists())
        self.assertFalse(AnnouncementAlert.objects.exists())

    def test_blank_override_preserves_computed_message(self):
        for name in (None, ""):
            row = setting(name)
            before = snapshot_scope([row])
            result = dls_alert()
            self.assertTrue(result["show_alert"])
            self.assertTrue(result["message"].startswith("Next Daylight Saving Time: March 08, 2026."))
            self.assertTrue(timezone.is_aware(result["next_change"]))
            self.assertEqual(DayLightSavingsAlert.objects.count(), 1)
            assert_unchanged(before)
            row.delete()

    def test_active_override_replaces_message_and_newlines(self):
        row = setting("line1\nline2")
        before = snapshot_scope([row])
        result, html = dls_alert(), render_tag()
        self.assertEqual(result["message"], "line1<br>line2")
        self.assertTrue(result["show_alert"])
        self.assertTrue(timezone.is_aware(result["next_change"]))
        self.assertIn("line1<br>line2", html)
        self.assertEqual(sum(attrs.get("id") == "clockButton" for _, attrs in Elements(html).nodes), 1)
        self.assertEqual(DayLightSavingsAlert.objects.count(), 1)
        assert_unchanged(before)
        self.assertFalse(AnnouncementAlert.objects.exists())

    def test_inactive_setting_hides_dst_fragment(self):
        row = setting("Hidden message", is_active=False)
        before = snapshot_scope([row])
        for _ in range(2):
            self.assertFalse(dls_alert()["show_alert"])
            html = render_tag()
            for sentinel in ("clockButton", 'id="overlay"', 'id="alert"', "toggleAlert",
                             "clock.webp", "Hidden message"):
                self.assertNotIn(sentinel, html)
        assert_unchanged(before)
        self.assertEqual(DayLightSavingsAlert.objects.count(), 1)

    def test_explicit_reactivation_appears_on_next_read(self):
        row = setting("Return", is_active=False)
        self.assertFalse(dls_alert()["show_alert"])
        row.is_active = True
        row.save()
        before = snapshot_scope([row])
        self.assertTrue(dls_alert()["show_alert"])
        html = render_tag()
        self.assertIn("Return", html)
        self.assertIn('id="clockButton"', html)
        assert_unchanged(before)

    def test_fragment_controls_have_local_targets(self):
        row, ann = setting("Clock"), announcement()
        before = snapshot_scope([row, ann])
        html = render_tag()
        nodes = Elements(html).nodes
        for id_ in ("clockButton", "alert", "overlay"):
            self.assertEqual(sum(attrs.get("id") == id_ for _, attrs in nodes), 1)
        self.assertEqual(html.count("function toggleAlert()"), 1)
        self.assertEqual(sum(attrs.get("onclick") == "toggleAlert()" for _, attrs in nodes), 2)
        self.assertIn("document.getElementById('alert')", html)
        self.assertIn("document.getElementById('overlay')", html)
        ann_html = render_to_string("MISC/announcement_alert.html", {"announcements": [ann]})
        self.assertIn("this.closest('table').style.display='none';", ann_html)
        self.assertFalse(any(tag == "form" for tag, _ in nodes + Elements(ann_html).nodes))
        self.assertNotIn("fetch(", html + ann_html)
        assert_unchanged(before)

    def test_tag_none_result_uses_unavailable_message(self):
        with patch("MISC.templatetags.dls_tags.get_next_dst_change", return_value=None):
            result, html = dls_alert(), render_tag()
        self.assertEqual(result, {"show_alert": True, "next_change": None,
                                 "message": "Daylight Saving Time information unavailable."})
        self.assertIn('id="clockButton"', html)
        self.assertIn(result["message"], html)
        self.assertFalse(DayLightSavingsAlert.objects.exists())
        self.assertFalse(AnnouncementAlert.objects.exists())

    def test_tag_none_result_still_allows_setting_override(self):
        row = setting("Maintenance", is_active=False)
        before = snapshot_scope([row])
        with patch("MISC.templatetags.dls_tags.get_next_dst_change", return_value=None):
            result, html = dls_alert(), render_tag()
        self.assertEqual(result, {"show_alert": False, "next_change": None, "message": "Maintenance"})
        self.assertNotIn("clockButton", html)
        self.assertNotIn("Maintenance", html)
        assert_unchanged(before)
        self.assertEqual(DayLightSavingsAlert.objects.count(), 1)

    def test_injected_does_not_exist_keeps_tag_default(self):
        with patch.object(DayLightSavingsAlert.objects, "first",
                          side_effect=DayLightSavingsAlert.DoesNotExist):
            result = dls_alert()
        self.assertTrue(result["show_alert"])
        self.assertIn("March 08, 2026", result["message"])
        self.assertTrue(timezone.is_aware(result["next_change"]))
        self.assertFalse(DayLightSavingsAlert.objects.exists())
        self.assertFalse(AnnouncementAlert.objects.exists())
