from urllib.parse import parse_qs, urlsplit

from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import reverse

from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import csrf_client, login_actor

from .support import (APPROVE, DASHBOARD, EXPORT, SUBMIT, Event, PhilanthropyCase,
                      edit, history, make_event, messages, payload)


class AccessTests(PhilanthropyCase):
    def setUp(self):
        super().setUp()
        self.a = make_user(username='a', roles=('ACTIVE',))
        self.b = make_user(username='b', roles=('ACTIVE',))
        self.e = make_event(self.b)
        self.f = make_event(self.b, title='Other', hours=7, status='approved')

    def requests(self, target=None):
        target = target or self.a
        return [('get', path, {}) for path in (
            DASHBOARD, SUBMIT, APPROVE, edit(self.e), history(target), EXPORT,
        )] + [
            ('post', SUBMIT, payload()),
            ('post', APPROVE, {'event_id': self.e.pk, 'action': 'approve'}),
            ('post', APPROVE, {'event_id': self.e.pk, 'action': 'deny'}),
            ('post', edit(self.e), payload(hours='3', event_title='Edited',
                                         event_date='2026-07-02')),
        ]

    def assert_denied(self, actor, requests, required, referrer=None):
        login_actor(self.client, actor)
        before = self.capture(actor, self.b, self.e, self.f)
        count = Event.objects.count()
        for method, path, data in requests:
            with self.subTest(actor=actor.username, method=method, path=path):
                extra = {'HTTP_REFERER': referrer} if referrer else {}
                response = getattr(self.client, method)(path, data, **extra)
                self.assertRedirects(response, referrer or '/legacy/',
                                     fetch_redirect_response=False)
                text = ' '.join(messages(response))
                for name in required:
                    self.assertIn(name, text)
                self.unchanged(before)
                self.assertEqual(Event.objects.count(), count)
                self.assert_session_actor(self.client, actor)

    def test_anonymous_domain_requests_require_login(self):
        before = self.capture(self.a, self.b, self.e, self.f)
        for method, path, data in self.requests():
            with self.subTest(method=method, path=path):
                response = getattr(self.client, method)(path, data)
                self.assertEqual(response.status_code, 302)
                parts = urlsplit(response.url)
                if path == APPROVE:
                    self.assertEqual(parts.path, reverse('login'))
                    self.assertEqual(parse_qs(parts.query), {})
                else:
                    self.assertEqual(parts.path, resolve_url(settings.LOGIN_URL))
                    self.assertEqual(parse_qs(parts.query), {'next': [path]})
                self.unchanged(before)
                self.assertEqual(Event.objects.count(), 2)

    def test_non_active_actors_cannot_submit_or_read_member_pages(self):
        for index, roles in enumerate(((), ('ALUMNI',), ('NEW_MEMBER',),
                                       ('EXEC',), ('PHIL_CHAIR',))):
            actor = make_user(username=f'non-active-{index}', roles=roles)
            requests = [('get', path, {}) for path in
                        (DASHBOARD, SUBMIT, history(actor))]
            requests.append(('post', SUBMIT, payload()))
            self.assert_denied(actor, requests, ['ACTIVE'])

    def test_approval_requires_both_narrow_roles(self):
        for index, roles in enumerate(((), ('ACTIVE',), ('PHIL_CHAIR',),
                                       ('EXEC',), ('ACTIVE', 'EXEC'))):
            actor = make_user(username=f'reviewer-{index}', roles=roles)
            missing = [r for r in ('PHIL_CHAIR', 'ACTIVE') if r not in roles]
            requests = [('get', APPROVE, {})] + [
                ('post', APPROVE, {'event_id': self.e.pk, 'action': action})
                for action in ('approve', 'deny')
            ]
            self.assert_denied(actor, requests, missing)

    def test_non_chairs_cannot_read_or_post_edit(self):
        for index, roles in enumerate(((), ('ACTIVE',), ('ALUMNI',),
                                       ('NEW_MEMBER',), ('EXEC',), ('ACTIVE', 'EXEC'))):
            actor = make_user(username=f'editor-{index}', roles=roles)
            self.assert_denied(actor, [('get', edit(self.e), {}),
                                      ('post', edit(self.e), payload(hours='3'))],
                               ['PHIL_CHAIR'])

    def test_missing_profiles_are_denied_by_role_decorators(self):
        actor = make_user(username='profileless', with_profile=False)
        requests = [request for request in self.requests(self.b) if request[1] != EXPORT]
        self.assert_denied(actor, requests, ['User profile not found.'])
        self.assertFalse(hasattr(actor, 'brother_profile'))

    def csrf_denial(self, path, data, roles):
        actor = make_user(username='csrf-actor', roles=roles)
        client = csrf_client()
        login_actor(client, actor)
        self.token(client, path)
        before = self.capture(actor, self.b, self.e, self.f)
        for token in (None, 'bad-token'):
            with self.subTest(token=token):
                posted = dict(data)
                if token is not None:
                    posted['csrfmiddlewaretoken'] = token
                response = client.post(path, posted)
                self.assertEqual(response.status_code, 403)
                self.unchanged(before)
                self.assertEqual(Event.objects.count(), 2)
                self.assert_session_actor(client, actor)

    def test_submit_csrf_rejects_absent_or_bad_token(self):
        self.csrf_denial(SUBMIT, payload(), ('ACTIVE',))

    def test_approve_csrf_rejects_absent_or_bad_token(self):
        self.csrf_denial(APPROVE, {'event_id': self.e.pk, 'action': 'approve'},
                         ('ACTIVE', 'PHIL_CHAIR'))

    def test_deny_csrf_rejects_absent_or_bad_token(self):
        self.csrf_denial(APPROVE, {'event_id': self.e.pk, 'action': 'deny'},
                         ('ACTIVE', 'PHIL_CHAIR'))

    def test_edit_csrf_rejects_absent_or_bad_token(self):
        self.csrf_denial(edit(self.e), payload(hours='3', event_title='Edited',
                                             event_date='2026-07-02'),
                         ('ACTIVE', 'PHIL_CHAIR'))

    def test_role_denial_uses_poll_without_referrer(self):
        self.assert_denied(self.a, [('get', APPROVE, {})], ['PHIL_CHAIR'])

    def test_role_denial_uses_safe_referrer(self):
        self.assert_denied(self.a, [('get', APPROVE, {})], ['PHIL_CHAIR'],
                           referrer='http://testserver/philanthropy/')
