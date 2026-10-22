"""Seed the application's real domain models with fictional demo records."""
import shutil
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from AUTHENTICATE.models import Brother_Profile, DashboardLink, Major, Role
from HOME.models import BannerImage, RushFormLink, RushSlide
from MISC.models import AnnouncementAlert, DayLightSavingsAlert
from NEWMEMBER.models import NewMember_Mark_Event_and_Request
from PARLEYPRO.models import Brother_votes, Vote_Poll
from PHILANTHROPY.models import Philanthropy_Hours_Event_and_Request

MEMBERS = [
    ("demo-executive", "Alex", "Example", ["ACTIVE", "EXEC", "PRESIDENT", "PHIL_CHAIR", "NM_BOARD", "NME"]),
    ("demo-active", "Jordan", "Sample", ["ACTIVE"]),
    ("demo-3", "Taylor", "Demo", ["ACTIVE", "EXEC", "EXT_VP"]),
    ("demo-4", "Casey", "Example", ["ACTIVE", "EXEC", "PHIL_CHAIR"]),
    ("demo-5", "Morgan", "Sample", ["ACTIVE", "EXEC", "RECRUITMENT_CHAIR"]),
    ("demo-6", "Riley", "Demo", ["ACTIVE", "EXEC", "RISK_MGR"]),
    ("demo-7", "Jamie", "Example", ["ACTIVE", "EXEC", "SOCIAL_CHAIR"]),
    ("demo-8", "Avery", "Sample", ["ACTIVE", "EXEC", "BUSINESS_MGR"]),
    ("demo-9", "Quinn", "Demo", ["ACTIVE", "EXEC", "AFFAIRS_DIRECTOR"]),
    ("demo-newmember", "Cameron", "Example", ["NEW_MEMBER"]),
    ("demo-11", "Drew", "Sample", ["NEW_MEMBER"]),
    ("demo-alumni", "Hayden", "Demo", ["ALUMNI"]),
]


class Command(BaseCommand):
    help = "Seed the isolated Railway demo; never use private member records."

    @transaction.atomic
    def handle(self, *args, **options):
        if not getattr(settings, "DEMO_MODE", False):
            raise CommandError("Only isolated demo settings permit this seed.")
        users = seed_members()
        seed_home()
        seed_workflows(users)
        self.stdout.write("Seeded 12 fictional members, board roles, polls, philanthropy, and new-member marks.")


def seed_members():
    """Upsert only known demo accounts; never replace usable credentials."""
    major, _ = Major.objects.get_or_create(name="Engineering (demo)")
    users = []
    for username, first, last, role_names in MEMBERS:
        group, _ = Group.objects.get_or_create(name=f"railway-demo:{username}")
        user = group.user_set.first()
        created = False
        if user is None:
            user, created = User.objects.get_or_create(username=username)
        if not created and (user.has_usable_password() or user.is_staff or user.is_superuser):
            raise CommandError("Refusing to replace a credentialed or privileged account.")
        user.username = username
        user.first_name, user.last_name = first, last
        user.email = f"{username}@example.invalid"
        user.set_unusable_password()
        user.save()
        user.groups.add(group)
        profile, _ = Brother_Profile.objects.update_or_create(user=user, defaults={
            "firstName": first, "lastName": last, "hometown": "Example City",
            "pclass": "Beta Omicron", "profileImage": None,
        })
        profile.roles.set([Role.objects.get_or_create(name=name)[0] for name in role_names])
        profile.majors.set([major])
        users.append(user)
    return users


def seed_home():
    """Reuse public repository images; no personal profile photos are imported."""
    media = settings.MEDIA_ROOT
    (media / "banners").mkdir(parents=True, exist_ok=True)
    (media / "rush_slides").mkdir(parents=True, exist_ok=True)
    source = settings.BASE_DIR / "static/images/colony_members.webp"
    shutil.copyfile(source, media / "banners/demo-banner.webp")
    shutil.copyfile(source, media / "rush_slides/demo-slide.webp")
    if not BannerImage.objects.exists():
        BannerImage.objects.create(image="banners/demo-banner.webp")
    if not RushFormLink.objects.exists():
        # Keep the sample interest link within the demo, with no external submission.
        host = settings.DEMO_PUBLIC_DOMAIN or "localhost"
        RushFormLink.objects.create(link=f"https://{host}/rush/")
    RushSlide.objects.get_or_create(caption="Chapter life — sample slide", defaults={"image": "rush_slides/demo-slide.webp", "order": 0})
    AnnouncementAlert.objects.update_or_create(title="Welcome to the seeded demo", defaults={"content": "All member names and workflow records here are fictional. Use demo sign-in to choose a role and explore fictional workflows.", "is_active": True})
    DayLightSavingsAlert.objects.get_or_create(name="Demo chapter notice", defaults={"is_active": False})
    for order, (text, link) in enumerate([("Executive Board", "/executive-board/"), ("Rush Information", "/rush/"), ("Member profile", "/auth/profile/")]):
        DashboardLink.objects.update_or_create(text=text, defaults={"link": link, "order": order})


def seed_workflows(users):
    """Populate each real workflow with dated sample records and statuses."""
    now = timezone.now()
    for index, user in enumerate(users[:9]):
        Philanthropy_Hours_Event_and_Request.objects.update_or_create(user=user, philanthropy_event_title="Demo: community service", defaults={
            "philanthropy_event_hours": 3 + index, "philanthropy_event_date": now.date() - timedelta(days=3),
            "philanthropy_approval_status": "approved" if index % 3 else "requested",
            "philanthropy_event_approver_name": "Alex Example" if index % 3 else None,
        })
        Brother_votes.objects.update_or_create(user=user, defaults={"user_vote_choice": "Aye" if index % 3 else "Nay"})
    for index, user in enumerate(users[9:11]):
        for status, value in (("approved", 3), ("requested", 1)):
            NewMember_Mark_Event_and_Request.objects.update_or_create(target_user=user, requesting_user=users[0], mark_event_title=f"Demo: chapter participation ({status})", defaults={
                "mark_value": value, "mark_event_date": now.date() - timedelta(days=2),
                "mark_approval_status": status, "mark_approver_name": "Alex Example" if status == "approved" else None,
            })
    Vote_Poll.objects.update_or_create(Vote_Poll_Name="Demo: next service activity", defaults={"created_by": users[0], "Vote_Poll_End": None})
    Vote_Poll.objects.update_or_create(Vote_Poll_Name="Demo: previous chapter motion", defaults={
        "created_by": users[0], "Vote_Poll_End": now - timedelta(days=7),
        "Vote_Poll_Count_Yes": 8, "Vote_Poll_Count_No": 1,
    })
