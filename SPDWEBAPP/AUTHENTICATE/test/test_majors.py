"""Catalog normalization and explicit replacement using real relations."""
from django.test import SimpleTestCase
from AUTHENTICATE.models import Major
from AUTHENTICATE.utils import contains_profanity
from .support import IdentityCase, BASIC_ROLES, set_roles


class MajorTests(IdentityCase):
    def setUp(self):
        super().setUp()
        self.old = self.major("Old", self.a)
        self.other = self.major("Other", self.b)
        self.login()

    def selection(self, names):
        return self.client.post("/auth/update_majors/", {"majors": names}, content_type="application/json")

    def custom(self, name):
        return self.client.post("/auth/add-custom-major/", {"major_name": name}, content_type="application/json")

    def test_replace_own_major_set(self):
        new = self.major("New")
        catalog = list(Major.objects.order_by("pk").values())
        for roles in BASIC_ROLES:
            with self.subTest(roles=roles):
                self.a.brother_profile.majors.set([self.old])
                set_roles(self.a, roles)
                before = self.pair_snapshot()
                self.assert_json(self.selection(["New", "New"]), {
                    "success": True, "message": "Majors updated successfully"})
                self.assertEqual(list(self.a.brother_profile.majors.values_list("pk", flat=True)), [new.pk])
                self.assertEqual(list(Major.objects.order_by("pk").values()), catalog)
                self.assert_pair_unchanged(before, relations=("majors",))

    def test_clear_own_major_set(self):
        before, catalog = self.pair_snapshot(), list(Major.objects.order_by("pk").values())
        self.assert_json(self.selection([]), {"success": True, "message": "Majors updated successfully"})
        self.assertFalse(self.a.brother_profile.majors.exists())
        self.assertEqual(list(Major.objects.order_by("pk").values()), catalog)
        self.assert_pair_unchanged(before, relations=("majors",))

    def test_major_selection_get_noop(self):
        before, catalog = self.pair_snapshot(), list(Major.objects.order_by("pk").values())
        self.assert_json(self.client.get("/auth/update_majors/"), {
            "success": False, "message": "Invalid request method"})
        self.assert_pair_unchanged(before)
        self.assertEqual(list(Major.objects.order_by("pk").values()), catalog)

    def test_repeat_major_replacement(self):
        new = self.major("New")
        self.a.brother_profile.majors.set([new])
        before, catalog = self.pair_snapshot(), list(Major.objects.order_by("pk").values())
        for _ in range(2):
            self.assert_json(self.selection(["New"]), {"success": True, "message": "Majors updated successfully"})
        self.assertEqual(list(self.a.brother_profile.majors.values_list("pk", flat=True)), [new.pk])
        self.assertEqual(list(Major.objects.order_by("pk").values()), catalog)
        self.assert_pair_unchanged(before)

    def test_custom_major_normalization(self):
        for i, roles in enumerate(BASIC_ROLES):
            with self.subTest(roles=roles):
                Major.objects.filter(name="Mechanical Engineering").delete()
                set_roles(self.a, roles)
                before, count = self.pair_snapshot(), Major.objects.count()
                response = self.custom("  mechanical   ENGINEERING  ")
                self.assertEqual(response.status_code, 200)
                row = Major.objects.get(name="Mechanical Engineering")
                self.assertEqual(response.json(), {"success": True, "major_id": row.pk,
                                                   "major_name": "Mechanical Engineering"})
                self.assertEqual(Major.objects.count(), count + 1)
                self.assert_pair_unchanged(before)

    def test_custom_major_sequential_idempotency(self):
        major = self.major("Mechanical Engineering")
        before, count = self.pair_snapshot(), Major.objects.count()
        for _ in range(2):
            self.assert_json(self.custom("mechanical engineering"), {
                "success": True, "major_id": major.pk, "major_name": "Mechanical Engineering"})
        self.assertEqual(Major.objects.count(), count)
        self.assert_pair_unchanged(before)

    def test_custom_major_blacklist_rejection(self):
        before, catalog = self.pair_snapshot(), list(Major.objects.order_by("pk").values())
        self.assert_json(self.custom("fuck"), {
            "success": False, "message": "Major name contains inappropriate language"})
        self.assertEqual(list(Major.objects.order_by("pk").values()), catalog)
        self.assert_pair_unchanged(before)

    def test_custom_major_get_noop(self):
        before, catalog = self.pair_snapshot(), list(Major.objects.order_by("pk").values())
        self.assert_json(self.client.get("/auth/add-custom-major/"), {
            "success": False, "message": "Invalid request method"})
        self.assertEqual(list(Major.objects.order_by("pk").values()), catalog)
        self.assert_pair_unchanged(before)


class FilterTests(SimpleTestCase):
    def test_filter_clean_and_whitelist_inputs(self):
        for value in ("engineering", "BIOLOGY", "biological   engineering", ""):
            with self.subTest(value=value):
                self.assertIs(contains_profanity(value), False)

    def test_filter_independent_blacklist_substring(self):
        for value in ("fuck", "FUCK", "xxfuckxx"):
            with self.subTest(value=value):
                self.assertIs(contains_profanity(value), True)
