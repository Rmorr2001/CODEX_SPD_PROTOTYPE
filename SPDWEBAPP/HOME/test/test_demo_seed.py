from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import override_settings

from AUTHENTICATE.models import Brother_Profile, DashboardLink, Major, Role
from HOME.models import BannerImage, RushFormLink, RushSlide
from MISC.models import AnnouncementAlert, DayLightSavingsAlert
from NEWMEMBER.models import NewMember_Mark_Event_and_Request as Mark
from PARLEYPRO.models import Brother_votes, Vote_Poll
from PHILANTHROPY.models import Philanthropy_Hours_Event_and_Request as Hours
from railway_demo.management.commands import seed_railway_demo as seed_source
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import at_time, temporary_media
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope

from .helpers import file_path, image_bytes, slide, upload


IDENTITIES = [
    ("demo-executive", "Alex", "Example", {"ACTIVE", "EXEC", "PRESIDENT", "PHIL_CHAIR", "NM_BOARD", "NME"}),
    ("demo-active", "Jordan", "Sample", {"ACTIVE"}),
    ("demo-3", "Taylor", "Demo", {"ACTIVE", "EXEC", "EXT_VP"}),
    ("demo-4", "Casey", "Example", {"ACTIVE", "EXEC", "PHIL_CHAIR"}),
    ("demo-5", "Morgan", "Sample", {"ACTIVE", "EXEC", "RECRUITMENT_CHAIR"}),
    ("demo-6", "Riley", "Demo", {"ACTIVE", "EXEC", "RISK_MGR"}),
    ("demo-7", "Jamie", "Example", {"ACTIVE", "EXEC", "SOCIAL_CHAIR"}),
    ("demo-8", "Avery", "Sample", {"ACTIVE", "EXEC", "BUSINESS_MGR"}),
    ("demo-9", "Quinn", "Demo", {"ACTIVE", "EXEC", "AFFAIRS_DIRECTOR"}),
    ("demo-newmember", "Cameron", "Example", {"NEW_MEMBER"}),
    ("demo-11", "Drew", "Sample", {"NEW_MEMBER"}),
    ("demo-alumni", "Hayden", "Demo", {"ALUMNI"}),
]
SEED_MODELS = [User, Group, Role, Major, Brother_Profile, DashboardLink, BannerImage,
               RushFormLink, RushSlide, AnnouncementAlert, DayLightSavingsAlert,
               Hours, Brother_votes, Mark, Vote_Poll]


class SeedFixtureMixin:
    def setUp(self):
        super().setUp()
        if not hasattr(self, "media_root"):
            self.media_root = self.enterContext(temporary_media())
        self.source_directory = TemporaryDirectory(prefix="home-seed-source-")
        self.addCleanup(self.source_directory.cleanup)
        self.source_root = Path(self.source_directory.name)
        self.source_file = self.source_root / "static/images/colony_members.webp"
        self.source_file.parent.mkdir(parents=True)
        self.source_file.write_bytes(image_bytes())
        self.sentinel = self.source_root / "synthetic-canary.txt"
        self.sentinel.write_bytes(b"unrelated-synthetic-canary")
        self.enterContext(override_settings(DEMO_MODE=True, DEMO_PUBLIC_DOMAIN=None,
                                           BASE_DIR=self.source_root,
                                           MEDIA_ROOT=Path(settings.MEDIA_ROOT)))
        self.instant = self.enterContext(at_time("2026-10-01T12:00:00Z"))

    def seed(self):
        output = StringIO()
        call_command("seed_railway_demo", stdout=output)
        self.assertIn("Seeded 12 fictional members", output.getvalue())
        self.assertEqual(self.sentinel.read_bytes(), b"unrelated-synthetic-canary")
        return output.getvalue()

    def all_seed_rows(self):
        return [row for model in SEED_MODELS for row in model.objects.all()]

    def relations(self):
        result = []
        for user in User.objects.all():
            result.append(user.groups)
        for profile in Brother_Profile.objects.all():
            result.extend([profile.roles, profile.majors])
        return result

    def seed_files(self):
        return [Path(settings.MEDIA_ROOT) / "banners/demo-banner.webp",
                Path(settings.MEDIA_ROOT) / "rush_slides/demo-slide.webp", self.sentinel]

    def assert_seed_counts(self):
        for model, count in ((Brother_Profile, 12), (Brother_votes, 9), (Hours, 9),
                             (Mark, 4), (Vote_Poll, 2), (BannerImage, 1),
                             (RushFormLink, 1), (RushSlide, 1)):
            self.assertEqual(model.objects.count(), count, model.__name__)


