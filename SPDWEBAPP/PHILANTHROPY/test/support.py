"""Thin event fixtures and domain assertions; shared harness stays in CORE."""
from datetime import date, datetime, timezone
import re

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse

from PHILANTHROPY.models import Philanthropy_Hours_Event_and_Request as Event
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope

T0 = datetime(2026, 7, 1, 9, tzinfo=timezone.utc)
T1 = datetime(2026, 7, 2, 12, tzinfo=timezone.utc)
SUBMIT = reverse('philanthropy_request')
APPROVE = reverse('philanthropy_approve')
DASHBOARD = reverse('philanthropy_dashboard')
EXPORT = reverse('export_philanthropy_hours')


def make_event(owner, *, title='Park', hours=2, day=date(2026, 7, 1),
               status='requested', **audit):
    return Event.objects.create(
        user=owner, philanthropy_event_title=title,
        philanthropy_event_hours=hours, philanthropy_event_date=day,
        philanthropy_approval_status=status, **audit,
    )


def payload(**changes):
    fields = {'hours': '2', 'event_title': 'Park', 'event_date': '2026-07-01'}
    fields.update(changes)
    return fields


def history(user):
    return reverse('brother_philanthropy_history', args=[user.pk])


def edit(event):
    return reverse('philanthropy_edit_event', args=[event.pk])


def messages(response):
    return [str(message) for message in get_messages(response.wsgi_request)]


class PhilanthropyAssertions:
    def capture(self, *rows):
        """Capture named existing rows; relation snapshots use the shared interface."""
        named = list(rows)
        relations = {}
        for row in rows:
            if isinstance(row, User) and hasattr(row, 'brother_profile'):
                named.append(row.brother_profile)
                relations[f'user-{row.pk}-roles'] = row.brother_profile.roles
            if isinstance(row, User):
                relations[f'user-{row.pk}-permissions'] = row.user_permissions
        return snapshot_scope(named, relations=relations)

    def unchanged(self, before):
        assert_unchanged(before)

    def token(self, client, path):
        response = client.get(path)
        self.assertEqual(response.status_code, 200)
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"',
                          response.content.decode())
        self.assertIsNotNone(match, 'The real form must contain a CSRF token')
        self.assertIn('csrftoken', client.cookies)
        return match.group(1)

    def assert_session_actor(self, client, user):
        self.assertEqual(client.session.get('_auth_user_id'), str(user.pk))

    def assert_requested(self, event, owner, *, title='Park', hours=2,
                         day=date(2026, 7, 1)):
        event.refresh_from_db()
        self.assertEqual(event.user_id, owner.pk)
        self.assertEqual(event.philanthropy_event_title, title)
        self.assertEqual(event.philanthropy_event_hours, hours)
        self.assertEqual(event.philanthropy_event_date, day)
        self.assertEqual(event.philanthropy_approval_status, 'requested')
        self.assertIsNone(event.philanthropy_event_approver_name)
        self.assertIsNone(event.philanthropy_event_submission_approval_date)
        self.assertIsNone(event.last_edited_by_id)
        self.assertIsNone(event.last_edited_at)


class PhilanthropyCase(PhilanthropyAssertions, RegressionTestCase):
    """The ordinary atomic TestCase boundary for domain tests."""
