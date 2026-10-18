import json
from unittest.mock import patch

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.models import Permission
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from HOME.models import BannerImage, RushFormLink, RushSlide
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import csrf_client, login_actor
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope

from .helpers import file_path, image_bytes, slide, upload


MODELS = (BannerImage, RushFormLink, RushSlide)


def admin_url(model, action, obj=None):
    name = f"admin:{model._meta.app_label}_{model._meta.model_name}_{action}"
    return reverse(name, args=[obj.pk] if obj is not None else [])


class AdminTests(RegressionTestCase):
    def setUp(self):
        super().setUp()
        self.banner = BannerImage.objects.create(image=upload("banner.png"))
        self.link = RushFormLink.objects.create(link="https://example.invalid/old")
        self.a, self.b = slide("A", 1), slide("B", 2)
        self.rows = [self.banner, self.link, self.a, self.b]
        self.sequence = 0

    def staff(self, model=None, grants=(), **kwargs):
        self.sequence += 1
        user = make_user(username=f"staff-{self.sequence}", is_staff=True, **kwargs)
        if model:
            for action in grants:
                user.user_permissions.add(Permission.objects.get(
                    content_type__app_label=model._meta.app_label,
                    codename=f"{action}_{model._meta.model_name}"))
        return user

    def client_for(self, user):
        client = csrf_client()
        login_actor(client, user)
        response = client.get(reverse("admin:login"))
        # Already authenticated staff may be redirected. Add form always renders csrf.
        if "csrftoken" not in client.cookies:
            client.get(reverse("admin:index"))
        self.assertIn("csrftoken", client.cookies)
        return client

    def post(self, client, url, data):
        return client.post(url, {**data, "csrfmiddlewaretoken": client.cookies["csrftoken"].value})

    def before(self):
        return snapshot_scope(self.rows, files=[file_path(self.banner.image),
                                              file_path(self.a.image), file_path(self.b.image)])

    def unchanged_for(self, model, target=None):
        rows = [row for kind in MODELS for row in kind.objects.all()
                if kind is not model or (model is RushSlide and row.pk != getattr(target, "pk", None))]
        return snapshot_scope(rows, files=[file_path(row.image) for row in rows if hasattr(row, "image")])

    def payload(self, model, changed=False):
        if model is RushFormLink:
            return {"link": "https://example.invalid/new"}
        payload = {"image": upload("new.png", "blue")}
        if model is RushSlide:
            payload["caption"] = "x" * 200 if not changed else "Changed"
        return payload

    def test_admin_anonymous_and_nonstaff_are_denied(self):
        before = self.before()
        actors = [None] + [make_user(username=f"nonstaff-{i}", roles=roles)
                          for i, roles in enumerate((("ACTIVE",), ("EXEC",), ()))]
        actors[-1].user_permissions.set(Permission.objects.filter(content_type__app_label="HOME"))
        for actor in actors:
            client = csrf_client()
            if actor:
                login_actor(client, actor)
            for model in MODELS:
                obj = model.objects.first()
                for action in ("changelist", "add", "change", "delete", "history"):
                    url = admin_url(model, action, obj if action in ("change", "delete", "history") else None)
                    response = client.get(url)
                    self.assertEqual(response.status_code, 302)
                    self.assertTrue(response.url.startswith(reverse("admin:login") + "?next="))
                # CSRF token acquired from the real login form; admission still denies.
                client.get(reverse("admin:login"))
                response = self.post(client, admin_url(model, "change", obj), self.payload(model))
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("admin:login")))
            self.assertEqual(client.session.get("_auth_user_id"), str(actor.pk) if actor else None)
        self.assertEqual(LogEntry.objects.count(), 0)
        assert_unchanged(before)

    def test_admin_individual_model_permissions_are_distinct(self):
        before = self.before()
        for model in MODELS:
            obj = model.objects.first()
            for grant in (None, "view", "add", "change", "delete"):
                client = self.client_for(self.staff(model, () if grant is None else (grant,)))
                allowed = {"add": "add", "change": "change", "delete": "delete"}
                for action, required in allowed.items():
                    if grant != required:
                        response = self.post(client, admin_url(model, action, None if action == "add" else obj), {})
                        self.assertEqual(response.status_code, 403, (model, grant, action))
                if grant in ("view", "change"):
                    self.assertEqual(client.get(admin_url(model, "changelist")).status_code, 200)
                    self.assertEqual(client.get(admin_url(model, "change", obj)).status_code, 200)
        self.assertEqual(LogEntry.objects.count(), 0)
        assert_unchanged(before)

    def test_admin_unsafe_requests_require_real_csrf(self):
        before = self.before()
        client = self.client_for(self.staff(is_superuser=True))
        for model in MODELS:
            obj = model.objects.first()
            urls = [admin_url(model, "add"), admin_url(model, "change", obj),
                    admin_url(model, "delete", obj), admin_url(model, "changelist")]
            for url in urls:
                for token in (None, "bad-token"):
                    data = {} if token is None else {"csrfmiddlewaretoken": token}
                    self.assertEqual(client.post(url, data).status_code, 403)
        for token in (None, "bad-token"):
            headers = {} if token is None else {"HTTP_X_CSRFTOKEN": token}
            response = client.post(reverse("admin:HOME_rushslide_sortable_update"),
                                   data=json.dumps({"updatedItems": []}),
                                   content_type="application/json", **headers)
            self.assertEqual(response.status_code, 403)
        self.assertEqual(LogEntry.objects.count(), 0)
        assert_unchanged(before)

    def test_admin_superuser_can_read_home_models(self):
        before = self.before()
        actor = self.staff(is_superuser=True)
        self.assertFalse(actor.brother_profile.roles.exists())
        client = self.client_for(actor)
        for model in MODELS:
            obj = model.objects.first()
            for action in ("changelist", "change", "history"):
                response = client.get(admin_url(model, action, None if action == "changelist" else obj))
                self.assertEqual(response.status_code, 200)
        self.assertEqual(LogEntry.objects.count(), 0)
        assert_unchanged(before)

    def test_admin_invalid_forms_do_not_run_singleton_hooks(self):
        before = self.before()
        client = self.client_for(self.staff(is_superuser=True))
        for model in MODELS:
            variants = ([({}, "link"), ({"link": "not-a-url"}, "link"),
                         ({"link": "https://example.invalid/" + "x" * (201 - len("https://example.invalid/"))}, "link")]
                        if model is RushFormLink else [({}, "image"),
                         ({"image": SimpleUploadedFile("bad.png", b"not an image")}, "image")])
            if model is RushSlide:
                variants += [({"caption": "x" * 201, "image": upload()}, "caption"),
                             ({"caption": "", "image": upload()}, "caption")]
            for action in ("add", "change"):
                for payload, field in variants:
                    if action == "change" and not payload and model is not RushFormLink:
                        # Existing image is optional on change; a corrupt new upload is tested above.
                        continue
                    payload = dict(payload)
                    if model is RushSlide and "caption" not in payload:
                        payload["caption"] = "Fixture"
                    if "image" in payload and hasattr(payload["image"], "seek"):
                        payload["image"].seek(0)
                    response = self.post(client, admin_url(model, action, model.objects.first()
                                                          if action == "change" else None), payload)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(field, response.context["adminform"].form.errors)
        self.assertEqual(LogEntry.objects.count(), 0)
        assert_unchanged(before)

    def test_admin_add_creates_home_row_and_audit(self):
        for model in MODELS:
            if model in (BannerImage, RushFormLink):
                model.objects.all().delete()
            before = self.unchanged_for(model)
            actor = self.staff(model, ("add",))
            client = self.client_for(actor)
            response = self.post(client, admin_url(model, "add"), self.payload(model))
            self.assertEqual(response.status_code, 302)
            obj = model.objects.order_by("-pk").first()
            if model is RushFormLink:
                self.assertEqual(obj.link, "https://example.invalid/new")
            else:
                self.assertEqual(file_path(obj.image).read_bytes(), image_bytes("blue"))
            if model is RushSlide:
                self.assertEqual(obj.caption, "x" * 200)
            self.assertTrue(LogEntry.objects.filter(user=actor, object_id=str(obj.pk), action_flag=ADDITION).exists())
            assert_unchanged(before)

    def test_admin_change_updates_home_row_and_audit(self):
        for model in MODELS:
            obj = model.objects.first()
            before = self.unchanged_for(model, obj)
            actor = self.staff(model, ("change",))
            client = self.client_for(actor)
            for _ in range(2):
                response = self.post(client, admin_url(model, "change", obj), self.payload(model, True))
                self.assertEqual(response.status_code, 302)
                obj.refresh_from_db()
            if model is RushFormLink:
                self.assertEqual(obj.link, "https://example.invalid/new")
            else:
                self.assertEqual(file_path(obj.image).read_bytes(), image_bytes("blue"))
                if model is RushSlide:
                    self.assertEqual(obj.caption, "Changed")
            self.assertTrue(LogEntry.objects.filter(user=actor, object_id=str(obj.pk), action_flag=CHANGE).exists())
            assert_unchanged(before)

    def test_admin_delete_confirmation_and_cancel(self):
        for model in MODELS:
            obj = model.objects.first()
            before = snapshot_scope([obj, self.b], files=[file_path(self.b.image)])
            actor = self.staff(model, ("delete",))
            client = self.client_for(actor)
            response = client.get(admin_url(model, "delete", obj))
            self.assertEqual(response.status_code, 200)
            assert_unchanged(before)  # Cancel: user leaves without confirmation.
            pk = obj.pk
            response = self.post(client, admin_url(model, "delete", obj), {"post": "yes"})
            self.assertEqual(response.status_code, 302)
            self.assertFalse(model.objects.filter(pk=pk).exists())
            self.assertTrue(LogEntry.objects.filter(user=actor, object_id=str(pk), action_flag=DELETION).exists())
            self.b.refresh_from_db()
            self.assertEqual(self.b.caption, "B")

    def test_admin_bulk_delete_removes_only_selected_rows(self):
        c = slide("C", 3)
        before = snapshot_scope([c, self.banner, self.link], files=[file_path(c.image)])
        actor = self.staff(RushSlide, ("view", "delete"))
        client = self.client_for(actor)
        url = admin_url(RushSlide, "changelist")
        data = {"action": "delete_selected", "_selected_action": [self.a.pk, self.b.pk]}
        self.assertEqual(self.post(client, url, data).status_code, 200)
        self.assertEqual(RushSlide.objects.count(), 3)
        self.assertEqual(self.post(client, url, {**data, "post": "yes"}).status_code, 302)
        self.assertEqual(set(RushSlide.objects.values_list("pk", flat=True)), {c.pk})
        self.assertEqual(LogEntry.objects.filter(user=actor, action_flag=DELETION).count(), 2)
        assert_unchanged(before)

    def test_admin_stale_object_redirects_without_writes(self):
        client = self.client_for(self.staff(is_superuser=True))
        for model in MODELS:
            obj = model.objects.first()
            pk = obj.pk
            model.objects.filter(pk=pk).delete()
            for action in ("change", "delete"):
                for method in ("get", "post"):
                    url = reverse(f"admin:HOME_{model._meta.model_name}_{action}", args=[pk])
                    response = client.get(url) if method == "get" else self.post(client, url, {})
                    self.assertEqual(response.status_code, 302)
                    self.assertEqual(response.url, reverse("admin:index"))
            self.assertFalse(model.objects.filter(pk=pk).exists())
        self.assertEqual(LogEntry.objects.count(), 0)
        self.assertTrue(RushSlide.objects.filter(pk=self.b.pk).exists())

    def test_admin_db_failure_rolls_back_singleton_and_audit(self):
        for model in (BannerImage, RushFormLink):
            before = self.before()
            client = self.client_for(self.staff(model, ("change",)))
            with patch.object(model, "_do_insert", side_effect=IntegrityError("synthetic insert failure")):
                with self.assertRaises(IntegrityError):
                    self.post(client, admin_url(model, "change", model.objects.first()), self.payload(model, True))
            assert_unchanged(before)
            self.assertEqual(LogEntry.objects.count(), 0)

    def reorder(self, client, payload, raw=False):
        return client.post(reverse("admin:HOME_rushslide_sortable_update"),
                           data=payload if raw else json.dumps(payload), content_type="application/json",
                           HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)

    def test_sortable_requires_post_and_change_permission(self):
        before = self.before()
        client = self.client_for(self.staff(RushSlide, ("change",)))
        self.assertEqual(client.get(reverse("admin:HOME_rushslide_sortable_update")).status_code, 405)
        client = self.client_for(self.staff(RushSlide, ("view",)))
        self.assertEqual(self.reorder(client, {"updatedItems": []}).status_code, 403)
        assert_unchanged(before)
        self.assertEqual(LogEntry.objects.count(), 0)

    def test_sortable_updates_only_named_orders_and_repeats(self):
        c = slide("C", 4)
        before = snapshot_scope([c, self.banner, self.link],
                                files=[file_path(obj.image) for obj in (self.a, self.b, c, self.banner)])
        client = self.client_for(self.staff(RushSlide, ("change",)))
        for _ in range(2):
            response = self.reorder(client, {"updatedItems": [[self.a.pk, 3], [self.b.pk, 1]]})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"Updated 2 items")
            self.a.refresh_from_db()
            self.b.refresh_from_db()
            self.assertEqual((self.a.order, self.b.order, self.a.caption, self.b.caption), (3, 1, "A", "B"))
        assert_unchanged(before)

    def test_sortable_malformed_batches_are_not_partially_written(self):
        before = self.before()
        client = self.client_for(self.staff(RushSlide, ("change",)))
        for payload in ("not-json", "{}", '{"updatedItems":null}', '{"updatedItems":[[]]}',
                        json.dumps({"updatedItems": [[self.a.pk, 9], [99999, 1]]})):
            self.assertEqual(self.reorder(client, payload, raw=True).status_code, 400)
            assert_unchanged(before)

    def test_sortable_empty_batch_is_noop(self):
        before = self.before()
        client = self.client_for(self.staff(RushSlide, ("change",)))
        response = self.reorder(client, {"updatedItems": []})
        self.assertEqual((response.status_code, response.content), (200, b"Updated 0 items"))
        assert_unchanged(before)

    def test_admin_new_slide_uses_maximum_plus_one(self):
        self.a.order, self.b.order = 3, 7
        self.a.save()
        self.b.save()
        before = self.before()
        actor = self.staff(RushSlide, ("add",))
        client = self.client_for(actor)
        self.assertEqual(self.post(client, admin_url(RushSlide, "add"),
                                   {"caption": "Third", "image": upload()}).status_code, 302)
        c = RushSlide.objects.get(caption="Third")
        self.assertEqual(c.order, 8)
        self.assertTrue(LogEntry.objects.filter(user=actor, object_id=str(c.pk), action_flag=ADDITION).exists())
        assert_unchanged(before)
