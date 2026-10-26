"""Real credential/session behavior; unresolved transport policies stay in docs."""
from datetime import datetime, timezone
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse

from AUTHENTICATE.models import Brother_Profile
from SPDWEBAPP_CORE.testing.factories import TEST_PASSWORD, make_user
from SPDWEBAPP_CORE.testing.helpers import csrf_client, at_time
from .support import IdentityCase, FormInputs, member_state, real_token, set_roles

NEW_PASSWORD = "Replacement-22!word"
CLOCK = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)


class SessionTests(IdentityCase):
    def setUp(self):
        super().setUp()
        self.enterContext(at_time(CLOCK))

    def credentials(self, client=None, user=None, **kwargs):
        user = user or self.a
        with at_time(CLOCK):
            return (client or self.client).post("/auth/login/", {
                "username": user.username, "password": TEST_PASSWORD}, **kwargs)

    def change(self, client=None, current=TEST_PASSWORD, new=NEW_PASSWORD, confirm=NEW_PASSWORD):
        return (client or self.client).post("/auth/change-password/", {
            "current_password": current, "new_password1": new,
            "new_password2": confirm}, content_type="application/json")

    def assert_invalid(self, response):
        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)
        self.assertEqual([str(m) for m in get_messages(response.wsgi_request)],
                         ["Invalid username or password."])

    def test_login_form(self):
        before = self.pair_snapshot()
        counts = (User.objects.count(), Brother_Profile.objects.count())
        response = self.client.get("/auth/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "AUTHENTICATE/login.html")
        inputs = FormInputs(response.content).inputs
        self.assertEqual(inputs["username"]["type"], "text")
        self.assertEqual(inputs["password"]["type"], "password")
        self.assertTrue(inputs["csrfmiddlewaretoken"]["value"])
        self.assert_identity(self.client, None)
        self.assertEqual((User.objects.count(), Brother_Profile.objects.count()), counts)
        self.assert_pair_unchanged(before)

    def test_password_login_home(self):
        before = self.pair_snapshot()
        session = self.client.session
        session["marker"] = "before"
        session.save()
        old_key = session.session_key
        response = self.credentials()
        self.assertRedirects(response, "/app/dashboard", fetch_redirect_response=False)
        self.assert_identity(self.client, self.a)
        self.assertNotEqual(self.client.session.session_key, old_key)
        self.a.refresh_from_db()
        self.assertEqual(self.a.last_login, CLOCK)
        self.assert_pair_unchanged(before, user_fields=("last_login",))

    def test_password_login_local_next(self):
        before = self.pair_snapshot()
        with at_time(CLOCK):
            response = self.client.post("/auth/login/?next=/auth/roster/%3Fx%3D1", {
                "username": "actor-a", "password": TEST_PASSWORD})
        self.assertRedirects(response, "/auth/roster/?x=1", fetch_redirect_response=False)
        self.assert_identity(self.client, self.a)
        self.a.refresh_from_db()
        self.assertEqual(self.a.last_login, CLOCK)
        self.assert_pair_unchanged(before, user_fields=("last_login",))

    def test_password_login_without_profile(self):
        user = make_user(username="no-profile", with_profile=False)
        before = member_state(user)
        response = self.credentials(user=user)
        self.assertRedirects(response, "/app/dashboard", fetch_redirect_response=False)
        self.assert_identity(self.client, user)
        self.assertFalse(Brother_Profile.objects.filter(user=user).exists())
        self.assert_member_unchanged(before, user, user_fields=("last_login",))

    def test_reject_bad_login_credentials(self):
        before = self.pair_snapshot()
        payloads = [
            {"username": "actor-a", "password": "wrong"},
            {"username": "", "password": TEST_PASSWORD}, {"password": TEST_PASSWORD},
            {"username": "actor-a", "password": ""}, {"username": "actor-a"},
        ]
        for payload in payloads:
            with self.subTest(payload_fields=tuple(payload), empty_fields=[k for k,v in payload.items() if not v]):
                client = Client()
                self.assert_invalid(client.post("/auth/login/", payload))
                self.assert_identity(client, None)
        self.assert_pair_unchanged(before)

    def test_reject_inactive_login(self):
        inactive = make_user(username="inactive-a", is_active=False)
        before = member_state(inactive)
        self.assert_invalid(self.credentials(user=inactive))
        self.assert_identity(self.client, None)
        self.assert_member_unchanged(before, inactive)

    def test_authenticated_login_get(self):
        self.login()
        before = self.pair_snapshot()
        response = self.client.get("/auth/login/?next=/auth/roster/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "AUTHENTICATE/login.html")
        self.assertNotIn("Location", response)
        self.assert_identity(self.client, self.a)
        self.assert_pair_unchanged(before)

    def test_failed_login_keeps_existing_identity(self):
        self.login()
        before = self.pair_snapshot()
        self.assert_invalid(self.client.post("/auth/login/", {
            "username": self.b.username, "password": "wrong"}))
        self.assert_identity(self.client, self.a)
        self.assert_pair_unchanged(before)

    def test_logout_rejects_bad_csrf(self):
        for bad in (None, "invalid"):
            with self.subTest(token_kind="absent" if bad is None else "bad"):
                client = csrf_client()
                self.login(client=client)
                real_token(client)
                session = client.session
                session["marker"] = "before"
                session.save()
                before = self.pair_snapshot()
                response = client.post("/auth/logout/", {} if bad is None else {"csrfmiddlewaretoken": bad})
                self.assertEqual(response.status_code, 403)
                self.assert_identity(client, self.a)
                self.assertEqual(client.session["marker"], "before")
                self.assert_pair_unchanged(before)

    def test_password_change_keeps_current_session(self):
        roles = [(), ("ACTIVE",), ("EXEC",), ("EXEC", "ACTIVE"),
                 ("PHIL_CHAIR", "ACTIVE"), ("NEW_MEMBER",), ("ALUMNI",)]
        for role_set in roles:
            with self.subTest(roles=role_set):
                User.objects.filter(pk=self.a.pk).update(password=self.b.password)
                self.a.refresh_from_db()
                set_roles(self.a, role_set)
                c1, other = Client(), Client()
                self.assertEqual(self.credentials(client=c1).status_code, 302)
                self.assertEqual(self.credentials(client=other, user=self.b).status_code, 302)
                before = self.pair_snapshot()
                self.assert_json(self.change(client=c1), {"success": True})
                self.a.refresh_from_db()
                self.assertTrue(self.a.check_password(NEW_PASSWORD))
                self.assertFalse(self.a.check_password(TEST_PASSWORD))
                self.assertEqual(c1.get("/auth/profile/").status_code, 200)
                self.assert_identity(c1, self.a)
                self.assert_identity(other, self.b)
                self.assert_pair_unchanged(before, user_fields=("password",))

    def test_password_change_invalidates_other_session(self):
        c1, c2 = Client(), Client()
        self.credentials(client=c1)
        self.credentials(client=c2)
        before = self.pair_snapshot()
        self.assert_json(self.change(client=c1), {"success": True})
        response = c2.get("/auth/profile/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))
        self.assert_identity(c2, None)
        self.assert_identity(c1, self.a)
        self.assert_pair_unchanged(before, user_fields=("password",))

    def test_wrong_current_password(self):
        self.login()
        before = self.pair_snapshot()
        self.assert_json(self.change(current="wrong"), {
            "success": False, "error": "Current password is incorrect."})
        self.assert_identity(self.client, self.a)
        self.assert_pair_unchanged(before)

    def test_password_confirmation_mismatch(self):
        self.login()
        before = self.pair_snapshot()
        self.assert_json(self.change(confirm="different"), {
            "success": False, "error": "New passwords do not match."})
        self.assert_identity(self.client, self.a)
        self.assert_pair_unchanged(before)

    def test_password_change_without_profile(self):
        user = make_user(username="no-profile", with_profile=False)
        self.credentials(user=user)
        before, b_before = member_state(user), member_state(self.b)
        self.assert_json(self.change(), {"success": True})
        user.refresh_from_db()
        self.assertTrue(user.check_password(NEW_PASSWORD))
        self.assertFalse(user.check_password(TEST_PASSWORD))
        self.assert_identity(self.client, user)
        self.assert_member_unchanged(before, user, user_fields=("password",))
        self.assert_member_unchanged(b_before, self.b)
        self.assertFalse(Brother_Profile.objects.filter(user=user).exists())
