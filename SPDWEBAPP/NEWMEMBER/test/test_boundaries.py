from urllib.parse import parse_qs, urlsplit

from django.urls import reverse

from NEWMEMBER.models import NewMember_Mark_Event_and_Request as Mark
from SPDWEBAPP_CORE.testing.helpers import csrf_client, at_time
from .support import WorkflowCase, NOW


class BoundaryTests(WorkflowCase):
    def test_landing_renders_public_navigation(self):
        for actor in [None, self.b]:
            if actor:
                self.login(actor)
            before = self.capture()
            response = self.client.get('/newmember/')
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'newmember_dashboard.html')
            for name in ['newmember_marks_dashboard', 'roster', 'alumni_roster']:
                self.assertContains(response, 'href="' + reverse(name) + '"')
            self.unchanged(before)
            if actor:
                self.identity(actor)

    def test_anonymous_routes_redirect_to_login(self):
        client = csrf_client()
        client.get(reverse('login'))
        token = client.cookies['csrftoken'].value
        before = self.capture()
        paths = ['/newmember/marks/', '/newmember/request/', '/newmember/approve/',
                 self.edit_url(), reverse('newmember_mark_history', args=[self.t1.pk]),
                 reverse('export_newmember_marks')]
        for path in paths:
            for method in ['get', 'post']:
                with self.subTest(path=path, method=method):
                    data = {'csrfmiddlewaretoken': token} if method == 'post' else {}
                    response = getattr(client, method)(path, data)
                    self.assertEqual(response.status_code, 302)
                    parsed = urlsplit(response.url)
                    self.assertEqual(parsed.path, reverse('login'))
                    self.assertEqual(parse_qs(parsed.query)['next'], [path])
                    self.assertNotContains(response, 'Workshop', status_code=302)
                    self.assertNotIn('_auth_user_id', client.session)
        self.unchanged(before)

    def test_request_requires_explicit_active_role(self):
        for i, roles in enumerate([(), ('ALUMNI',), ('EXEC',), ('NME',), ('NM_BOARD',)]):
            actor = self.user('denied-create-' + str(i), roles)
            self.login(actor)
            before = self.capture()
            for method in ['get', 'post']:
                with self.subTest(roles=roles, method=method):
                    response = getattr(self.client, method)(reverse('newmember_request'), {
                        'target_users': [self.t1.pk], 'mark_value': '2',
                        'mark_reason': 'Workshop', 'mark_date': '2026-10-16'})
                    self.assertRedirects(response, reverse('newmember_marks_dashboard'), fetch_redirect_response=False)
                    self.message(response, 'Only active members')
                    self.identity(actor)
                    self.unchanged(before)

    def test_review_and_regular_edit_require_board_role(self):
        for i, roles in enumerate([(), ('ACTIVE',), ('ALUMNI',), ('EXEC',), ('NME',)]):
            actor = self.user('denied-review-' + str(i), roles)
            self.login(actor)
            for own in [False, True]:
                Mark.objects.filter(pk=self.m.pk).update(requesting_user=actor if own else self.b)
                before = self.capture()
                for path, payload in [(reverse('newmember_approve'), {'mark_id': self.m.pk, 'action': 'approve'}),
                                      (self.edit_url(), self.payload())]:
                    for method in ['get', 'post']:
                        with self.subTest(roles=roles, own=own, path=path, method=method):
                            response = getattr(self.client, method)(path, payload)
                            self.assertRedirects(response, reverse('newmember_marks_dashboard'), fetch_redirect_response=False)
                            self.message(response, 'Only New Member Board')
                            self.identity(actor)
                            self.unchanged(before)

    def test_edit_deny_requires_both_roles(self):
        for i, roles in enumerate([('NM_BOARD',), ('NME',)]):
            actor = self.user('denied-deny-' + str(i), roles)
            self.login(actor)
            for own in [False, True]:
                Mark.objects.filter(pk=self.m.pk).update(requesting_user=actor if own else self.b)
                before = self.capture()
                response = self.client.post(self.edit_url(), {'action': 'deny'})
                self.assertRedirects(response, reverse('newmember_marks_dashboard'), fetch_redirect_response=False)
                self.message(response, 'Only New Member Educators' if i == 0 else 'Only New Member Board')
                self.identity(actor)
                self.unchanged(before)

    def csrf_setup(self):
        actor = self.user('csrf', ('ACTIVE', 'NM_BOARD', 'NME'))
        client = self.login(actor, csrf_client())
        return actor, client

    def test_mutating_routes_reject_missing_or_bad_csrf(self):
        actor, client = self.csrf_setup()
        variants = [(reverse('newmember_request'), {'target_users': [self.t1.pk], 'mark_value': '2',
                     'mark_reason': 'Workshop', 'mark_date': '2026-10-16'}),
                    (reverse('newmember_approve'), {'mark_id': self.m.pk, 'action': 'approve'}),
                    (self.edit_url(), self.payload()), (self.edit_url(), {'action': 'deny'})]
        for path, payload in variants:
            client.get(path)
            before = self.capture()
            for token in [None, 'wrong-token']:
                with self.subTest(path=path, token=token, action=payload.get('action')):
                    data = dict(payload)
                    if token is not None:
                        data['csrfmiddlewaretoken'] = token
                    response = client.post(path, data)
                    self.assertEqual(response.status_code, 403)
                    self.unchanged(before)
                    self.identity(actor, client)

    def csrf_post(self, operation):
        actor, client = self.csrf_setup()
        paths = {'create': reverse('newmember_request'), 'approve': reverse('newmember_approve'),
                 'update': self.edit_url(), 'deny': self.edit_url()}
        payloads = {'create': {'target_users': [self.t1.pk], 'mark_value': '2',
                              'mark_reason': 'Workshop', 'mark_date': '2026-10-16'},
                    'approve': {'mark_id': self.m.pk, 'action': 'approve'},
                    'update': self.payload(), 'deny': {'action': 'deny'}}
        client.get(paths[operation])
        token = client.cookies['csrftoken'].value
        before = self.capture(exclude=() if operation == 'create' else (self.m,))
        old = self.mark_state(self.m)
        with at_time(NOW):
            response = client.post(paths[operation], {**payloads[operation], 'csrfmiddlewaretoken': token})
        if operation == 'approve':
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'newmember_marks_approve.html')
        else:
            target = reverse('newmember_mark_history', args=[self.t1.pk]) if operation == 'update' else reverse('newmember_marks_dashboard')
            self.assertRedirects(response, target, fetch_redirect_response=False)
        self.message(response, 'successfully' if operation != 'update' else 'updated successfully')
        name = actor.brother_profile.firstName + ' ' + actor.brother_profile.lastName
        if operation == 'create':
            mark = Mark.objects.exclude(pk__in=[self.m.pk, self.z.pk]).get()
            self.assertEqual((mark.target_user_id, mark.requesting_user_id, mark.mark_value,
                              mark.mark_event_title, mark.mark_event_date.isoformat(),
                              mark.mark_approval_status, mark.mark_approver_name),
                             (self.t1.pk, actor.pk, 2, 'Workshop', '2026-10-16', 'approved', name))
            self.assertEqual(mark.mark_submission_request_date, NOW)
            self.assertEqual(mark.mark_submission_approval_date, NOW)
            self.assertIsNone(mark.last_edited_by_id)
            self.assertIsNone(mark.last_edited_at)
        elif operation == 'update':
            self.assert_changes(self.m, old, mark_event_title='Lab', mark_value=-2,
                                last_edited_by_id=actor.pk, last_edited_at=NOW)
        else:
            changes = dict(mark_approval_status='approved' if operation == 'approve' else 'denied',
                           mark_approver_name=name, mark_submission_approval_date=NOW)
            if operation == 'deny':
                changes.update(last_edited_by_id=actor.pk, last_edited_at=NOW)
            self.assert_changes(self.m, old, **changes)
        self.unchanged(before, count_delta=1 if operation == 'create' else 0)
        self.identity(actor, client)

    def test_create_accepts_acquired_csrf_token(self):
        self.csrf_post('create')

    def test_approve_accepts_acquired_csrf_token(self):
        self.csrf_post('approve')

    def test_update_accepts_acquired_csrf_token(self):
        self.csrf_post('update')

    def test_edit_deny_accepts_acquired_csrf_token(self):
        self.csrf_post('deny')
