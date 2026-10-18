import shutil
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError
from django.test import TransactionTestCase, override_settings

from PARLEYPRO.models import Vote_Poll
from railway_demo.management.commands import seed_railway_demo as seed_source
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope

from .test_demo_seed import SEED_MODELS, SeedFixtureMixin


class SeedFailureTests(SeedFixtureMixin, TransactionTestCase):
    def capture(self):
        return snapshot_scope(self.all_seed_rows(), relations=self.relations(), files=[self.sentinel])

    def counts(self):
        return {model: model.objects.count() for model in SEED_MODELS}

    def assert_counts(self, before):
        self.assertEqual(self.counts(), before)

    def test_seed_non_demo_refusal_has_no_side_effects(self):
        make_user(username="unrelated", roles=("ALUMNI",))
        before, counts, output = self.capture(), self.counts(), StringIO()
        with override_settings(DEMO_MODE=False), self.assertRaisesMessage(CommandError, "Only isolated demo"):
            call_command("seed_railway_demo", stdout=output)
        self.assertNotIn("Seeded", output.getvalue())
        self.assert_counts(counts)
        assert_unchanged(before)
        self.assertFalse(self.seed_files()[0].exists())

    def test_seed_refuses_credentialed_or_privileged_identity(self):
        sentinel = make_user(username="unrelated")
        for route in ("username", "group"):
            for index, flags in enumerate(({"password": "Synthetic-password-17"},
                                           {"password": None, "is_staff": True},
                                           {"password": None, "is_superuser": True},
                                           {"password": "Synthetic-password-17", "is_staff": True,
                                            "is_superuser": True})):
                with self.subTest(route=route, flags=tuple(flags)):
                    name = "demo-executive" if route == "username" else f"renamed-{index}"
                    actor = make_user(username=name, **flags)
                    group = None
                    if route == "group":
                        group = Group.objects.create(name="railway-demo:demo-executive")
                        actor.groups.add(group)
                    before, counts, output = self.capture(), self.counts(), StringIO()
                    with self.assertRaisesMessage(CommandError, "credentialed or privileged"):
                        call_command("seed_railway_demo", stdout=output)
                    self.assertNotIn("Seeded", output.getvalue())
                    self.assertNotIn(actor.password, output.getvalue())
                    self.assert_counts(counts)
                    assert_unchanged(before)
                    actor.delete()
                    if group:
                        group.delete()
        sentinel.refresh_from_db()
        self.assertTrue(sentinel.has_usable_password())
        self.assertFalse(self.seed_files()[0].exists())

    def test_late_member_refusal_rolls_back_prior_member_writes(self):
        early = make_user(username="demo-active", password=None, roles=("ALUMNI",),
                          profile_fields={"firstName": "Keep", "hometown": "Keep town"})
        blocked = make_user(username="demo-11", password=None, is_staff=True)
        before, counts, output = self.capture(), self.counts(), StringIO()
        with self.assertRaises(CommandError):
            call_command("seed_railway_demo", stdout=output)
        self.assertNotIn("Seeded", output.getvalue())
        self.assert_counts(counts)
        assert_unchanged(before)
        early.refresh_from_db()
        blocked.refresh_from_db()
        self.assertEqual(early.brother_profile.firstName, "Keep")
        self.assertTrue(blocked.is_staff)
        self.assertFalse(self.seed_files()[0].exists())

    def test_late_seed_db_failure_rolls_back_all_database_writes(self):
        self.seed()
        before, counts, output = self.capture(), self.counts(), StringIO()
        with patch.object(Vote_Poll, "_do_update", side_effect=IntegrityError("synthetic late DB failure")):
            with self.assertRaises(IntegrityError):
                call_command("seed_railway_demo", stdout=output)
        self.assertNotIn("Seeded", output.getvalue())
        self.assert_counts(counts)
        assert_unchanged(before)
        # Files are observed separately: repeated copies happened despite DB rollback.
        for path in self.seed_files()[:2]:
            self.assertEqual(path.read_bytes(), self.source_file.read_bytes())

    def test_media_setup_failures_roll_back_prior_db_writes(self):
        make_user(username="demo-active", password=None, roles=("ALUMNI",))
        for failure in ("source", "mkdir", "first-copy", "second-copy"):
            with self.subTest(failure=failure):
                before, counts, output = self.capture(), self.counts(), StringIO()
                original = shutil.copyfile
                copy_index = 0

                def copy_boundary(*args, **kwargs):
                    nonlocal copy_index
                    copy_index += 1
                    if copy_index == (1 if failure == "first-copy" else 2):
                        raise OSError("synthetic copy failure")
                    return original(*args, **kwargs)

                if failure == "source":
                    self.source_file.unlink()
                    boundary = patch.object(seed_source.shutil, "copyfile", wraps=original)
                elif failure == "mkdir":
                    boundary = patch("pathlib.Path.mkdir", side_effect=OSError("synthetic mkdir failure"))
                else:
                    boundary = patch.object(seed_source.shutil, "copyfile", side_effect=copy_boundary)
                with boundary, self.assertRaises(OSError):
                    call_command("seed_railway_demo", stdout=output)
                self.assertNotIn("Seeded", output.getvalue())
                self.assert_counts(counts)
                assert_unchanged(before)
                if failure == "source":
                    from .helpers import image_bytes
                    self.source_file.write_bytes(image_bytes())
                for path in self.seed_files()[:2]:
                    if path.exists():
                        self.assertEqual(path.read_bytes(), self.source_file.read_bytes())

    def test_seed_retry_after_partial_failure_finishes_once(self):
        original = shutil.copyfile
        count = 0

        def fail_second(*args, **kwargs):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("synthetic second copy failure")
            return original(*args, **kwargs)

        with patch.object(seed_source.shutil, "copyfile", side_effect=fail_second):
            with self.assertRaises(OSError):
                call_command("seed_railway_demo", stdout=StringIO())
        self.assertTrue(self.seed_files()[0].exists())
        self.assertFalse(User.objects.exists())
        self.seed()
        self.assert_seed_counts()
        for path in self.seed_files()[:2]:
            self.assertEqual(path.read_bytes(), self.source_file.read_bytes())
        for user in User.objects.all():
            self.assertFalse(user.has_usable_password())
            self.assertFalse(user.is_staff or user.is_superuser)
