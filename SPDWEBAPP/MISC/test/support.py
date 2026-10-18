"""Small MISC constructors and admin assertions, using the shared harness."""
from contextlib import contextmanager
from datetime import datetime
from unittest.mock import patch
from html.parser import HTMLParser

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from MISC.models import AnnouncementAlert, DayLightSavingsAlert
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import login_actor, at_time
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged

MODELS = (AnnouncementAlert, DayLightSavingsAlert)


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def announcement(title="Notice", content="Text", **fields):
    return AnnouncementAlert.objects.create(title=title, content=content, **fields)


def setting(name="Clock", **fields):
    return DayLightSavingsAlert.objects.create(name=name, **fields)


def admin_url(model, action, pk=None):
    name = f"admin:MISC_{model._meta.model_name}_{action}"
    return reverse(name, args=[pk] if pk is not None else None)


def payload(model, label="New", **extra):
    data = ({"title": label, "content": "Text"} if model is AnnouncementAlert
            else {"name": label, "is_active": "on"})
    return {**data, **extra}


def create(model, label="Target", **fields):
    return (announcement(title=label, **fields) if model is AnnouncementAlert
            else setting(name=label, **fields))


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


class AdminAssertions:
    """Not a TestCase: importing the mixin does not duplicate discovery."""
    def setUp(self):
        super().setUp()
        self.other_ann = announcement("Untouched announcement", is_active=False)
        self.other_dst = setting("Untouched setting", is_active=False)
        self.untouched = snapshot_scope([self.other_ann, self.other_dst])
        self.actor_number = 0
        self.actor = self.staff()
        login_actor(self.client, self.actor)
        self.actor_scope = snapshot_scope([self.actor, self.actor.brother_profile])

    def tearDown(self):
        try:
            assert_unchanged(self.untouched)
            assert_unchanged(self.actor_scope, except_fields={self.actor: {"last_login"}})
            self.assertEqual(list(self.actor.brother_profile.roles.all()), [])
        finally:
            super().tearDown()

    def staff(self, models=MODELS, actions=("view", "add", "change", "delete"), **kwargs):
        self.actor_number += 1
        actor = make_user(username=f"staff-{self.actor_number}", is_staff=True, **kwargs)
        for model in models:
            names = [f"{action}_{model._meta.model_name}" for action in actions]
            actor.user_permissions.add(*Permission.objects.filter(
                content_type__app_label="MISC", codename__in=names))
        return actor

    def identity(self, client=None, actor=None):
        self.assertEqual((client or self.client).session.get("_auth_user_id"),
                         str((actor or self.actor).pk))

    def assert_log(self, obj, flag, actor=None, count=1):
        entries = LogEntry.objects.filter(content_type=ContentType.objects.get_for_model(obj),
                                         object_id=str(obj.pk), action_flag=flag)
        self.assertEqual(entries.count(), count)
        for entry in entries:
            self.assertEqual(entry.user_id, (actor or self.actor).pk)
            self.assertEqual(entry.object_repr, str(obj))
            self.assertIsNotNone(entry.action_time.utcoffset())
        return entries

    def assert_redirect(self, response, url):
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], url)


@contextmanager
def misc_time(value):
    """Freeze the datetime import consumed by MISC while preserving constructors."""
    fixed = instant(value) if isinstance(value, str) else value

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed.astimezone(tz) if tz else fixed.replace(tzinfo=None)

    with at_time(fixed), patch("MISC.utils.datetime", FrozenDateTime):
        yield fixed


@contextmanager
def audit_time(value):
    """Freeze the model field's captured callable as well as Django's live clock."""
    fixed = instant(value) if isinstance(value, str) else value
    field = LogEntry._meta.get_field("action_time")
    with at_time(fixed), patch.object(field, "_get_default", lambda: fixed):
        yield fixed