class SeedTests(SeedFixtureMixin, RegressionTestCase):
    def test_first_seed_creates_exact_fictional_identities(self):
        output = self.seed()
        self.assertEqual(User.objects.count(), 12)
        self.assertEqual(Brother_Profile.objects.count(), 12)
        for username, first, last, roles in IDENTITIES:
            user = User.objects.get(username=username)
            profile = user.brother_profile
            self.assertEqual((user.first_name, user.last_name, user.email),
                             (first, last, f"{username}@example.invalid"))
            self.assertFalse(user.has_usable_password())
            self.assertFalse(user.is_staff or user.is_superuser)
            self.assertEqual(set(user.groups.values_list("name", flat=True)), {f"railway-demo:{username}"})
            self.assertEqual((profile.firstName, profile.lastName, profile.hometown, profile.pclass),
                             (first, last, "Example City", "Beta Omicron"))
            self.assertFalse(profile.profileImage)
            self.assertEqual(set(profile.roles.values_list("name", flat=True)), roles)
            self.assertEqual(list(profile.majors.values_list("name", flat=True)), ["Engineering (demo)"])
            self.assertNotIn(user.password, output)
        self.assertEqual(Major.objects.count(), 1)
        self.assertEqual(Brother_Profile.objects.filter(roles__name="ACTIVE").distinct().count(), 9)
        self.assertEqual(Brother_Profile.objects.filter(roles__name="INT_VP").count(), 0)

    def test_first_seed_creates_public_content_and_media(self):
        with override_settings(DEMO_PUBLIC_DOMAIN="demo.example.invalid"):
            self.seed()
        self.assertEqual(BannerImage.objects.count(), 1)
        self.assertEqual(BannerImage.objects.get().image.name, "banners/demo-banner.webp")
        self.assertEqual(RushFormLink.objects.get().link, "https://demo.example.invalid/rush/")
        obj = RushSlide.objects.get()
        self.assertEqual((obj.caption, obj.order, obj.image.name),
                         ("Chapter life — sample slide", 0, "rush_slides/demo-slide.webp"))
        for file in self.seed_files()[:2]:
            self.assertEqual(file.read_bytes(), self.source_file.read_bytes())

    def test_first_seed_creates_alert_and_dashboard_manifest(self):
        sentinel = make_user(username="unrelated")
        before = snapshot_scope([sentinel, sentinel.brother_profile], files=[self.sentinel])
        self.seed()
        alert = AnnouncementAlert.objects.get(title="Welcome to the seeded demo")
        self.assertTrue(alert.is_active)
        self.assertEqual(alert.content, "All member names and workflow records here are fictional. "
                         "Switch personas above to explore the original app.")
        self.assertFalse(DayLightSavingsAlert.objects.get(name="Demo chapter notice").is_active)
        self.assertEqual(list(DashboardLink.objects.values_list("text", "link", "order")), [
            ("Executive Board", "/executive-board/", 0), ("Rush Information", "/rush/", 1),
            ("Member profile", "/auth/profile/", 2)])
        assert_unchanged(before)

    def test_first_seed_populates_hours_and_votes(self):
        self.seed()
        self.assertEqual(Hours.objects.count(), 9)
        self.assertEqual(Brother_votes.objects.count(), 9)
        for index, (username, _, _, _) in enumerate(IDENTITIES[:9]):
            user = User.objects.get(username=username)
            obj = Hours.objects.get(user=user)
            self.assertEqual((obj.philanthropy_event_title, obj.philanthropy_event_hours,
                              obj.philanthropy_event_date.isoformat()),
                             ("Demo: community service", 3 + index, "2026-09-28"))
            self.assertEqual(obj.philanthropy_approval_status, "approved" if index % 3 else "requested")
            self.assertEqual(obj.philanthropy_event_approver_name, "Alex Example" if index % 3 else None)
            self.assertEqual(Brother_votes.objects.get(user=user).user_vote_choice, "Aye" if index % 3 else "Nay")

    def test_first_seed_populates_newmember_marks(self):
        self.seed()
        self.assertEqual(Mark.objects.count(), 4)
        executive = User.objects.get(username="demo-executive")
        for username in ("demo-newmember", "demo-11"):
            target = User.objects.get(username=username)
            for status, value in (("approved", 3), ("requested", 1)):
                obj = Mark.objects.get(target_user=target, mark_approval_status=status)
                self.assertEqual((obj.requesting_user_id, obj.mark_value, obj.mark_event_date.isoformat()),
                                 (executive.pk, value, "2026-09-29"))
                self.assertEqual(obj.mark_event_title, f"Demo: chapter participation ({status})")
                self.assertEqual(obj.mark_approver_name, "Alex Example" if status == "approved" else None)

    def test_first_seed_populates_open_and_closed_polls(self):
        self.seed()
        self.assertEqual(Vote_Poll.objects.count(), 2)
        executive = User.objects.get(username="demo-executive")
        opened = Vote_Poll.objects.get(Vote_Poll_Name="Demo: next service activity")
        closed = Vote_Poll.objects.get(Vote_Poll_Name="Demo: previous chapter motion")
        self.assertEqual((opened.created_by_id, closed.created_by_id), (executive.pk, executive.pk))
        self.assertIsNone(opened.Vote_Poll_End)
        self.assertEqual(closed.Vote_Poll_End.isoformat(), "2026-09-24T12:00:00+00:00")
        self.assertEqual((closed.Vote_Poll_Count_Yes, closed.Vote_Poll_Count_No), (8, 1))

    def test_repeat_seed_preserves_stable_row_identity(self):
        unrelated = make_user(username="unrelated")
        unrelated_before = snapshot_scope([unrelated, unrelated.brother_profile])
        self.seed()
        rows = self.all_seed_rows()
        before = snapshot_scope(rows, relations=self.relations(), files=self.seed_files())
        expected_pks = {model: set(model.objects.values_list("pk", flat=True)) for model in SEED_MODELS}
        for user in User.objects.exclude(pk=unrelated.pk):
            self.assertFalse(user.has_usable_password())
        for _ in range(2):
            self.seed()
            self.assert_seed_counts_with_unrelated()
            # Approved coordinator clarification: unusable markers randomize, semantic
            # unusability and all stable business fields/PKs/relations must remain.
            assert_unchanged(before, except_fields={user: {"password"} for user in User.objects.exclude(pk=unrelated.pk)})
            for model, pks in expected_pks.items():
                self.assertEqual(set(model.objects.values_list("pk", flat=True)), pks)
            for user in User.objects.exclude(pk=unrelated.pk):
                self.assertFalse(user.has_usable_password())
                self.assertFalse(user.is_staff or user.is_superuser)
            assert_unchanged(unrelated_before)

    def assert_seed_counts_with_unrelated(self):
        self.assertEqual(Brother_Profile.objects.count(), 13)
        for model, count in ((Hours, 9), (Brother_votes, 9), (Mark, 4), (Vote_Poll, 2),
                             (BannerImage, 1), (RushFormLink, 1), (RushSlide, 1)):
            self.assertEqual(model.objects.count(), count)

    def test_repeat_seed_preserves_unrelated_synthetic_records(self):
        self.seed()
        user = make_user(username="unrelated", roles=("ALUMNI",))
        extra = [user, user.brother_profile, slide("Unrelated", 9),
                 AnnouncementAlert.objects.create(title="Unrelated", content="Keep", is_active=False),
                 DashboardLink.objects.create(text="Unrelated", link="/keep/", order=9),
                 Hours.objects.create(user=user, philanthropy_event_title="Unrelated", philanthropy_event_hours=2,
                                      philanthropy_event_date=self.instant.date(), philanthropy_approval_status="requested"),
                 Mark.objects.create(target_user=user, requesting_user=user, mark_event_title="Unrelated",
                                     mark_value=1, mark_event_date=self.instant.date(), mark_approval_status="requested"),
                 Vote_Poll.objects.create(Vote_Poll_Name="Unrelated", created_by=user)]
        before = snapshot_scope(extra, relations=[user.groups, user.brother_profile.roles],
                                files=[file_path(extra[2].image), self.sentinel])
        self.seed()
        assert_unchanged(before)
        self.assertEqual(BannerImage.objects.count(), 1)
        self.assertEqual(RushSlide.objects.filter(caption="Chapter life — sample slide").count(), 1)

    def test_seed_preserves_existing_home_rows(self):
        banner = BannerImage.objects.create(image=upload("custom.png"))
        link = RushFormLink.objects.create(link="https://example.invalid/custom")
        obj = slide("Chapter life — sample slide", 5)
        alert = DayLightSavingsAlert.objects.create(name="Demo chapter notice", is_active=True)
        before = snapshot_scope([banner, link, obj, alert], files=[file_path(banner.image), file_path(obj.image)])
        self.seed()
        assert_unchanged(before)
        self.assertEqual((BannerImage.objects.count(), RushFormLink.objects.count(), RushSlide.objects.count()), (1, 1, 1))

    def test_seed_copies_only_public_source_asset(self):
        import shutil
        original = shutil.copyfile
        with patch.object(seed_source.shutil, "copyfile", wraps=original) as copy:
            self.seed()
        self.assertEqual(copy.call_count, 2)
        self.assertEqual([Path(call.args[0]) for call in copy.call_args_list], [self.source_file] * 2)
        self.assertEqual([Path(call.args[1]) for call in copy.call_args_list], self.seed_files()[:2])
        for file in self.seed_files()[:2]:
            self.assertEqual(file.read_bytes(), self.source_file.read_bytes())
        self.assertFalse(any(profile.profileImage for profile in Brother_Profile.objects.all()))

    def test_seed_interest_url_uses_local_demo_host(self):
        for domain, expected in ((None, "https://localhost/rush/"),
                                 ("demo.example.invalid", "https://demo.example.invalid/rush/")):
            RushFormLink.objects.all().delete()
            with override_settings(DEMO_PUBLIC_DOMAIN=domain):
                seed_source.seed_home()
            self.assertEqual(RushFormLink.objects.get().link, expected)
            self.assertTrue(all(path.exists() for path in self.seed_files()))
            self.assertEqual(self.sentinel.read_bytes(), b"unrelated-synthetic-canary")
