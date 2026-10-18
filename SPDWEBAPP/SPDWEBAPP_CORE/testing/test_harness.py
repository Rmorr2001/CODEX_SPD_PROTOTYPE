"""Verify the shared test infrastructure detects changes instead of masking them."""
import sys
from datetime import datetime, timezone
from django.conf import settings
from django.core.checks import run_checks
from django.test import SimpleTestCase
from AUTHENTICATE.models import Brother_Profile, Role
from .base import RegressionTestCase
from .factories import make_profile, make_user
from .helpers import at_time, csrf_client, temporary_media
from .state import assert_unchanged, snapshot_scope


class IsolationTests(SimpleTestCase):
    def test_standalone_settings_do_not_import_runtime_secrets(self):
        self.assertEqual(run_checks(), [])
        self.assertNotIn("secret_config", sys.modules)
        self.assertNotIn("SPDWEBAPP_CORE.settings", sys.modules)
        self.assertEqual(settings.DATABASES["default"]["ENGINE"], "django.db.backends.sqlite3")
        self.assertEqual(settings.DATABASES["default"]["NAME"].startswith("file:memorydb"), True)

    def test_temporary_media_restores_settings_and_deletes_files(self):
        previous = settings.MEDIA_ROOT
        with temporary_media() as path:
            self.assertEqual(settings.MEDIA_ROOT, path)
            (path / "synthetic.txt").write_text("fixture")
        self.assertEqual(settings.MEDIA_ROOT, previous)
        self.assertFalse(path.exists())

    def test_clock_requires_awareness_and_restores_real_time(self):
        from django.utils import timezone as django_timezone
        fixed = datetime(2026, 7, 1, tzinfo=timezone.utc)
        original = django_timezone.now
        with at_time(fixed):
            self.assertEqual(django_timezone.now(), fixed)
        self.assertIs(django_timezone.now, original)
        with self.assertRaises(ValueError):
            with at_time(datetime(2026, 7, 1)):
                self.fail("Naive clock accepted")

    def test_csrf_client_does_not_disable_csrf(self):
        self.assertEqual(csrf_client().post("/auth/login/", {}).status_code, 403)


class FixtureTests(RegressionTestCase):
    def test_roles_do_not_grant_active_staff_or_superuser(self):
        user = make_user(username="executive", roles=("EXEC",))
        self.assertEqual(list(user.brother_profile.roles.values_list("name", flat=True)), ["EXEC"])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.brother_profile.majors.exists())
        self.assertFalse(user.brother_profile.profileImage)

    def test_no_profile_and_unusable_password_are_explicit(self):
        user = make_user(username="unprofiled", with_profile=False, password=None)
        self.assertFalse(Brother_Profile.objects.filter(user=user).exists())
        self.assertFalse(user.has_usable_password())
        profile = make_profile(user, roles=("ACTIVE",))
        self.assertEqual(profile.user_id, user.pk)
        with self.assertRaises(ValueError):
            make_profile(user)

    def test_invalid_role_or_profile_arguments_leave_no_user(self):
        from django.contrib.auth.models import User
        for arguments in ({"roles": ("NOT_A_ROLE",)}, {"roles": ("ACTIVE",), "with_profile": False}):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                make_user(username="invalid", **arguments)
            self.assertFalse(User.objects.filter(username="invalid").exists())


class StateAssertionsTests(RegressionTestCase):
    def test_snapshot_uses_fresh_database_values(self):
        user = make_user(username="a")
        before = snapshot_scope([user])
        type(user).objects.filter(pk=user.pk).update(email="changed@example.invalid")
        with self.assertRaisesRegex(AssertionError, "email"):
            assert_unchanged(before)
        assert_unchanged(before, except_fields={user: {"email"}})

    def test_snapshot_detects_row_deletion_even_when_instance_pk_is_cleared(self):
        user = make_user(username="a")
        original_pk = user.pk
        before = snapshot_scope([user])
        user.delete()
        with self.assertRaisesRegex(AssertionError, "existence"):
            assert_unchanged(before)
        assert_unchanged(before, except_fields={(type(user), original_pk): {"__deleted__"}})

    def test_snapshot_detects_relation_change(self):
        user = make_user(username="a", roles=("ACTIVE",))
        before = snapshot_scope([user], relations={"roles": user.brother_profile.roles})
        user.brother_profile.roles.add(Role.objects.create(name="EXEC"))
        with self.assertRaisesRegex(AssertionError, "Relation"):
            assert_unchanged(before)
        assert_unchanged(before, except_fields={"relations": {"roles"}})

    def test_snapshot_detects_file_change_and_deletion(self):
        file = self.media_root / "synthetic.txt"
        file.write_text("before")
        before = snapshot_scope([], files={"image": file})
        file.write_text("after")
        with self.assertRaisesRegex(AssertionError, "file"):
            assert_unchanged(before)
        file.unlink()
        with self.assertRaisesRegex(AssertionError, "file"):
            assert_unchanged(before)
        assert_unchanged(before, except_fields={"files": {"image"}})
