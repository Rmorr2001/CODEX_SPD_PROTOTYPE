"""Announcement and setting model contracts, and escaped announcement fragments."""
from django.contrib.admin.models import LogEntry
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils import timezone

from MISC.models import AnnouncementAlert, DayLightSavingsAlert
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.helpers import at_time
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from .support import announcement, setting, instant, Elements


class RecordTests(RegressionTestCase):
    def setUp(self):
        super().setUp()
        self.other = announcement("Other", "Keep", is_active=False)
        self.before = snapshot_scope([self.other])

    def tearDown(self):
        try:
            assert_unchanged(self.before)
            self.assertFalse(LogEntry.objects.exists())
        finally:
            super().tearDown()

    def test_announcement_create_defaults_and_string(self):
        t = instant("2026-01-02T12:00:00Z")
        with at_time(t):
            row = announcement("Spring notice", "Bring paper")
        row.refresh_from_db()
        self.assertTrue(row.is_active)
        self.assertEqual(str(row), "Spring notice")
        self.assertEqual((row.created_at, row.updated_at), (t, t))
        self.assertTrue(timezone.is_aware(row.created_at))
        self.assertEqual(AnnouncementAlert.objects.count(), 2)

    def test_announcement_update_changes_only_update_timestamp(self):
        t0, t1 = map(instant, ["2026-01-02T12:00:00Z", "2026-01-03T12:00:00Z"])
        with at_time(t0):
            row = announcement("Notice", "Room 4")
        pk = row.pk
        with at_time(t1):
            row.title, row.content = "Revised", "Room 5"
            row.save()
        row.refresh_from_db()
        self.assertEqual((row.title, row.content, str(row)), ("Revised", "Room 5", "Revised"))
        self.assertEqual((row.pk, row.created_at, row.updated_at, row.is_active), (pk, t0, t1, True))
        self.assertEqual(AnnouncementAlert.objects.count(), 2)

    def test_unchanged_announcement_save_advances_updated_at(self):
        t0, t1 = map(instant, ["2026-01-02T12:00:00Z", "2026-01-03T12:00:00Z"])
        with at_time(t0):
            row = announcement("Notice", "Room 4")
        pk = row.pk
        with at_time(t1):
            row.save()
        row.refresh_from_db()
        self.assertEqual((row.pk, row.title, row.content, row.is_active), (pk, "Notice", "Room 4", True))
        self.assertEqual((row.created_at, row.updated_at), (t0, t1))
        self.assertEqual(AnnouncementAlert.objects.count(), 2)

    def test_announcement_full_clean_rejects_missing_or_long_title(self):
        for title, content, field in [("", "Text", "title"), ("Notice", "", "content"),
                                      ("x" * 256, "Text", "title")]:
            with self.subTest(field=field, size=len(title)):
                row = AnnouncementAlert(title=title, content=content)
                with self.assertRaises(ValidationError) as raised:
                    row.full_clean()
                self.assertIn(field, raised.exception.message_dict)
                self.assertIsNone(row.pk)
        self.assertEqual(AnnouncementAlert.objects.count(), 1)

    def test_announcement_full_clean_accepts_maximum_title(self):
        row = AnnouncementAlert(title="x" * 255, content="Text")
        row.full_clean()
        t = instant("2026-01-02T12:00:00Z")
        with at_time(t):
            row.save()
        row.refresh_from_db()
        self.assertEqual((row.title, row.content, row.is_active), ("x" * 255, "Text", True))
        self.assertEqual((row.created_at, row.updated_at), (t, t))
        self.assertEqual(AnnouncementAlert.objects.count(), 2)

    def test_dst_model_default_optional_name_and_string(self):
        other = setting("Other", is_active=False)
        before = snapshot_scope([other])
        for fields, expected in [({}, None), ({"name": None}, None), ({"name": ""}, ""),
                                 ({"name": "x" * 255}, "x" * 255)]:
            with self.subTest(fields=fields):
                count = DayLightSavingsAlert.objects.count()
                row = DayLightSavingsAlert.objects.create(**fields)
                row.refresh_from_db()
                self.assertEqual((row.name, row.is_active), (expected, True))
                self.assertEqual(str(row), "DLS Alert - Active: True")
                self.assertEqual(DayLightSavingsAlert.objects.count(), count + 1)
                row.delete()
        assert_unchanged(before)

    def test_dst_model_update_keeps_other_settings(self):
        row, other = setting("Before"), setting("Other")
        before = snapshot_scope([other])
        pk = row.pk
        row.name, row.is_active = "After", False
        row.save()
        row.refresh_from_db()
        self.assertEqual((row.pk, row.name, row.is_active), (pk, "After", False))
        self.assertEqual(str(row), "DLS Alert - Active: False")
        self.assertEqual(DayLightSavingsAlert.objects.count(), 2)
        assert_unchanged(before)

    def test_dst_model_full_clean_rejects_long_name(self):
        other = setting("Other", is_active=False)
        before = snapshot_scope([other])
        row = DayLightSavingsAlert(name="x" * 256)
        with self.assertRaises(ValidationError) as raised:
            row.full_clean()
        self.assertIn("name", raised.exception.message_dict)
        self.assertIsNone(row.pk)
        self.assertEqual(DayLightSavingsAlert.objects.count(), 1)
        assert_unchanged(before)

    def test_announcement_template_escapes_untrusted_text(self):
        row = announcement('<script>alert(1)</script>', '<img src=x onerror=alert(2)> & "quoted"')
        before = snapshot_scope([row])
        html = render_to_string("MISC/announcement_alert.html", {"announcements": [row]})
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("&lt;img src=x onerror=alert(2)&gt; &amp; &quot;quoted&quot;", html)
        nodes = Elements(html).nodes
        self.assertFalse(any(tag in ("script", "img") for tag, _ in nodes))
        self.assertFalse(any("onerror" in attrs for _, attrs in nodes))
        self.assertEqual(sum(attrs.get("class") == "announcement-row" for _, attrs in nodes), 1)
        assert_unchanged(before)

    def test_announcement_template_prefers_updated_date(self):
        row = announcement()
        AnnouncementAlert.objects.filter(pk=row.pk).update(
            created_at=instant("2026-01-02T12:00:00Z"), updated_at=instant("2026-01-03T13:15:00Z"))
        row.refresh_from_db()
        before = snapshot_scope([row])
        with timezone.override("UTC"):
            html = render_to_string("MISC/announcement_alert.html", {"announcements": [row]})
        self.assertIn("Updated on: Jan 03, 2026, 13:15", html)
        self.assertNotIn("Created on:", html)
        self.assertEqual(html.count('class="announcement-title"'), 1)
        self.assertIn('>Notice</h2>', html)
        self.assertIn('>Text</p>', html)
        assert_unchanged(before)

    def test_announcement_template_created_date_fallback(self):
        row = AnnouncementAlert(title="Notice", content="Text",
                                created_at=instant("2026-01-02T12:00:00Z"), updated_at=None)
        count = AnnouncementAlert.objects.count()
        with timezone.override("UTC"):
            html = render_to_string("MISC/announcement_alert.html", {"announcements": [row]})
        self.assertIn("Created on: Jan 02, 2026, 12:00", html)
        self.assertNotIn("Updated on:", html)
        self.assertIsNone(row.pk)
        self.assertEqual(AnnouncementAlert.objects.count(), count)

    def test_announcement_fragment_without_context_is_empty(self):
        row = announcement("Not supplied", "Do not leak")
        before = snapshot_scope([row])
        for context in ({}, {"announcements": []}):
            html = render_to_string("MISC/announcement_alert.html", context)
            for sentinel in ("announcement-container", "announcement-table", "close-button", row.title):
                self.assertNotIn(sentinel, html)
        assert_unchanged(before)
        self.assertEqual(AnnouncementAlert.objects.count(), 2)
