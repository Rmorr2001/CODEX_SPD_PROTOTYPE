from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import at_time, login_actor
from SPDWEBAPP_CORE.testing.state import assert_unchanged

from .support import T1, Event, PhilanthropyCase, make_event


class AdminTests(PhilanthropyCase):
    def setUp(self):
        super().setUp()
        self.b = make_user(username='b', roles=('ACTIVE',))
        self.e = make_event(self.b, title='Target')
        self.f = make_event(self.b, title='Control', status='approved')
        self.content_type = ContentType.objects.get_for_model(Event)

    def staff(self, name, *permissions, superuser=False):
        actor = make_user(username=name, is_staff=True, is_superuser=superuser)
        actor.user_permissions.set(Permission.objects.filter(
            content_type=self.content_type,
            codename__in=[f'{action}_{Event._meta.model_name}' for action in permissions]))
        self.assertEqual(actor.user_permissions.count(), len(permissions))
        self.assertEqual(list(actor.brother_profile.roles.all()), [])
        return actor

    def url(self, action, event=None):
        return reverse(f'admin:PHILANTHROPY_{Event._meta.model_name}_{action}',
                       args=[event.pk] if event else None)

    def form(self, **changes):
        data = {'user': self.b.pk, 'philanthropy_event_title': 'Park',
                'philanthropy_event_hours': '2', 'philanthropy_event_date': '2026-07-01',
                'philanthropy_approval_status': 'requested', '_save': 'Save'}
        data.update(changes)
        return data

    def test_admin_list_obeys_staff_and_model_permissions(self):
        chair = make_user(username='nonstaff-chair', roles=('ACTIVE', 'PHIL_CHAIR'))
        none = self.staff('no-permission')
        viewer = self.staff('viewer', 'view')
        superuser = self.staff('superuser', superuser=True)
        actors = [chair, none, viewer, superuser]
        for actor, status in zip(actors, (302, 403, 200, 200)):
            with self.subTest(actor=actor.username):
                login_actor(self.client, actor)
                before = self.capture(self.b, self.e, self.f, *actors)
                response = self.client.get(self.url('changelist'))
                self.assertEqual(response.status_code, status)
                if status == 302:
                    self.assertTrue(response.url.startswith(reverse('admin:login') + '?next='))
                if status == 200:
                    columns = [c for c in response.context['cl'].list_display
                               if c != 'action_checkbox']
                    self.assertEqual(columns, ['philanthropy_event_title', 'user',
                                               'philanthropy_approval_status',
                                               'philanthropy_event_hours',
                                               'philanthropy_event_date'])
                    self.assertContains(response, 'Target')
                    self.assertContains(response, 'Control')
                self.unchanged(before)
                self.assertEqual(LogEntry.objects.count(), 0)
                self.assertEqual(Event.objects.count(), 2)

    def test_admin_permission_denied_add_and_change_do_not_write(self):
        actor = self.staff('viewer', 'view')
        login_actor(self.client, actor)
        before = self.capture(actor, self.b, self.e, self.f)
        for path, data in ((self.url('add'), self.form()),
                           (self.url('change', self.e),
                            self.form(philanthropy_event_title='Edited'))):
            response = self.client.post(path, data)
            self.assertEqual(response.status_code, 403)
            self.unchanged(before)
            self.assertEqual(Event.objects.count(), 2)
            self.assertEqual(LogEntry.objects.count(), 0)

    def test_admin_permission_sets_do_not_imply_domain_roles(self):
        actors = [self.staff(action, action) for action in ('add', 'change', 'delete')]
        for actor, allowed in zip(actors, ('add', 'change', 'delete')):
            login_actor(self.client, actor)
            before = self.capture(self.b, self.e, self.f, *actors)
            for action in ('add', 'change', 'delete'):
                with self.subTest(actor=actor.username, action=action):
                    path = self.url(action, None if action == 'add' else self.e)
                    response = self.client.get(path)
                    self.assertEqual(response.status_code, 200 if action == allowed else 403)
                    self.unchanged(before)
            self.assertEqual(LogEntry.objects.count(), 0)
            self.assertEqual(Event.objects.count(), 2)

    def test_admin_adds_integer_event_and_django_log(self):
        actor = self.staff('adder', 'add', 'view')
        login_actor(self.client, actor)
        before = self.capture(actor, self.b, self.e, self.f)
        with at_time(T1):
            response = self.client.post(self.url('add'), self.form())
        self.assertRedirects(response, self.url('changelist'), fetch_redirect_response=False)
        self.assertEqual(Event.objects.count(), 3)
        event = Event.objects.exclude(pk__in=[self.e.pk, self.f.pk]).get()
        self.assert_requested(event, self.b)
        self.assertEqual(event.philanthropy_event_submission_request_date, T1)
        entry = LogEntry.objects.get()
        self.assertEqual(entry.user_id, actor.pk)
        self.assertEqual(entry.content_type_id, self.content_type.pk)
        self.assertEqual(entry.object_id, str(event.pk))
        self.assertEqual(entry.action_flag, ADDITION)
        self.unchanged(before)

    def test_admin_model_form_rejects_invalid_fields_without_logs(self):
        actor = self.staff('editor', 'add', 'change')
        login_actor(self.client, actor)
        before = self.capture(actor, self.b, self.e, self.f)
        variants = [('philanthropy_approval_status', 'bogus'),
                    ('philanthropy_event_title', 'x' * 101),
                    ('philanthropy_event_hours', '1.5'),
                    ('philanthropy_event_hours', 'NaN'),
                    ('philanthropy_event_hours', 'abc'),
                    ('philanthropy_event_date', 'abc'),
                    ('philanthropy_event_date', '2026-02-30')]
        variants += [(field, None) for field in ('user', 'philanthropy_event_title',
                     'philanthropy_event_hours', 'philanthropy_event_date')]
        for path in (self.url('add'), self.url('change', self.e)):
            for field, value in variants:
                with self.subTest(path=path, field=field, value=value):
                    data = self.form()
                    if value is None:
                        data.pop(field)
                    else:
                        data[field] = value
                    response = self.client.post(path, data)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(field, response.context['adminform'].form.errors)
                    self.assertEqual(Event.objects.count(), 2)
                    self.assertEqual(LogEntry.objects.count(), 0)
                    self.unchanged(before)

    def test_admin_delete_confirmation_does_not_delete(self):
        actor = self.staff('deleter', 'delete')
        login_actor(self.client, actor)
        before = self.capture(actor, self.b, self.e, self.f)
        response = self.client.get(self.url('delete', self.e))
        self.assertContains(response, 'Target')
        self.assertContains(response, 'post')
        self.unchanged(before)
        self.assertEqual(LogEntry.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 2)

    def test_admin_delete_denial_preserves_events_and_logs(self):
        actor = self.staff('not-deleter', 'view', 'change')
        login_actor(self.client, actor)
        before = self.capture(actor, self.b, self.e, self.f)
        response = self.client.post(self.url('delete', self.e), {'post': 'yes'})
        self.assertEqual(response.status_code, 403)
        response = self.client.post(self.url('changelist'),
                                    {'action': 'delete_selected',
                                     '_selected_action': [str(self.e.pk)], 'post': 'yes'})
        self.assertIn(response.status_code, (200, 302))
        self.unchanged(before)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(LogEntry.objects.count(), 0)

    def test_editor_deletion_sets_null_on_other_owners_event(self):
        a = make_user(username='a', roles=('ACTIVE',))
        editor = make_user(username='editor', with_profile=False)
        self.e.philanthropy_approval_status = 'approved'
        self.e.last_edited_by = editor
        self.e.last_edited_at = T1
        self.e.save()
        self.f.user = a
        self.f.save()
        before = self.capture(a, self.b, self.e, self.f)
        editor_pk = editor.pk
        editor.delete()
        self.assertFalse(User.objects.filter(pk=editor_pk).exists())
        self.e.refresh_from_db()
        self.assertIsNone(self.e.last_edited_by_id)
        self.assertEqual(self.e.last_edited_at, T1)
        assert_unchanged(before, except_fields={self.e: {'last_edited_by_id'}})
        self.assertEqual(LogEntry.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 2)
