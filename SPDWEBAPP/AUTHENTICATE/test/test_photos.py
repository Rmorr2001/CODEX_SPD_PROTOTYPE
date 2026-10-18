"""Synthetic real-media uploads, replacement and reset ownership."""
from pathlib import Path
from django.urls import reverse
from AUTHENTICATE.models import Brother_Profile
from .support import IdentityCase, BASIC_ROLES, attach_image, image_upload, set_roles


class PhotoTests(IdentityCase):
    def test_photo_ajax_thumbnail_png(self):
        b_path = attach_image(self.b, "other.png", "blue")
        self.major("Physics", self.a)
        for roles in BASIC_ROLES:
            with self.subTest(roles=roles):
                profile = Brother_Profile.objects.get(user=self.a)
                if profile.profileImage:
                    profile.profileImage.delete()
                set_roles(self.a, roles)
                self.login()
                before, b_bytes = self.pair_snapshot(), b_path.read_bytes()
                response = self.client.post("/auth/update_photo/", {
                    "profile_photo": image_upload("portrait.png", (900, 450))},
                    HTTP_X_REQUESTED_WITH="XMLHttpRequest")
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["success"])
                profile = self.decode_image(self.a, (300, 150), "PNG")
                self.assertEqual(response.json()["image_url"], profile.profileImage.url)
                self.assertEqual(b_path.read_bytes(), b_bytes)
                self.assert_pair_unchanged(before, profile_fields=("profileImage",))

    def test_photo_form_preserves_small_jpeg(self):
        b_path = attach_image(self.b, "other.png", "blue")
        self.login()
        before, b_bytes = self.pair_snapshot(), b_path.read_bytes()
        response = self.client.post("/auth/update_photo/", {
            "profile_photo": image_upload("portrait.jpg", (80, 40), "JPEG")})
        self.assertRedirects(response, reverse("profile"), fetch_redirect_response=False)
        self.decode_image(self.a, (80, 40), "JPEG")
        self.assertEqual(b_path.read_bytes(), b_bytes)
        self.assert_pair_unchanged(before, profile_fields=("profileImage",))

    def test_photo_successful_replacement(self):
        old = attach_image(self.a)
        b_path = attach_image(self.b, "other.png", "blue")
        self.login()
        before, b_bytes = self.pair_snapshot(), b_path.read_bytes()
        response = self.client.post("/auth/update_photo/", {"profile_photo": image_upload()})
        self.assertRedirects(response, reverse("profile"), fetch_redirect_response=False)
        profile = self.decode_image(self.a, (40, 40), "PNG")
        self.assertNotEqual(Path(profile.profileImage.path), old)
        self.assertFalse(old.exists())
        self.assertEqual(b_path.read_bytes(), b_bytes)
        self.assert_pair_unchanged(before, profile_fields=("profileImage",))

    def test_photo_missing_upload_is_noop(self):
        a_path, b_path = attach_image(self.a), attach_image(self.b, "other.png", "blue")
        self.login()
        before = self.pair_snapshot()
        image_bytes = (a_path.read_bytes(), b_path.read_bytes())
        requests = [lambda: self.client.get("/auth/update_photo/"),
                    lambda: self.client.post("/auth/update_photo/", {}),
                    lambda: self.client.post("/auth/update_photo/", {"avatar": image_upload()})]
        for i, request in enumerate(requests):
            with self.subTest(request=i):
                self.assertRedirects(request(), reverse("profile"), fetch_redirect_response=False)
                self.assert_pair_unchanged(before)
                self.assertEqual((a_path.read_bytes(), b_path.read_bytes()), image_bytes)

    def test_reset_photo_removes_own_file(self):
        b_path = attach_image(self.b, "other.png", "blue")
        for roles in BASIC_ROLES:
            with self.subTest(roles=roles):
                old = attach_image(self.a)
                set_roles(self.a, roles)
                self.login()
                before, b_bytes = self.pair_snapshot(), b_path.read_bytes()
                self.assert_json(self.client.post("/auth/reset-photo/"), {
                    "success": True, "message": "Profile photo reset successfully"})
                self.assertFalse(Brother_Profile.objects.get(user=self.a).profileImage)
                self.assertFalse(old.exists())
                self.assertEqual(b_path.read_bytes(), b_bytes)
                self.assert_pair_unchanged(before, profile_fields=("profileImage",))

    def test_reset_photo_without_image_idempotent(self):
        b_path = attach_image(self.b, "other.png", "blue")
        self.login()
        before, b_bytes = self.pair_snapshot(), b_path.read_bytes()
        for _ in range(2):
            self.assert_json(self.client.post("/auth/reset-photo/"), {
                "success": True, "message": "Profile photo reset successfully"})
            self.assertFalse(Brother_Profile.objects.get(user=self.a).profileImage)
        self.assertEqual(b_path.read_bytes(), b_bytes)
        self.assert_pair_unchanged(before, profile_fields=("profileImage",))

    def test_reset_photo_get_is_noop(self):
        a_path, b_path = attach_image(self.a), attach_image(self.b, "other.png", "blue")
        self.login()
        before, image_bytes = self.pair_snapshot(), (a_path.read_bytes(), b_path.read_bytes())
        self.assert_json(self.client.get("/auth/reset-photo/"), {"success": False, "message": "Invalid request"})
        self.assert_pair_unchanged(before)
        self.assertEqual((a_path.read_bytes(), b_path.read_bytes()), image_bytes)
