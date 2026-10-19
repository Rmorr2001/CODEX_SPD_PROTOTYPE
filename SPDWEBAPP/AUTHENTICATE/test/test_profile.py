"""Own-profile fields, template contracts and nondestructive ordinary reads."""
from unittest.mock import patch

from django.contrib.auth.models import User
from AUTHENTICATE.models import Brother_Profile, Major
from .support import (IdentityCase, PROFILE_DATA, ALL_ROLES, FormInputs, attach_image,
                      member_state, set_roles)


class ProfileTests(IdentityCase):
    def assert_profile_update(self, before, payload):
        self.a.refresh_from_db()
        profile = Brother_Profile.objects.get(user=self.a)
        self.assertEqual(self.a.username, payload["username"])
        self.assertEqual(self.a.email, payload["email"])
        for key in ("firstName", "lastName", "hometown", "pclass"):
            self.assertEqual(getattr(profile, key), payload[key])
        self.assert_pair_unchanged(before, user_fields=("username", "email"),
                                   profile_fields=("firstName", "lastName", "hometown", "pclass"))

    def test_edit_own_profile(self):
        self.major("Physics", self.a)
        for roles in ALL_ROLES:
            with self.subTest(roles=roles):
                # Every role variant must exercise a change, rather than an idempotent write.
                Brother_Profile.objects.filter(user=self.a).update(pclass="Beta")
                set_roles(self.a, roles)
                self.login()
                before = self.pair_snapshot()
                self.assert_json(self.client.post("/auth/update_profile/", PROFILE_DATA), {"success": True})
                self.assert_profile_update(before, PROFILE_DATA)

    def test_profile_ignores_target_and_privilege_fields(self):
        set_roles(self.a, ("ACTIVE",))
        self.login()
        before = self.pair_snapshot()
        payload = {**PROFILE_DATA, "user": self.b.pk, "user_id": self.b.pk,
                   "profile_id": self.b.brother_profile.pk, "roles": "EXEC",
                   "is_staff": "true", "is_superuser": "true"}
        self.assert_json(self.client.post("/auth/update_profile/", payload), {"success": True})
        self.assert_profile_update(before, PROFILE_DATA)
        self.assertEqual(list(self.a.brother_profile.roles.values_list("name", flat=True)), ["ACTIVE"])

    def test_repeat_profile_update(self):
        User.objects.filter(pk=self.a.pk).update(username=PROFILE_DATA["username"], email=PROFILE_DATA["email"])
        Brother_Profile.objects.filter(user=self.a).update(**{
            field: PROFILE_DATA[field] for field in ("firstName", "lastName", "hometown", "pclass")})
        self.a.refresh_from_db()
        self.login()
        before = self.pair_snapshot()
        counts = (User.objects.count(), Brother_Profile.objects.count(), Major.objects.count())
        for _ in range(2):
            self.assert_json(self.client.post("/auth/update_profile/", PROFILE_DATA), {"success": True})
        self.assertEqual((User.objects.count(), Brother_Profile.objects.count(), Major.objects.count()), counts)
        self.assert_pair_unchanged(before)

    def test_profile_rejects_blacklist_field(self):
        self.login()
        before = self.pair_snapshot()
        for field in ("username", "firstName", "lastName", "hometown", "pclass"):
            with self.subTest(field=field):
                self.assert_json(self.client.post("/auth/update_profile/", {**PROFILE_DATA, field: "fuck"}), {
                    "success": False, "message": "Input contains inappropriate language."})
                self.assert_pair_unchanged(before)

    def test_profile_get_rejection(self):
        self.login()
        before, count = self.pair_snapshot(), Major.objects.count()
        self.assert_json(self.client.get("/auth/update_profile/"), {"success": False, "message": "Invalid request"})
        self.assert_pair_unchanged(before)
        self.assertEqual(Major.objects.count(), count)

    def test_profile_accepts_exact_whitelist(self):
        self.login()
        before = self.pair_snapshot()
        payload = {**PROFILE_DATA, "hometown": "biological engineering"}
        self.assert_json(self.client.post("/auth/update_profile/", payload), {"success": True})
        self.assert_profile_update(before, payload)

    def test_profile_read_own_context(self):
        self.major("Physics", self.a)
        self.major("Chemistry", self.b)
        self.login()
        before = self.pair_snapshot()
        response = self.client.get("/auth/profile/", {"user_id": self.b.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "AUTHENTICATE/profile.html")
        self.assertEqual(response.context["brother_profile"].pk, self.a.brother_profile.pk)
        inputs = FormInputs(response.content).inputs
        self.assertEqual(inputs["username"]["value"], self.a.username)
        self.assertEqual(inputs["firstName"]["value"], "Alice")
        self.assertNotEqual(inputs["firstName"]["value"], self.b.brother_profile.firstName)
        self.assert_pair_unchanged(before)

    def test_profile_sorted_majors_and_form_payloads(self):
        self.major("Zoology")
        self.major("Chemistry")
        self.login()
        before = self.pair_snapshot()
        response = self.client.get("/auth/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([m.name for m in response.context["available_majors"]], ["Chemistry", "Zoology"])
        parsed = FormInputs(response.content)
        for field in PROFILE_DATA:
            self.assertIn(field, parsed.inputs)
        self.assertEqual(parsed.inputs["profile_photo"]["type"], "file")
        self.assertTrue(parsed.inputs["csrfmiddlewaretoken"]["value"])
        self.assertTrue(any(f.get("enctype") == "multipart/form-data"
                            and f.get("action") == "/auth/update_photo/" for f in parsed.forms))
        self.assert_pair_unchanged(before)

    def test_profile_read_does_not_rewrite_image(self):
        a_path = attach_image(self.a)
        b_path = attach_image(self.b, "other.png", "blue")
        self.login()
        before = self.pair_snapshot()
        a_bytes, b_bytes = a_path.read_bytes(), b_path.read_bytes()
        storage = Brother_Profile.objects.get(user=self.a).profileImage.storage
        with patch.object(storage, "save", wraps=storage.save) as save:
            with patch.object(storage, "delete", wraps=storage.delete) as delete:
                for _ in range(2):
                    response = self.client.get("/auth/profile/")
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.context["brother_profile"].pk, self.a.brother_profile.pk)
                save.assert_not_called()
                delete.assert_not_called()
        self.assertEqual(a_path.read_bytes(), a_bytes)
        self.assertEqual(b_path.read_bytes(), b_bytes)
        self.assert_pair_unchanged(before)
