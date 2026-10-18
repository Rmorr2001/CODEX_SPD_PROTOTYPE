"""Core Django admin identity permissions, separate from the public demo boundary."""
from django.contrib import admin
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from AUTHENTICATE.admin import Brother_ProfileAdmin
from AUTHENTICATE.models import Brother_Profile, Role, Major, DashboardLink
from SPDWEBAPP_CORE.testing.helpers import csrf_client
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from .support import IdentityCase, member_state, real_token, set_roles


class AdminTests(IdentityCase):
    def setUp(self):
        super().setUp()
        self.role = Role.objects.create(name="ACTIVE")
        self.major_row = self.major("Physics", self.b)
        self.link = DashboardLink.objects.create(text="First", link="/first/", order=1)
        self.b.brother_profile.roles.add(self.role)
        self.targets = [self.b, self.b.brother_profile, self.role, self.major_row, self.link]

    def change_url(self, obj):
        return reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.pk])

    def grant(self, *names):
        User.objects.filter(pk=self.a.pk).update(is_staff=True)
        self.a.refresh_from_db()
        self.a.user_permissions.add(*[Permission.objects.get(
            content_type__app_label=app, codename=code) for app, code in names])

    def admin_client(self):
        client = csrf_client()
        self.login(client=client)
        token = real_token(client, "/auth/login/")
        return client, token

    def test_admin_rejects_nonstaff_domain_executive(self):
        set_roles(self.a, ("EXEC", "ACTIVE"))
        client, token = self.admin_client()
        before = self.pair_snapshot()
        target_state = snapshot_scope(self.targets)
        for obj in self.targets:
            urls = [self.change_url(obj), reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_changelist")]
            for url in urls:
                for method in ("get", "post"):
                    with self.subTest(model=obj._meta.label, url=url, method=method):
                        response = getattr(client, method)(url, {} if method == "get" else {"csrfmiddlewaretoken": token})
                        self.assertEqual(response.status_code, 302)
                        self.assertTrue(response.url.startswith(reverse("admin:login") + "?next="))
        assert_unchanged(target_state)
        self.assertFalse(LogEntry.objects.exists())
        self.assert_identity(client, self.a)
        self.assert_pair_unchanged(before)

    def test_admin_staff_without_model_permissions(self):
        self.grant()
        client, token = self.admin_client()
        before = self.pair_snapshot()
        state = snapshot_scope(self.targets)
        for obj in self.targets:
            for method in ("get", "post"):
                with self.subTest(model=obj._meta.label, method=method):
                    response = getattr(client, method)(self.change_url(obj),
                        {} if method == "get" else {"csrfmiddlewaretoken": token})
                    self.assertEqual(response.status_code, 403)
                    self.assertNotContains(response, "CSRF verification failed", status_code=403)
        assert_unchanged(state)
        self.assertFalse(LogEntry.objects.exists())
        self.assert_pair_unchanged(before)

    def test_admin_forged_user_privilege_fields(self):
        self.grant(("auth", "change_user"))
        client, token = self.admin_client()
        before = self.pair_snapshot()
        response = client.post(self.change_url(self.b), {
            "csrfmiddlewaretoken": token, "username": self.b.username, "email": self.b.email,
            "first_name": self.b.first_name, "last_name": self.b.last_name, "_save": "Save",
            "is_staff": "true", "is_superuser": "true", "brother_profile": self.a.brother_profile.pk})
        self.assertRedirects(response, reverse("admin:auth_user_changelist"), fetch_redirect_response=False)
        self.assert_pair_unchanged(before)
        self.assertFalse(User.objects.get(pk=self.b.pk).is_staff)
        self.assertFalse(User.objects.get(pk=self.b.pk).is_superuser)
        self.assertEqual(LogEntry.objects.get().action_flag, CHANGE)
        self.assertEqual(LogEntry.objects.get().object_id, str(self.b.pk))

    def test_admin_major_and_link_edit(self):
        self.grant(("AUTHENTICATE", "change_major"), ("AUTHENTICATE", "change_dashboardlink"))
        second = DashboardLink.objects.create(text="Second", link="/second/", order=2)
        client, token = self.admin_client()
        before = self.pair_snapshot()
        state = snapshot_scope([self.role, self.link])
        response = client.post(self.change_url(self.major_row), {
            "name": "Applied Physics", "_save": "Save", "csrfmiddlewaretoken": token})
        self.assertRedirects(response, reverse("admin:AUTHENTICATE_major_changelist"), fetch_redirect_response=False)
        self.assertEqual(Major.objects.get(pk=self.major_row.pk).name, "Applied Physics")
        self.assertEqual(list(self.b.brother_profile.majors.values_list("pk", flat=True)), [self.major_row.pk])
        log = LogEntry.objects.get()
        self.assertEqual((log.object_id, log.action_flag), (str(self.major_row.pk), CHANGE))
        response = client.post(reverse("admin:AUTHENTICATE_dashboardlink_sortable_update"), {
            "updatedItems": [[second.pk, 0]]}, content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Updated 1 items")
        self.assertEqual(list(DashboardLink.objects.values_list("pk", flat=True)), [second.pk, self.link.pk])
        self.assertEqual(DashboardLink.objects.get(pk=second.pk).order, 0)
        self.assertEqual(LogEntry.objects.count(), 1)
        assert_unchanged(state)
        self.assert_pair_unchanged(before)

    def test_admin_role_invalid_choice(self):
        self.grant(("AUTHENTICATE", "change_role"))
        client, token = self.admin_client()
        before = self.pair_snapshot()
        response = client.post(self.change_url(self.role), {
            "name": "UNDECLARED_ROLE", "_save": "Save", "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.context["adminform"].form.errors)
        self.assertEqual(Role.objects.get(pk=self.role.pk).name, "ACTIVE")
        self.assertFalse(LogEntry.objects.exists())
        self.assert_pair_unchanged(before)

    def test_model_admin_display_labels(self):
        Brother_Profile.objects.filter(user=self.b).update(firstName=None, lastName=None)
        profile = Brother_Profile.objects.get(user=self.b)
        before, state = self.pair_snapshot(), snapshot_scope([self.role, self.major_row, self.link])
        profile_admin = Brother_ProfileAdmin(Brother_Profile, admin.site)
        self.assertEqual(str(self.role), "Active Member")
        self.assertEqual(str(self.major_row), "Physics")
        self.assertEqual(str(profile), "None None")
        self.assertEqual(str(self.link), "First")
        self.assertEqual(profile_admin.get_roles(profile), "Active Member")
        self.assertEqual(profile_admin.get_majors(profile), "Physics")
        assert_unchanged(state)
        self.assert_pair_unchanged(before)

    def test_admin_superuser_without_domain_roles(self):
        User.objects.filter(pk=self.a.pk).update(is_staff=True, is_superuser=True)
        self.a.refresh_from_db()
        self.login()
        before, state = self.pair_snapshot(), snapshot_scope(self.targets)
        for obj in self.targets:
            with self.subTest(model=obj._meta.label):
                response = self.client.get(self.change_url(obj))
                self.assertEqual(response.status_code, 200)
                self.assertIn("adminform", response.context)
        self.assertFalse(self.a.brother_profile.roles.exists())
        self.assertFalse(LogEntry.objects.exists())
        assert_unchanged(state)
        self.assert_pair_unchanged(before)
