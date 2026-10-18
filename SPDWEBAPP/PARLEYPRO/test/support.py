"""Thin ORM fixtures and polling assertions; shared identity/harness lives in CORE."""
from datetime import datetime, timedelta, timezone
import re

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from AUTHENTICATE.models import Brother_Profile
from PARLEYPRO.models import Brother_votes, Vote_Poll
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import at_time, login_actor
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope

T = datetime(2026, 1, 15, 18, tzinfo=timezone.utc)


def make_poll(*, creator, name="Motion", start=None, end=None, yes=0, no=0):
    """Persist explicit lifecycle fields without bypassing model save behavior."""
    start = start or T - timedelta(seconds=10)
    with at_time(start):
        return Vote_Poll.objects.create(
            created_by=creator, Vote_Poll_Name=name, Vote_Poll_End=end,
            Vote_Poll_Count_Yes=yes, Vote_Poll_Count_No=no,
        )


def make_choice(user, value):
    return Brother_votes.objects.create(user=user, user_vote_choice=value)


def grant(user, *codenames):
    content_type = ContentType.objects.get_for_model(Vote_Poll)
    permissions = Permission.objects.filter(content_type=content_type, codename__in=codenames)
    if permissions.count() != len(codenames):
        raise AssertionError("Unknown poll permission in fixture")
    user.user_permissions.add(*permissions)


def csrf_token(response):
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.content.decode())
    if not match:
        raise AssertionError("Rendered form did not provide a CSRF token")
    return match.group(1)


class PollTestCase(RegressionTestCase):
    actor_roles = ("EXEC", "ACTIVE")

    def setUp(self):
        super().setUp()
        self.a = make_user(username="a", roles=self.actor_roles)
        self.b = make_user(username="b", roles=("ACTIVE",))
        self.h = make_poll(
            creator=self.b, name="Historical sentinel", start=T-timedelta(seconds=20),
            end=T-timedelta(seconds=1), yes=4, no=2,
        )
        self.b_choice = make_choice(self.b, "Nay")
        login_actor(self.client, self.a)

    def background(self):
        a_profile = Brother_Profile.objects.get(user=self.a)
        b_profile = Brother_Profile.objects.get(user=self.b)
        return snapshot_scope(
            [self.a, self.b, self.h, self.b_choice, a_profile, b_profile],
            relations=((a_profile, "roles"), (b_profile, "roles")),
        )

    def assert_background(self, before):
        assert_unchanged(before)
        self.assertEqual(LogEntry.objects.count(), 0)
        self.assertEqual(set(self.a.brother_profile.roles.values_list("name", flat=True)),
                         set(self.actor_roles))
        self.assertEqual(set(self.b.brother_profile.roles.values_list("name", flat=True)),
                         {"ACTIVE"})

    def assert_choice(self, user, value, pk=None):
        self.assertEqual(Brother_votes.objects.filter(user=user).count(), 1)
        row = Brother_votes.objects.get(user=user)
        self.assertEqual(row.user_vote_choice, value)
        if pk is not None:
            self.assertEqual(row.pk, pk)
        return row

    def assert_open_defaults(self, poll, name):
        poll.refresh_from_db()
        self.assertEqual(poll.Vote_Poll_Name, name)
        self.assertEqual(poll.created_by_id, self.a.pk)
        self.assertEqual((poll.Vote_Poll_Count_Yes, poll.Vote_Poll_Count_No), (0, 0))
        self.assertIsNone(poll.Vote_Poll_End)
