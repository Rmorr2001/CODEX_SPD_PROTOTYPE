"""Exact admin field surfaces, model-specific saves and malformed requests."""
import json

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.urls import reverse

from MISC.models import AnnouncementAlert, DayLightSavingsAlert
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.helpers import login_actor
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from .support import audit_time as at_time, AdminAssertions, MODELS, create, payload, admin_url, instant


class AdminWriteTests(AdminAssertions, RegressionTestCase):
    def edit(self, obj, body):
        return self.client.post(admin_url(type(obj), "change", obj.pk), body)

    def test_announcement_admin_exposes_only_title_and_content(self):
        row = create(AnnouncementAlert, is_active=False)
        before = snapshot_scope([row])
        for action in ("add", "change"):
            response = self.client.get(admin_url(AnnouncementAlert, action, row.pk if action == "change" else None))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(set(response.context["adminform"].form.fields), {"title", "content"})
        response = self.client.get(admin_url(AnnouncementAlert, "changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.context["cl"].list_display)
        self.assertIn("created_at", response.context["cl"].list_display)
        assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())

    def test_announcement_admin_add_sets_defaults_and_add_log(self):
        time = instant("2026-01-02T12:00:00Z")
        count = AnnouncementAlert.objects.count()
        with at_time(time):
            response = self.client.post(admin_url(AnnouncementAlert, "add"),
                                        {"title": "Notice", "content": "Room 4", "_save": "1"})
        self.assert_redirect(response, admin_url(AnnouncementAlert, "changelist"))
        row = AnnouncementAlert.objects.get(title="Notice")
        self.assertEqual((row.content, row.is_active, row.created_at, row.updated_at), ("Room 4", True, time, time))
        self.assertEqual(AnnouncementAlert.objects.count(), count + 1)
        entries = self.assert_log(row, ADDITION)
        self.assertEqual(entries.get().action_time, time)
        self.identity()

    def test_announcement_admin_edit_preserves_inactive_flag(self):
        t0, t1 = map(instant, ["2026-01-01T12:00:00Z", "2026-01-02T12:00:00Z"])
        with at_time(t0):
            row = create(AnnouncementAlert, "Notice", content="Room 4", is_active=False)
        pk = row.pk
        count = AnnouncementAlert.objects.count()
        with at_time(t1):
            response = self.edit(row, {"title": "Revised", "content": "Room 5", "_save": "1"})
        self.assert_redirect(response, admin_url(AnnouncementAlert, "changelist"))
        row.refresh_from_db()
        self.assertEqual((row.pk, row.title, row.content, row.is_active), (pk, "Revised", "Room 5", False))
        self.assertEqual((row.created_at, row.updated_at), (t0, t1))
        entry = self.assert_log(row, CHANGE).get()
        self.assertEqual(set(entry.change_message and json.loads(entry.change_message)[0]["changed"]["fields"]),
                         {"Title", "Content"})
        self.assertEqual(AnnouncementAlert.objects.count(), count)
        self.identity()

    def test_announcement_admin_ignores_excluded_field_payloads(self):
        t0, t1 = map(instant, ["2026-01-01T12:00:00Z", "2026-01-02T12:00:00Z"])
        for active in (False, True):
            with at_time(t0):
                row = create(AnnouncementAlert, "Notice", is_active=active)
            pk = row.pk
            with at_time(t1):
                response = self.edit(row, {"title": "Revised", "content": "Room 5", "is_active": "0",
                    "id": self.other_ann.pk, "created_at": "1990-01-01T00:00:00Z",
                    "updated_at": "1990-01-01T00:00:00Z", "_save": "1"})
            self.assertEqual(response.status_code, 302)
            row.refresh_from_db()
            self.assertEqual((row.pk, row.is_active, row.created_at, row.updated_at), (pk, active, t0, t1))
            self.assertEqual((row.title, row.content), ("Revised", "Room 5"))
            self.assert_log(row, CHANGE)
        self.identity()

    def test_save_continue_and_addanother_have_concrete_redirects(self):
        for flag, destination in [("_save", "changelist"), ("_continue", "change"), ("_addanother", "add")]:
            row = create(AnnouncementAlert, "Notice")
            count = AnnouncementAlert.objects.count()
            created = row.created_at
            response = self.edit(row, {"title": "Revised", "content": "Room 5", flag: "1"})
            self.assert_redirect(response, admin_url(AnnouncementAlert, destination,
                                                   row.pk if destination == "change" else None))
            row.refresh_from_db()
            self.assertEqual((row.title, row.content, row.created_at, row.is_active),
                             ("Revised", "Room 5", created, True))
            self.assertEqual(AnnouncementAlert.objects.count(), count)
            self.assert_log(row, CHANGE)
        self.identity()

    def test_saveasnew_requires_add_permission_even_when_button_hidden(self):
        actor = self.staff(models=(AnnouncementAlert,), actions=("view", "change"))
        login_actor(self.client, actor)
        row = create(AnnouncementAlert, "Original")
        before = snapshot_scope([row])
        count = AnnouncementAlert.objects.count()
        response = self.edit(row, {"title": "Clone", "content": "New", "_saveasnew": "1"})
        self.assertEqual(response.status_code, 403)
        assert_unchanged(before)
        self.assertEqual(AnnouncementAlert.objects.count(), count)
        self.assertFalse(LogEntry.objects.exists())
        self.identity(actor=actor)

    def test_authorized_saveasnew_creates_separate_announcement(self):
        row = create(AnnouncementAlert, "Original", is_active=False)
        before = snapshot_scope([row])
        count = AnnouncementAlert.objects.count()
        time = instant("2026-01-02T12:00:00Z")
        with at_time(time):
            response = self.edit(row, {"title": "Clone", "content": "New", "_saveasnew": "1"})
        clone = AnnouncementAlert.objects.get(title="Clone")
        self.assert_redirect(response, admin_url(AnnouncementAlert, "change", clone.pk))
        self.assertNotEqual(clone.pk, row.pk)
        self.assertEqual((clone.content, clone.is_active, clone.created_at, clone.updated_at),
                         ("New", True, time, time))
        self.assertEqual(AnnouncementAlert.objects.count(), count + 1)
        assert_unchanged(before)
        self.assert_log(clone, ADDITION)
        self.assertEqual(LogEntry.objects.count(), 1)
        self.identity()

    def test_add_only_staff_can_create_without_list_permission(self):
        actor = self.staff(models=(AnnouncementAlert,), actions=("add",))
        login_actor(self.client, actor)
        self.assertEqual(self.client.get(admin_url(AnnouncementAlert, "add")).status_code, 200)
        count = AnnouncementAlert.objects.count()
        response = self.client.post(admin_url(AnnouncementAlert, "add"), payload(AnnouncementAlert, "Added", _save="1"))
        self.assert_redirect(response, reverse("admin:index"))
        row = AnnouncementAlert.objects.get(title="Added")
        self.assertEqual((row.content, row.is_active), ("Text", True))
        self.assertEqual(AnnouncementAlert.objects.count(), count + 1)
        self.assert_log(row, ADDITION, actor=actor)
        self.assertEqual(self.client.get(admin_url(AnnouncementAlert, "changelist")).status_code, 403)
        self.identity(actor=actor)

    def test_dst_admin_form_and_list_expose_name_and_active(self):
        row = create(DayLightSavingsAlert, "Clock", is_active=False)
        before = snapshot_scope([row])
        for action in ("add", "change"):
            response = self.client.get(admin_url(DayLightSavingsAlert, action, row.pk if action == "change" else None))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(set(response.context["adminform"].form.fields), {"is_active", "name"})
        response = self.client.get(admin_url(DayLightSavingsAlert, "changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("is_active", response.context["cl"].list_display)
        self.assertIn("name", response.context["cl"].list_display)
        assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())

    def test_dst_admin_add_records_active_name_and_log(self):
        count = DayLightSavingsAlert.objects.count()
        response = self.client.post(admin_url(DayLightSavingsAlert, "add"), payload(DayLightSavingsAlert, "Clock", _save="1"))
        self.assert_redirect(response, admin_url(DayLightSavingsAlert, "changelist"))
        row = DayLightSavingsAlert.objects.get(name="Clock")
        self.assertTrue(row.is_active)
        self.assertEqual(DayLightSavingsAlert.objects.count(), count + 1)
        self.assert_log(row, ADDITION)
        self.identity()

    def test_dst_admin_edit_omitted_checkbox_disables_setting(self):
        row = create(DayLightSavingsAlert, "Before")
        count = DayLightSavingsAlert.objects.count()
        pk = row.pk
        response = self.edit(row, {"name": "After", "_save": "1"})
        self.assert_redirect(response, admin_url(DayLightSavingsAlert, "changelist"))
        row.refresh_from_db()
        self.assertEqual((row.pk, row.name, row.is_active), (pk, "After", False))
        self.assertEqual(DayLightSavingsAlert.objects.count(), count)
        self.assert_log(row, CHANGE)
        self.identity()

    def test_dst_admin_name_normalization_accepts_blank_values(self):
        for fields, expected in [({}, None), ({"name": ""}, None), ({"name": "   "}, None),
                                 ({"name": "  Clock  "}, "Clock")]:
            row = create(DayLightSavingsAlert, "Before")
            count = DayLightSavingsAlert.objects.count()
            response = self.edit(row, {"is_active": "on", "_save": "1", **fields})
            self.assertEqual(response.status_code, 302)
            row.refresh_from_db()
            self.assertEqual((row.name, row.is_active), (expected, True))
            self.assertEqual(DayLightSavingsAlert.objects.count(), count)
            self.assert_log(row, CHANGE)
        self.identity()

    def test_repeated_dst_edit_does_not_insert_duplicate(self):
        row = create(DayLightSavingsAlert, "Before")
        count = DayLightSavingsAlert.objects.count()
        pk = row.pk
        for _ in range(2):
            self.assertEqual(self.edit(row, payload(DayLightSavingsAlert, "After", _save="1")).status_code, 302)
        row.refresh_from_db()
        self.assertEqual((row.pk, row.name, row.is_active), (pk, "After", True))
        self.assertEqual(DayLightSavingsAlert.objects.count(), count)
        self.assert_log(row, CHANGE, count=2)
        self.identity()

    def test_dst_admin_save_flags_and_saveasnew_action(self):
        for flag, destination in [("_save", "changelist"), ("_continue", "change"),
                                  ("_addanother", "add"), ("_saveasnew", "clone")]:
            row = create(DayLightSavingsAlert, "Before", is_active=False)
            before = snapshot_scope([row])
            count = DayLightSavingsAlert.objects.count()
            response = self.edit(row, payload(DayLightSavingsAlert, "Clock", **{flag: "1"}))
            if destination == "clone":
                clone = DayLightSavingsAlert.objects.exclude(pk=row.pk).get(name="Clock")
                self.assert_redirect(response, admin_url(DayLightSavingsAlert, "change", clone.pk))
                self.assertTrue(clone.is_active)
                self.assert_log(clone, ADDITION)
                self.assertEqual(DayLightSavingsAlert.objects.count(), count + 1)
                assert_unchanged(before)
                clone.delete()
            else:
                self.assert_redirect(response, admin_url(DayLightSavingsAlert, destination,
                                                        row.pk if destination == "change" else None))
                row.refresh_from_db()
                self.assertEqual((row.name, row.is_active), ("Clock", True))
                self.assert_log(row, CHANGE)
                self.assertEqual(DayLightSavingsAlert.objects.count(), count)
            row.delete()
        self.identity()

    def test_admin_invalid_fields_return_errors_without_writes(self):
        for model, variants in [(AnnouncementAlert, [({"title": "", "content": "Text"}, "title"),
                ({"title": "Notice", "content": ""}, "content"),
                ({"title": "x" * 256, "content": "Text"}, "title")]),
                (DayLightSavingsAlert, [({"name": "x" * 256, "is_active": "on"}, "name")])]:
            row = create(model, "Before")
            before = snapshot_scope([row])
            count = model.objects.count()
            for action in ("add", "change"):
                for body, field in variants:
                    response = self.client.post(admin_url(model, action, row.pk if action == "change" else None), body)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(field, response.context["adminform"].form.errors)
                    self.assertEqual(model.objects.count(), count)
                    assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())
        self.identity()

    def test_missing_and_malformed_admin_object_ids_do_not_mutate(self):
        counts = tuple(m.objects.count() for m in MODELS)
        for model in MODELS:
            for pk in ("999999", "not-an-integer"):
                for action in ("change", "delete"):
                    url = admin_url(model, action, pk)
                    body = {"post": "yes"} if action == "delete" else payload(model, "No replacement", _save="1")
                    for request in (lambda: self.client.get(url), lambda: self.client.post(url, body)):
                        response = request()
                        self.assert_redirect(response, reverse("admin:index"))
                        messages = [str(m) for m in response.wsgi_request._messages]
                        self.assertTrue(any("doesn’t exist" in m or "doesn't exist" in m for m in messages))
        self.assertEqual(tuple(m.objects.count() for m in MODELS), counts)
        self.assertFalse(LogEntry.objects.exists())
        self.identity()

    def test_unknown_or_empty_bulk_action_has_no_state_effect(self):
        for model in MODELS:
            target = create(model)
            before = snapshot_scope([target])
            for body in ({"action": "unknown_action", "index": "0", "_selected_action": [target.pk]},
                         {"action": "delete_selected", "index": "0"}):
                response = self.client.post(admin_url(model, "changelist"), body)
                self.assert_redirect(response, admin_url(model, "changelist"))
                self.assertTrue(list(response.wsgi_request._messages))
                assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())
        self.identity()

    def check_add_flags(self, model):
        for flag, destination in [("_save", "changelist"), ("_continue", "change"), ("_addanother", "add")]:
            count = model.objects.count()
            response = self.client.post(admin_url(model, "add"), payload(model, "Created", **{flag: "1"}))
            row = model.objects.get(**({"title": "Created"} if model is AnnouncementAlert else {"name": "Created"}))
            self.assert_redirect(response, admin_url(model, destination, row.pk if destination == "change" else None))
            self.assertEqual(model.objects.count(), count + 1)
            self.assertTrue(row.is_active)
            self.assert_log(row, ADDITION)
            row.delete()
        self.identity()

    def test_announcement_add_flags_redirect_without_extra_inserts(self):
        self.check_add_flags(AnnouncementAlert)

    def test_dst_add_flags_redirect_without_extra_inserts(self):
        self.check_add_flags(DayLightSavingsAlert)
