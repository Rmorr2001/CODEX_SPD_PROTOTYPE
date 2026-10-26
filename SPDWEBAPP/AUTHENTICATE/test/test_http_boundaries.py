"""Authentication, foreign-target isolation and real CSRF middleware matrices."""
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from AUTHENTICATE.models import Brother_Profile, Major
from SPDWEBAPP_CORE.testing.factories import TEST_PASSWORD
from SPDWEBAPP_CORE.testing.helpers import csrf_client
from .support import (IdentityCase, PROFILE_DATA, attach_image, image_upload,
                      member_state, real_token, set_roles)

OPERATIONS = ("change-password", "update_profile", "update_photo", "reset-photo",
              "update_majors", "add-custom-major")


class HttpBoundaryTests(IdentityCase):
    def files(self):
        return {str(p.relative_to(self.media_root)): p.read_bytes()
                for p in self.media_root.rglob("*") if p.is_file()}

    def request(self, client, operation, token=None, target=None):
        headers, form = {}, {}
        if token is not None:
            headers["HTTP_X_CSRFTOKEN"] = token
            form["csrfmiddlewaretoken"] = token
        foreign = {"user_id": target.pk} if target else {}
        if operation == "change-password":
            data = {"current_password": TEST_PASSWORD, "new_password1": "Replacement-22!word",
                    "new_password2": "Replacement-22!word", **foreign}
        elif operation == "update_majors":
            data = {"majors": ["Physics"] if target else [], **foreign}
        elif operation == "add-custom-major":
            data = {"major_name": "Astronomy", **foreign}
        elif operation == "update_profile":
            data = {**PROFILE_DATA, **form, **foreign}
        elif operation == "update_photo":
            data = {"profile_photo": image_upload(), **form, **foreign}
        else:
            data = {**form, **foreign}
        if operation in ("change-password", "update_majors", "add-custom-major"):
            return client.post(f"/auth/{operation}/", data, content_type="application/json", **headers)
        return client.post(f"/auth/{operation}/", data, **headers)

    def assert_login_redirect(self, response, path):
        self.assertEqual(response.status_code, 302)
        parts = urlsplit(response.url)
        self.assertEqual(parts.path, reverse("login"))
        self.assertEqual(parse_qs(parts.query), {"next": [path]})

    def test_anonymous_protected_routes(self):
        attach_image(self.a)
        attach_image(self.b, "other.png", "blue")
        before, files = self.pair_snapshot(), self.files()
        paths = ("dashboard", "roster", "alumni_roster", "profile", *OPERATIONS)
        for route in paths:
            with self.subTest(route=route):
                path = f"/auth/{route}/"
                response = self.client.get(path)
                self.assert_login_redirect(response, path)
                self.assertNotContains(response, "Town B", status_code=302)
                self.assert_identity(self.client, None)
                self.assert_pair_unchanged(before)
                self.assertEqual(self.files(), files)

    def test_anonymous_protected_post_routes(self):
        attach_image(self.a)
        attach_image(self.b, "other.png", "blue")
        client = csrf_client()
        token = real_token(client, "/auth/login/")
        before, files = self.pair_snapshot(), self.files()
        catalog = list(Major.objects.order_by("pk").values())
        for operation in OPERATIONS:
            with self.subTest(operation=operation):
                response = self.request(client, operation, token)
                self.assert_login_redirect(response, f"/auth/{operation}/")
                self.assert_identity(client, None)
                self.assert_pair_unchanged(before)
                self.assertEqual(self.files(), files)
                self.assertEqual(list(Major.objects.order_by("pk").values()), catalog)

    def test_own_mutations_ignore_foreign_target_fields(self):
        set_roles(self.a, ("ACTIVE",))
        self.major("Old", self.a)
        self.major("Other", self.b)
        b_path = attach_image(self.b, "other.png", "blue")
        self.login()
        for operation in ("update_majors", "reset-photo", "update_photo"):
            with self.subTest(operation=operation):
                attach_image(self.a)
                before, b_bytes = self.pair_snapshot(), b_path.read_bytes()
                response = self.request(self.client, operation, target=self.b)
                if operation == "update_photo":
                    self.assertRedirects(response, reverse("profile"), fetch_redirect_response=False)
                    self.decode_image(self.a, (40, 40), "PNG")
                    self.assert_pair_unchanged(before, profile_fields=("profileImage",))
                elif operation == "reset-photo":
                    self.assert_json(response, {"success": True, "message": "Profile photo reset successfully"})
                    self.assertFalse(Brother_Profile.objects.get(user=self.a).profileImage)
                    self.assert_pair_unchanged(before, profile_fields=("profileImage",))
                else:
                    self.assert_json(response, {"success": True, "message": "Majors updated successfully"})
                    self.assertEqual(list(self.a.brother_profile.majors.values_list("name", flat=True)), ["Physics"])
                    self.assert_pair_unchanged(before, relations=("majors",))
                self.assertEqual(b_path.read_bytes(), b_bytes)

    def test_csrf_rejects_profile_mutation_tokens(self):
        attach_image(self.a)
        attach_image(self.b, "other.png", "blue")
        for operation in OPERATIONS:
            for token_kind in (None, "invalid"):
                with self.subTest(operation=operation, token=token_kind):
                    client = csrf_client()
                    self.login(client=client)
                    real_token(client, secure=True)
                    before, files = self.pair_snapshot(), self.files()
                    catalog = list(Major.objects.order_by("pk").values())
                    response = self.request(client, operation, token_kind)
                    self.assertEqual(response.status_code, 403)
                    self.assert_identity(client, self.a)
                    self.assert_pair_unchanged(before)
                    self.assertEqual(self.files(), files)
                    self.assertEqual(list(Major.objects.order_by("pk").values()), catalog)

    def test_csrf_accepts_real_profile_tokens(self):
        for operation in OPERATIONS:
            with self.subTest(operation=operation):
                client = csrf_client()
                self.login(client=client)
                token = real_token(client, secure=True)
                before, catalog = self.pair_snapshot(), Major.objects.count()
                response = self.request(client, operation, token)
                if operation == "update_photo":
                    self.assertRedirects(response, reverse("profile"), fetch_redirect_response=False)
                    self.decode_image(self.a, (40, 40), "PNG")
                    self.assert_pair_unchanged(before, profile_fields=("profileImage",))
                else:
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(response.json()["success"])
                    if operation == "change-password":
                        self.a.refresh_from_db()
                        self.assertTrue(self.a.check_password("Replacement-22!word"))
                        self.assertFalse(self.a.check_password(TEST_PASSWORD))
                        self.assert_pair_unchanged(before, user_fields=("password",))
                    elif operation == "update_profile":
                        self.a.refresh_from_db()
                        self.assertEqual((self.a.username, self.a.email),
                                         (PROFILE_DATA["username"], PROFILE_DATA["email"]))
                        profile = Brother_Profile.objects.get(user=self.a)
                        for field in ("firstName", "lastName", "hometown", "pclass"):
                            self.assertEqual(getattr(profile, field), PROFILE_DATA[field])
                        self.assert_pair_unchanged(before, user_fields=("username", "email"),
                            profile_fields=("firstName", "lastName", "hometown", "pclass"))
                    elif operation == "reset-photo":
                        self.assertFalse(Brother_Profile.objects.get(user=self.a).profileImage)
                        self.assert_pair_unchanged(before, profile_fields=("profileImage",))
                    elif operation == "update_majors":
                        self.assertFalse(self.a.brother_profile.majors.exists())
                        self.assert_pair_unchanged(before, relations=("majors",))
                    else:
                        row = Major.objects.get(pk=response.json()["major_id"])
                        self.assertEqual(row.name, "Astronomy")
                        self.assertEqual(Major.objects.count(), catalog + 1)
                        self.assert_pair_unchanged(before)
                self.assert_identity(client, self.a)

    def test_login_csrf_token_boundary(self):
        for kind in ("absent", "bad", "matching"):
            with self.subTest(token=kind):
                client = csrf_client()
                token = real_token(client, "/auth/login/")
                before = self.pair_snapshot()
                payload = {"username": self.a.username, "password": TEST_PASSWORD}
                if kind != "absent":
                    payload["csrfmiddlewaretoken"] = token if kind == "matching" else "invalid"
                response = client.post("/auth/login/", payload)
                if kind == "matching":
                    self.assertRedirects(response, "/app/dashboard", fetch_redirect_response=False)
                    self.assert_identity(client, self.a)
                    self.assert_pair_unchanged(before, user_fields=("last_login",))
                else:
                    self.assertEqual(response.status_code, 403)
                    self.assert_identity(client, None)
                    self.assert_pair_unchanged(before)
