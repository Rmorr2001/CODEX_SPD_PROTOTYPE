from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import Permission
from django.contrib.admin.models import LogEntry, DELETION
from django.urls import reverse

from NEWMEMBER.models import NewMember_Mark_Event_and_Request as Mark
from .support import WorkflowCase


class AdminTests(WorkflowCase):
    def admin_url(self, action, mark=None):
        name = f'admin:{Mark._meta.app_label}_{Mark._meta.model_name}_{action}'
        return reverse(name, args=[(mark or self.m).pk] if action in ['change', 'delete'] else None)

    def staff(self, name='staff', permissions=(), superuser=False):
        actor = self.user(name, is_staff=True, is_superuser=superuser)
        perms = Permission.objects.filter(content_type__app_label=Mark._meta.app_label,
                    codename__in=[action + '_' + Mark._meta.model_name for action in permissions])
        self.assertEqual(perms.count(), len(permissions))
        actor.user_permissions.add(*perms)
        self.login(actor)
        return actor

    def admin_payload(self):
        return {'mark_event_title': 'Workshop', 'mark_value': '2', 'mark_event_date': '2026-10-16',
                'mark_approval_status': 'requested', 'requesting_user': str(self.b.pk),
                'target_user': str(self.t1.pk), '_save': 'Save'}

    def assert_admin_login(self, response, path):
        self.assertEqual(response.status_code, 302)
        parsed = urlsplit(response.url)
        self.assertEqual(parsed.path, reverse('admin:login'))
        self.assertEqual(parse_qs(parsed.query)['next'], [path])

    def test_admin_nonstaff_redirects_even_with_board_role(self):
        self.login(self.r)
        before = self.capture()
        for action in ['changelist', 'add', 'change', 'delete']:
            path = self.admin_url(action)
            response = self.client.get(path)
            self.assert_admin_login(response, path)
            self.assertNotContains(response, 'Workshop', status_code=302)
            self.unchanged(before)
            self.identity(self.r)

    def test_admin_changelist_shows_configured_columns(self):
        actor = self.staff(superuser=True)
        before = self.capture()
        response = self.client.get(self.admin_url('changelist'))
        self.assertEqual(response.status_code, 200)
        for field in ['mark_event_title', 'target_user', 'requesting_user', 'mark_approval_status',
                      'mark_value', 'mark_event_date']:
            self.assertContains(response, 'column-' + field)
        self.assertEqual(list(response.context['cl'].result_list), [self.m, self.z])
        self.assertFalse(actor.brother_profile.roles.exists())
        self.unchanged(before)
        self.identity(actor)

    def test_admin_staff_without_permissions_is_forbidden(self):
        actor = self.staff()
        before = self.capture()
        for action in ['changelist', 'add', 'change', 'delete']:
            response = self.client.get(self.admin_url(action))
            self.assertEqual(response.status_code, 403)
            self.assertNotContains(response, 'Workshop', status_code=403)
            self.unchanged(before)
            self.identity(actor)
        self.assertFalse(actor.user_permissions.exists())

    def test_admin_staff_explicit_permission_allows_corresponding_page(self):
        for permission, action in [('view', 'changelist'), ('add', 'add'),
                                   ('change', 'change'), ('delete', 'delete')]:
            actor = self.staff('staff-' + permission, (permission,))
            before = self.capture()
            with self.subTest(permission=permission):
                response = self.client.get(self.admin_url(action))
                self.assertEqual(response.status_code, 200)
                if permission == 'view':
                    readonly = self.client.get(self.admin_url('change'))
                    self.assertEqual(readonly.status_code, 200)
                    self.assertNotContains(readonly, 'name="_save"')
                self.assertFalse(actor.brother_profile.roles.exists())
                self.unchanged(before)
                self.identity(actor)

    def test_admin_staff_without_write_permission_cannot_add_or_change(self):
        actor = self.staff(permissions=('view',))
        before = self.capture()
        for action in ['add', 'change']:
            response = self.client.post(self.admin_url(action), self.admin_payload())
            self.assertEqual(response.status_code, 403)
            self.unchanged(before)
            self.identity(actor)
        self.assertEqual(LogEntry.objects.count(), 0)

    def test_admin_nonstaff_cannot_add_or_change_through_admin(self):
        self.login(self.r)
        before = self.capture()
        for action in ['add', 'change']:
            path = self.admin_url(action)
            response = self.client.post(path, self.admin_payload())
            self.assert_admin_login(response, path)
            self.unchanged(before)
            self.identity(self.r)
        self.assertEqual(LogEntry.objects.count(), 0)

    def test_admin_forms_reject_invalid_model_fields(self):
        actor = self.staff(permissions=('add', 'change'))
        before = self.capture()
        variants = [('mark_value', 'abc'), ('mark_event_date', '2026-02-30'),
                    ('mark_approval_status', 'unknown'), ('requesting_user', None), ('target_user', None)]
        for action in ['add', 'change']:
            for field, value in variants:
                with self.subTest(action=action, field=field):
                    payload = self.admin_payload()
                    if value is None:
                        payload.pop(field)
                    else:
                        payload[field] = value
                    response = self.client.post(self.admin_url(action), payload)
                    self.assertEqual(response.status_code, 200)
                    form = response.context['adminform'].form
                    self.assertIn(field, form.errors)
                    self.assertContains(response, 'errorlist')
                    self.unchanged(before)
                    self.identity(actor)
        self.assertEqual(LogEntry.objects.count(), 0)

    def test_mark_string_representation_names_target(self):
        target = self.user('target-one', ('NEW_MEMBER',), username='target-one')
        mark = self.mark(self.a, target, value=-3)
        before = self.capture()
        self.assertEqual(str(mark), 'Workshop - target-one (-3)')
        for status in ['approved', 'denied']:
            mark.mark_approval_status = status
            mark.mark_approver_name = 'In-memory reviewer'
            mark.last_edited_by = self.r
            self.assertEqual(str(mark), 'Workshop - target-one (-3)')
        self.unchanged(before)

    def test_admin_mark_delete_removes_only_selected_mark(self):
        actor = self.staff(permissions=('view', 'delete'))
        before = self.capture(exclude=(self.m,))
        path = self.admin_url('delete')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workshop')
        response = self.client.post(path, {'post': 'yes'})
        self.assertRedirects(response, reverse('admin:index'), fetch_redirect_response=False)
        self.assertFalse(Mark.objects.filter(pk=self.m.pk).exists())
        self.assertTrue(Mark.objects.filter(pk=self.z.pk).exists())
        self.unchanged(before, count_delta=-1)
        log = LogEntry.objects.get()
        self.assertEqual((log.action_flag, log.user_id), (DELETION, actor.pk))
        self.identity(actor)

    def test_admin_delete_without_permission_preserves_records(self):
        actor = self.staff(permissions=('view',))
        before = self.capture()
        for method in ['get', 'post']:
            response = getattr(self.client, method)(self.admin_url('delete'), {'post': 'yes'})
            self.assertEqual(response.status_code, 403)
            self.unchanged(before)
            self.identity(actor)
        self.assertEqual(LogEntry.objects.count(), 0)
