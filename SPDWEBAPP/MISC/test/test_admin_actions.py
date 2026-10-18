"""Real CSRF requests, selected deletions and scoped stock audit history."""
import re

from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.test import override_settings

from MISC.models import AnnouncementAlert, DayLightSavingsAlert
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.helpers import login_actor, csrf_client
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from .support import audit_time as at_time, AdminAssertions, MODELS, create, payload, admin_url, instant


class AdminActionTests(AdminAssertions, RegressionTestCase):
    def test_admin_mutations_reject_missing_or_bad_csrf_token(self):
        for model in MODELS:
            target = create(model, "Keep")
            before = snapshot_scope([target])
            count = model.objects.count()
            for token in (None, "bad-token"):
                client = csrf_client()
                login_actor(client, self.actor)
                for action in ("add", "change", "delete", "changelist"):
                    pk = target.pk if action in ("change", "delete") else None
                    body = payload(model, _save="1")
                    if model is DayLightSavingsAlert:
                        body.pop("is_active")
                    if action == "delete":
                        body = {"post": "yes"}
                    elif action == "changelist":
                        body = {"action": "delete_selected", "_selected_action": [target.pk], "post": "yes"}
                    if token:
                        body["csrfmiddlewaretoken"] = token
                    response = client.post(admin_url(model, action, pk), body)
                    self.assertEqual(response.status_code, 403)
                    assert_unchanged(before)
                    self.assertEqual(model.objects.count(), count)
                    self.identity(client=client)
        self.assertFalse(LogEntry.objects.exists())

    def test_admin_valid_csrf_pair_allows_intended_write(self):
        for model in MODELS:
            for action in ("add", "change", "delete", "changelist"):
                with self.subTest(model=model.__name__, action=action):
                    target = create(model, "Keep")
                    other = create(model, "Second")
                    before = snapshot_scope([other])
                    other_model = MODELS[1] if model is MODELS[0] else MODELS[0]
                    other_count = other_model.objects.count()
                    count, logs = model.objects.count(), LogEntry.objects.count()
                    client = csrf_client()
                    login_actor(client, self.actor)
                    url = admin_url(model, action, target.pk if action in ("change", "delete") else None)
                    form = client.get(url)
                    self.assertEqual(form.status_code, 200)
                    token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', form.content.decode())[1]
                    self.assertIn(settings.CSRF_COOKIE_NAME, client.cookies)
                    body = payload(model, _save="1")
                    if model is DayLightSavingsAlert:
                        body.pop("is_active")
                    if action == "delete":
                        body = {"post": "yes"}
                    elif action == "changelist":
                        body = {"action": "delete_selected", "_selected_action": [target.pk], "post": "yes"}
                    response = client.post(url, {**body, "csrfmiddlewaretoken": token})
                    self.assertEqual(response.status_code, 302)
                    if action == "add":
                        changed = model.objects.get(**({"title": "New"} if model is AnnouncementAlert else {"name": "New"}))
                        self.assertEqual(model.objects.count(), count + 1)
                        self.assertEqual(changed.is_active, model is AnnouncementAlert)
                        flag = ADDITION
                    elif action == "change":
                        target.refresh_from_db()
                        self.assertEqual(target.title if model is AnnouncementAlert else target.name, "New")
                        self.assertEqual(target.is_active, model is AnnouncementAlert)
                        self.assertEqual(model.objects.count(), count)
                        changed, flag = target, CHANGE
                    else:
                        self.assertFalse(model.objects.filter(pk=target.pk).exists())
                        self.assertEqual(model.objects.count(), count - 1)
                        changed, flag = target, DELETION
                    self.assert_log(changed, flag)
                    self.assertEqual(LogEntry.objects.count(), logs + 1)
                    assert_unchanged(before)
                    self.assertEqual(other_model.objects.count(), other_count)
                    self.identity(client=client)
                    if action == "add":
                        changed.delete()
                    if action not in ("delete", "changelist"):
                        target.delete()
                    other.delete()

    def test_demo_boundary_blocks_model_admin_even_with_permission(self):
        from SPDWEBAPP_CORE.testing import demo_settings
        targets = [create(model, "Private") for model in MODELS]
        before = snapshot_scope(targets)
        with override_settings(ROOT_URLCONF=demo_settings.ROOT_URLCONF, DEMO_MODE=True,
                MIDDLEWARE=demo_settings.MIDDLEWARE, SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True):
            for model, target in zip(MODELS, targets):
                for action in ("changelist", "add", "change", "delete", "history"):
                    response = self.client.get(admin_url(model, action,
                        target.pk if action in ("change", "delete", "history") else None), secure=True)
                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(response.json(), {"error": "Admin is unavailable on the public demo."})
                    self.assertNotIn(b"Private", response.content)
            self.assertEqual(self.client.get("/admin/", secure=True).status_code, 403)
        assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())
        self.identity()

    def test_detail_delete_confirmation_get_is_read_only(self):
        for model in MODELS:
            target = create(model, "Delete me")
            before = snapshot_scope([target])
            response = self.client.get(admin_url(model, "delete", target.pk))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["object"].pk, target.pk)
            self.assertContains(response, str(target))
            self.assertContains(response, 'name="post"')
            assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())
        self.identity()

    def test_detail_delete_removes_only_target_and_logs_once(self):
        for model in MODELS:
            target = create(model, "Delete me")
            count = model.objects.count()
            response = self.client.post(admin_url(model, "delete", target.pk), {"post": "yes"})
            self.assert_redirect(response, admin_url(model, "changelist"))
            self.assertFalse(model.objects.filter(pk=target.pk).exists())
            self.assertEqual(model.objects.count(), count - 1)
            self.assert_log(target, DELETION)
        self.assertEqual(LogEntry.objects.count(), 2)
        self.identity()

    def test_bulk_delete_confirmation_preserves_selected_rows(self):
        for model in MODELS:
            x, y, z = [create(model, label) for label in ("First", "Second", "Keep")]
            before = snapshot_scope([x, y, z])
            response = self.client.post(admin_url(model, "changelist"), {
                "action": "delete_selected", "index": "0", "_selected_action": [x.pk, y.pk]})
            self.assertEqual(response.status_code, 200)
            self.assertEqual({r.pk for r in response.context["queryset"]}, {x.pk, y.pk})
            self.assertContains(response, str(x))
            self.assertContains(response, str(y))
            self.assertNotIn(admin_url(model, "change", z.pk),
                             " ".join(str(item) for item in response.context["deletable_objects"]))
            assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())
        self.identity()

    def test_confirmed_bulk_delete_keeps_unselected_records(self):
        for model in MODELS:
            x, y, z = [create(model, label) for label in ("First", "Second", "Keep")]
            before = snapshot_scope([z])
            count, logs = model.objects.count(), LogEntry.objects.count()
            response = self.client.post(admin_url(model, "changelist"), {
                "action": "delete_selected", "_selected_action": [x.pk, y.pk], "post": "yes"})
            self.assert_redirect(response, admin_url(model, "changelist"))
            self.assertEqual(model.objects.count(), count - 2)
            self.assertFalse(model.objects.filter(pk__in=[x.pk, y.pk]).exists())
            self.assert_log(x, DELETION)
            self.assert_log(y, DELETION)
            self.assertEqual(LogEntry.objects.count(), logs + 2)
            assert_unchanged(before)
        self.identity()

    def test_repeated_stale_delete_is_non_mutating(self):
        from django.urls import reverse
        for model in MODELS:
            target = create(model)
            pk = target.pk
            self.client.post(admin_url(model, "delete", pk), {"post": "yes"})
            logs, count = LogEntry.objects.count(), model.objects.count()
            for _ in range(2):
                response = self.client.post(admin_url(model, "delete", pk), {"post": "yes"})
                self.assert_redirect(response, reverse("admin:index"))
                self.assertTrue(any("exist" in str(m) for m in response.wsgi_request._messages))
                self.assertEqual(LogEntry.objects.count(), logs)
                self.assertEqual(model.objects.count(), count)
        self.identity()

    def test_admin_history_is_scoped_to_object_and_actor(self):
        for model in MODELS:
            login_actor(self.client, self.actor)
            with at_time(instant("2026-01-01T12:00:00Z")):
                self.client.post(admin_url(model, "add"), payload(model, "History target", _save="1"))
            target = model.objects.get(**({"title": "History target"} if model is AnnouncementAlert else {"name": "History target"}))
            with at_time(instant("2026-01-02T12:00:00Z")):
                self.client.post(admin_url(model, "change", target.pk), payload(model, "Edited history", _save="1"))
            target.refresh_from_db()
            other_actor = self.staff(models=(model,))
            login_actor(self.client, other_actor)
            self.client.post(admin_url(model, "add"), payload(model, "Other history", _save="1"))
            before = snapshot_scope(list(model.objects.all()))
            logs = list(LogEntry.objects.values())
            viewer = self.staff(models=(model,), actions=("view",))
            login_actor(self.client, viewer)
            response = self.client.get(admin_url(model, "history", target.pk))
            self.assertEqual(response.status_code, 200)
            entries = list(response.context["action_list"])
            self.assertEqual([r.action_flag for r in entries], [ADDITION, CHANGE])
            self.assertEqual([r.user_id for r in entries], [self.actor.pk] * 2)
            self.assertEqual({r.object_id for r in entries}, {str(target.pk)})
            self.assertEqual([r.action_time for r in entries],
                             [instant("2026-01-01T12:00:00Z"), instant("2026-01-02T12:00:00Z")])
            self.assertEqual(list(LogEntry.objects.values()), logs)
            assert_unchanged(before)
            self.identity(actor=viewer)

    def test_admin_history_denies_staff_without_view_or_change(self):
        for model in MODELS:
            login_actor(self.client, self.actor)
            self.client.post(admin_url(model, "add"), payload(model, "History target", _save="1"))
            target = model.objects.get(**({"title": "History target"} if model is AnnouncementAlert else {"name": "History target"}))
            before = snapshot_scope([target])
            logs = list(LogEntry.objects.values())
            actor = self.staff(models=(model,), actions=("add",))
            login_actor(self.client, actor)
            response = self.client.get(admin_url(model, "history", target.pk))
            self.assertEqual(response.status_code, 403)
            self.assertNotIn(b"History target", response.content)
            self.assertEqual(list(LogEntry.objects.values()), logs)
            assert_unchanged(before)
            self.identity(actor=actor)
