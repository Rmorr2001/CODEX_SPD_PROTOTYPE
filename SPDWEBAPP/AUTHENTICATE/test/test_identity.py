"""Identity constraints/forms and shared ALL-role contract, not endpoint policies."""
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.db import IntegrityError, transaction
from django.test import Client, override_settings
from django.urls import reverse

from AUTHENTICATE.forms import CreateUserForm
from AUTHENTICATE.models import Brother_Profile, Major, Role
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from .support import IdentityCase, member_state, set_roles
from . import role_urls


class IdentityTests(IdentityCase):
    def test_identity_role_and_profile_constraints(self):
        Role.objects.create(name="ACTIVE")
        before = self.pair_snapshot()
        for model, fields in [(Role, {"name": "ACTIVE"}), (Brother_Profile, {"user": self.a})]:
            with self.subTest(model=model.__name__):
                count = model.objects.count()
                with self.assertRaises(IntegrityError), transaction.atomic():
                    model.objects.create(**fields)
                self.assertEqual(model.objects.count(), count)
                self.assert_pair_unchanged(before)

    def test_user_delete_profile_cascade(self):
        set_roles(self.a, ("ACTIVE",))
        set_roles(self.b, ("ACTIVE",))
        major = self.major("Physics", self.a)
        self.b.brother_profile.majors.add(major)
        b_before = member_state(self.b)
        user_pk, profile_pk = self.a.pk, self.a.brother_profile.pk
        role = Role.objects.get(name="ACTIVE")
        self.a.delete()
        self.assertFalse(User.objects.filter(pk=user_pk).exists())
        self.assertFalse(Brother_Profile.objects.filter(pk=profile_pk).exists())
        self.assertFalse(Brother_Profile.roles.through.objects.filter(brother_profile_id=profile_pk).exists())
        self.assertFalse(Brother_Profile.majors.through.objects.filter(brother_profile_id=profile_pk).exists())
        self.assertTrue(Major.objects.filter(pk=major.pk).exists())
        self.assertTrue(Role.objects.filter(pk=role.pk).exists())
        self.assert_member_unchanged(b_before, self.b)

    def creation_data(self):
        return {"email": "created@example.invalid", "username": "created-a",
                "password1": "Distinct-Test-22!word", "password2": "Distinct-Test-22!word"}

    def test_creation_form_hashes_without_privileges(self):
        before = self.pair_snapshot()
        counts = (Role.objects.count(), Major.objects.count(), Brother_Profile.objects.count())
        form = CreateUserForm(self.creation_data())
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(User.objects.get(pk=user.pk).check_password("Distinct-Test-22!word"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(Brother_Profile.objects.filter(user=user).exists())
        self.assertEqual((Role.objects.count(), Major.objects.count(), Brother_Profile.objects.count()), counts)
        self.assert_pair_unchanged(before)

    def test_creation_form_validation(self):
        before = self.pair_snapshot()
        count = User.objects.count()
        variants = [("email", "not-email"), ("username", self.b.username), ("password2", "different")]
        for field, value in variants:
            with self.subTest(field=field):
                form = CreateUserForm({**self.creation_data(), field: value})
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)
        self.assertEqual(User.objects.count(), count)
        self.assert_pair_unchanged(before)


@override_settings(ROOT_URLCONF="AUTHENTICATE.test.role_urls")
class RoleGateTests(IdentityCase):
    def setUp(self):
        super().setUp()
        role_urls.calls.clear()

    def assert_denied(self, response, location, message):
        self.assertRedirects(response, location, fetch_redirect_response=False)
        self.assertEqual([str(m) for m in get_messages(response.wsgi_request)], [message])
        self.assertEqual(role_urls.calls, [])

    def test_all_role_gate_requires_each_role(self):
        both = "Access denied. You are missing the following required roles: 'EXEC', 'ACTIVE'"
        variants = [
            ((), False, both), (("EXEC",), False, "Access denied. You are missing the following required role: 'ACTIVE'"),
            (("ACTIVE",), False, "Access denied. You are missing the following required role: 'EXEC'"),
            (("PHIL_CHAIR",), False, both), (("NM_BOARD",), False, both), (("NME",), False, both),
            (("PHIL_CHAIR", "ACTIVE"), False, "Access denied. You are missing the following required role: 'EXEC'"),
            ((), True, both),
        ]
        for roles, superuser, message in variants:
            with self.subTest(roles=roles, superuser=superuser):
                User.objects.filter(pk=self.a.pk).update(is_superuser=superuser)
                self.a.refresh_from_db()
                set_roles(self.a, roles)
                client = Client()
                self.login(client=client)
                before = self.pair_snapshot()
                self.assert_denied(client.get("/test-role-gate/"), "/legacy/", message)
                self.assert_identity(client, self.a)
                self.assert_pair_unchanged(before)

    def test_all_role_gate_accepts_complete_set(self):
        set_roles(self.a, ("EXEC", "ACTIVE"))
        self.login()
        before = self.pair_snapshot()
        response = self.client.get("/test-role-gate/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"reached")
        self.assertEqual(role_urls.calls, [self.a.pk])
        self.assertEqual(list(get_messages(response.wsgi_request)), [])
        self.assert_identity(self.client, self.a)
        self.assert_pair_unchanged(before)

    def test_role_gate_anonymous_and_missing_profile(self):
        no_profile = make_user(username="no-profile", with_profile=False)
        self.assert_denied(self.client.get("/test-role-gate/"), reverse("login"),
                           "You must be logged in to access this page.")
        self.assert_identity(self.client, None)
        self.client = Client()
        self.login(user=no_profile)
        before, pair = member_state(no_profile), self.pair_snapshot()
        self.assert_denied(self.client.get("/test-role-gate/"), "/legacy/", "User profile not found.")
        self.assert_identity(self.client, no_profile)
        self.assertFalse(Brother_Profile.objects.filter(user=no_profile).exists())
        self.assert_member_unchanged(before, no_profile)
        self.assert_pair_unchanged(pair)

    def test_role_gate_local_referrer(self):
        set_roles(self.a, ("ACTIVE",))
        self.login()
        before = self.pair_snapshot()
        self.assert_denied(self.client.get("/test-role-gate/", HTTP_REFERER="/auth/dashboard/"),
                           "/auth/dashboard/", "Access denied. You are missing the following required role: 'EXEC'")
        self.assert_identity(self.client, self.a)
        self.assert_pair_unchanged(before)
