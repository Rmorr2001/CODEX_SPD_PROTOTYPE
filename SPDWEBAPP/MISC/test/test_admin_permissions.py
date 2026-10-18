"""Model-specific admin grants, denied direct requests and global record access."""
from urllib.parse import parse_qs, urlsplit

from django.contrib.admin.models import LogEntry
from django.test import Client
from django.urls import reverse

from MISC.models import AnnouncementAlert, DayLightSavingsAlert
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import login_actor
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from .support import AdminAssertions, MODELS, create, payload, admin_url


class AdminPermissionTests(AdminAssertions, RegressionTestCase):
    def denied_post(self, model, actor, action, target=None):
        login_actor(self.client, actor)
        before = snapshot_scope([target] if target else [])
        counts = tuple(m.objects.count() for m in MODELS)
        logs = LogEntry.objects.count()
        body = {"post": "yes"} if action == "delete" else payload(model, _save="1")
        response = self.client.post(admin_url(model, action, target.pk if target else None), body)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(tuple(m.objects.count() for m in MODELS), counts)
        self.assertEqual(LogEntry.objects.count(), logs)
        assert_unchanged(before)
        self.identity(actor=actor)

    def test_anonymous_nonstaff_and_inactive_staff_cannot_enter_admin(self):
        actors = [None, make_user(username="member", roles=("PRESIDENT",)),
                  self.staff(is_active=False)]
        for model in MODELS:
            target = create(model)
            before = snapshot_scope([target])
            for actor in actors:
                client = Client()
                if actor:
                    login_actor(client, actor)
                for action in ("changelist", "add", "change", "delete"):
                    path = admin_url(model, action, target.pk if action in ("change", "delete") else None)
                    response = client.get(path)
                    self.assertEqual(response.status_code, 302)
                    location = urlsplit(response.headers["Location"])
                    self.assertEqual(location.path, reverse("admin:login"))
                    self.assertEqual(parse_qs(location.query)["next"], [path])
                    self.assertNotIn(b"Target", response.content)
                if actor is None:
                    self.assertNotIn("_auth_user_id", client.session)
            assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())

    def test_staff_without_view_or_change_cannot_list_models(self):
        actor = self.staff(actions=())
        login_actor(self.client, actor)
        for model in MODELS:
            target = create(model)
            before = snapshot_scope([target])
            for action in ("changelist", "change"):
                response = self.client.get(admin_url(model, action, target.pk if action == "change" else None))
                self.assertEqual(response.status_code, 403)
            assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())
        self.identity(actor=actor)

    def test_view_permission_allows_read_without_writes(self):
        actor = self.staff(models=(AnnouncementAlert,), actions=("view",))
        login_actor(self.client, actor)
        target = create(AnnouncementAlert, "View me")
        before = snapshot_scope([target])
        listing = self.client.get(admin_url(AnnouncementAlert, "changelist"))
        detail = self.client.get(admin_url(AnnouncementAlert, "change", target.pk))
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(detail.status_code, 200)
        self.assertFalse(detail.context["has_change_permission"])
        self.assertFalse(detail.context["has_add_permission"])
        self.assertFalse(detail.context["has_delete_permission"])
        self.assertEqual(set(detail.context["adminform"].form.fields), set())
        self.assertEqual(self.client.get(admin_url(DayLightSavingsAlert, "changelist")).status_code, 403)
        assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())
        self.identity(actor=actor)

    def test_add_permission_is_required_for_direct_add_post(self):
        for model in MODELS:
            actor = self.staff(models=(model,), actions=("view",))
            login_actor(self.client, actor)
            self.assertEqual(self.client.get(admin_url(model, "add")).status_code, 403)
            self.denied_post(model, actor, "add")

    def test_change_permission_is_required_for_direct_edit_post(self):
        for model in MODELS:
            actor = self.staff(models=(model,), actions=("view", "add"))
            target = create(model, "Keep")
            self.denied_post(model, actor, "change", target)

    def test_delete_permission_is_required_for_detail_delete(self):
        for model in MODELS:
            actor = self.staff(models=(model,), actions=("view", "add", "change"))
            target = create(model, "Keep")
            login_actor(self.client, actor)
            self.assertEqual(self.client.get(admin_url(model, "delete", target.pk)).status_code, 403)
            self.denied_post(model, actor, "delete", target)

    def test_hidden_bulk_delete_cannot_bypass_delete_permission(self):
        for model in MODELS:
            actor = self.staff(models=(model,), actions=("view", "change"))
            login_actor(self.client, actor)
            target, other = create(model, "Target"), create(model, "Other")
            before = snapshot_scope([target, other])
            response = self.client.post(admin_url(model, "changelist"), {
                "action": "delete_selected", "_selected_action": [target.pk], "post": "yes"})
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(response.context["action_form"])
            self.assertNotContains(response, "Are you sure")
            self.assertNotContains(response, "Successfully deleted")
            assert_unchanged(before)
            self.identity(actor=actor)
        self.assertFalse(LogEntry.objects.exists())

    def test_permissions_are_isolated_by_model(self):
        for granted, denied in ((MODELS[0], MODELS[1]), (MODELS[1], MODELS[0])):
            actor = self.staff(models=(granted,))
            login_actor(self.client, actor)
            target = create(denied)
            before = snapshot_scope([target])
            for action in ("changelist", "add", "change", "delete", "history"):
                response = self.client.get(admin_url(denied, action,
                    target.pk if action in ("change", "delete", "history") else None))
                self.assertEqual(response.status_code, 403)
            for action in ("add", "change", "delete"):
                self.denied_post(denied, actor, action, None if action == "add" else target)
            assert_unchanged(before)

    def test_chapter_role_and_record_creator_do_not_restrict_admin_read(self):
        creator = self.staff(models=(AnnouncementAlert,))
        targets = []
        for actor in (self.actor, creator):
            login_actor(self.client, actor)
            response = self.client.post(admin_url(AnnouncementAlert, "add"), payload(
                AnnouncementAlert, f"By-{actor.pk}", _save="1"))
            self.assertEqual(response.status_code, 302)
            target = AnnouncementAlert.objects.get(title=f"By-{actor.pk}")
            self.assertEqual(LogEntry.objects.get(object_id=str(target.pk)).user_id, actor.pk)
            targets.append(target)
        before = snapshot_scope(targets)
        logs = list(LogEntry.objects.values())
        editor = self.staff(models=(AnnouncementAlert,), actions=("view", "change"))
        login_actor(self.client, editor)
        self.assertFalse(editor.brother_profile.roles.exists())
        self.assertEqual(self.client.get(admin_url(AnnouncementAlert, "changelist")).status_code, 200)
        for target in targets:
            response = self.client.get(admin_url(AnnouncementAlert, "change", target.pk))
            self.assertContains(response, target.title)
        assert_unchanged(before)
        self.assertEqual(list(LogEntry.objects.values()), logs)
        self.identity(actor=editor)

    def test_delete_only_permission_does_not_grant_changelist(self):
        for model in MODELS:
            actor = self.staff(models=(model,), actions=("delete",))
            login_actor(self.client, actor)
            target = create(model)
            before = snapshot_scope([target])
            self.assertEqual(self.client.get(admin_url(model, "delete", target.pk)).status_code, 200)
            self.assertEqual(self.client.get(admin_url(model, "changelist")).status_code, 403)
            assert_unchanged(before)
            self.identity(actor=actor)
        self.assertFalse(LogEntry.objects.exists())

    def test_synthetic_superuser_can_read_both_models(self):
        actor = self.staff(actions=(), is_superuser=True)
        login_actor(self.client, actor)
        for model in MODELS:
            target = create(model)
            before = snapshot_scope([target])
            for action in ("changelist", "add", "change", "delete", "history"):
                response = self.client.get(admin_url(model, action,
                    target.pk if action in ("change", "delete", "history") else None))
                self.assertEqual(response.status_code, 200)
            assert_unchanged(before)
        self.assertFalse(LogEntry.objects.exists())
        self.identity(actor=actor)

    def test_admin_does_not_require_member_profile(self):
        actor = self.staff(models=(AnnouncementAlert,), actions=("view", "change"), with_profile=False)
        login_actor(self.client, actor)
        target = create(AnnouncementAlert, "Before")
        created = target.created_at
        self.assertEqual(self.client.get(admin_url(AnnouncementAlert, "change", target.pk)).status_code, 200)
        response = self.client.post(admin_url(AnnouncementAlert, "change", target.pk),
                                    payload(AnnouncementAlert, "After", _save="1"))
        self.assert_redirect(response, admin_url(AnnouncementAlert, "changelist"))
        target.refresh_from_db()
        self.assertEqual((target.title, target.content, target.created_at), ("After", "Text", created))
        self.assertFalse(type(self.actor.brother_profile).objects.filter(user=actor).exists())
        self.assert_log(target, 2, actor=actor)
        self.identity(actor=actor)
