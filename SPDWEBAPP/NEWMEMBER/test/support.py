"""Thin real-ORM mark fixtures and domain state assertions."""
from datetime import date, datetime, timezone
from pathlib import Path

from django.conf import settings
from django.contrib.messages import get_messages
from django.urls import reverse

from NEWMEMBER.models import NewMember_Mark_Event_and_Request as Mark
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import at_time, login_actor
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged

NOW = datetime(2026, 10, 17, 12, tzinfo=timezone.utc)
SUBMITTED = datetime(2026, 10, 16, 15, tzinfo=timezone.utc)
APPROVED = datetime(2026, 10, 16, 16, tzinfo=timezone.utc)
APPROVAL_FIELDS = ('mark_approval_status', 'mark_approver_name',
                   'mark_submission_approval_date')
EDITOR_FIELDS = ('last_edited_by_id', 'last_edited_at')


class MarkCase(RegressionTestCase):
    def setUp(self):
        super().setUp()
        self.rows = []
        self.users = []

    def user(self, name, roles=(), **kwargs):
        fields = kwargs.pop('profile_fields', {})
        fields = {'firstName': name.title(), 'lastName': 'Example', **fields}
        if kwargs.get('with_profile') is False:
            fields = None
        user = make_user(username=kwargs.pop('username', 'nm-' + name), roles=roles,
                         profile_fields=fields, **kwargs)
        self.rows.append(user)
        self.users.append(user)
        if kwargs.get('with_profile') is not False:
            self.rows.append(user.brother_profile)
        return user

    def mark(self, requester, target, *, status='requested', value=2,
             day='2026-10-16', title='Workshop', **audit):
        fields = dict(requesting_user=requester, target_user=target,
                      mark_event_title=title, mark_value=value,
                      mark_event_date=date.fromisoformat(day),
                      mark_approval_status=status)
        if status != 'requested':
            fields.update(mark_approver_name='Prior Reviewer',
                          mark_submission_approval_date=APPROVED)
        fields.update(audit)
        with at_time(SUBMITTED):
            mark = Mark.objects.create(**fields)
        self.rows.append(mark)
        return mark

    def login(self, actor, client=None):
        client = client or self.client
        login_actor(client, actor)
        return client

    def capture(self, exclude=()):
        rows = [r for r in self.rows if r not in exclude]
        relations = []
        for user in self.users:
            relations.extend([user.user_permissions, user.groups])
            if hasattr(user, 'brother_profile'):
                relations.extend([user.brother_profile.roles, user.brother_profile.majors])
        files = {str(p): p.read_bytes() for p in Path(settings.MEDIA_ROOT).rglob('*')
                 if p.is_file()}
        return snapshot_scope(rows, relations=relations), Mark.objects.count(), files

    def unchanged(self, before, *, count_delta=0):
        snapshot, count, files = before
        assert_unchanged(snapshot)
        self.assertEqual(Mark.objects.count(), count + count_delta)
        self.assertEqual({str(p): p.read_bytes() for p in Path(settings.MEDIA_ROOT).rglob('*')
                          if p.is_file()}, files)

    def identity(self, actor, client=None):
        self.assertEqual((client or self.client).session.get('_auth_user_id'), str(actor.pk))

    def message(self, response, text):
        self.assertTrue(any(text in str(m) for m in get_messages(response.wsgi_request)))

    def mark_state(self, mark):
        return Mark.objects.values().get(pk=mark.pk)

    def assert_changes(self, mark, before, **changes):
        self.assertEqual(self.mark_state(mark), {**before, **changes})

    def payload(self, target=None, **overrides):
        return {'action': 'update', 'mark_reason': 'Lab', 'mark_value': '-2',
                'mark_date': '2026-10-16', 'target_user': (target or self.t1).pk,
                **overrides}

    def edit_url(self, mark=None):
        return reverse('newmember_edit_mark', args=[(mark or self.m).pk])


class WorkflowCase(MarkCase):
    def setUp(self):
        super().setUp()
        self.a = self.user('a', ('ACTIVE',), profile_fields={'firstName': 'Alex', 'lastName': 'Able'})
        self.b = self.user('b')
        self.r = self.user('r', ('NM_BOARD',), profile_fields={'firstName': 'Rae', 'lastName': 'Reviewer'})
        self.t1 = self.user('t1', ('NEW_MEMBER',), profile_fields={'lastName': 'Able'})
        self.t2 = self.user('t2', ('NEW_MEMBER',), profile_fields={'lastName': 'Zed'})
        self.m = self.mark(self.b, self.t1)
        self.z = self.mark(self.b, self.t2, status='approved', value=7,
                           day='2026-10-01', title='Stable')
