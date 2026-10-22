"""Authenticated read contracts preserve caller privacy and dashboard landing behavior."""
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from AUTHENTICATE.models import Brother_Profile, DashboardLink, Role
from MISC.models import AnnouncementAlert


class IdentityReadApiTests(TestCase):
    def member(self, username='sample', roles=('ACTIVE',)):
        user = User.objects.create(username=username, email='private@example.invalid')
        profile = Brother_Profile.objects.create(user=user, firstName='Alex', lastName='Example', hometown='Private hometown')
        for code in roles:
            profile.roles.add(Role.objects.get_or_create(name=code)[0])
        return user

    def test_anonymous_session_is_minimal_no_store_and_sets_csrf_cookie(self):
        response = self.client.get('/api/v1/session/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'authenticated': False, 'profile_available': False,
                         'demo_enabled': False, 'landing_path': '/app/login', 'member': None})
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertIn('csrftoken', response.cookies)
        self.assertEqual(self.client.get('/api/v1/dashboard/').status_code, 403)

    def test_session_identity_is_only_the_caller_and_actual_capabilities(self):
        user = self.member(roles=('ACTIVE', 'EXEC'))
        self.member('another-person', ('ALUMNI',))
        self.client.force_login(user)
        data = self.client.get('/api/v1/session/').json()
        self.assertTrue(data['authenticated'])
        self.assertEqual(data['member']['display_name'], 'Alex Example')
        self.assertEqual({role['code'] for role in data['member']['roles']}, {'ACTIVE', 'EXEC'})
        self.assertTrue(data['member']['capabilities']['polls'])
        self.assertTrue(data['member']['capabilities']['service_hours'])
        self.assertEqual(data['landing_path'], '/app/dashboard')
        for private in ('private@example.invalid', 'Private hometown', 'another-person', 'session_key', 'password'):
            self.assertNotIn(private, str(data))

    def test_missing_profile_is_explicit_and_does_not_expose_dashboard(self):
        self.client.force_login(User.objects.create(username='unlinked'))
        data = self.client.get('/api/v1/session/').json()
        self.assertTrue(data['authenticated'])
        self.assertFalse(data['profile_available'])
        self.assertIsNone(data['member'])
        self.assertEqual(self.client.get('/api/v1/dashboard/').status_code, 403)

    def test_role_capabilities_match_active_newmember_and_alumni(self):
        for role, polls, landing in [('ACTIVE', True, '/app/dashboard'), ('NEW_MEMBER', False, '/app/new-members'), ('ALUMNI', False, '/app/dashboard')]:
            with self.subTest(role=role):
                self.client.force_login(self.member(role, (role,)))
                data = self.client.get('/api/v1/session/').json()
                self.assertEqual(data['member']['capabilities']['polls'], polls)
                self.assertEqual(data['member']['capabilities']['service_hours'], polls)
                self.assertEqual(data['landing_path'], landing)

    def test_dashboard_only_active_announcements_and_safe_ordered_links(self):
        self.client.force_login(self.member())
        visible = AnnouncementAlert.objects.create(title='Chapter notice', content='Plain text announcement')
        AnnouncementAlert.objects.create(title='Hidden notice', content='Do not expose', is_active=False)
        DashboardLink.objects.create(text='Later', link='/auth/profile/', order=4)
        DashboardLink.objects.create(text='First', link='https://example.invalid/resource', order=1)
        DashboardLink.objects.create(text='Unsafe', link='javascript:alert(1)', order=0)
        response = self.client.get('/api/v1/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        data = response.json()
        self.assertEqual([item['id'] for item in data['announcements']], [visible.pk])
        self.assertEqual(set(data['announcements'][0]), {'id', 'title', 'content', 'created_at'})
        self.assertEqual([link['text'] for link in data['links']], ['First', 'Later'])
        self.assertNotIn('Do not expose', str(data))

    def test_newmember_redirect_contract_precedes_general_dashboard_feed(self):
        self.client.force_login(self.member(roles=('ACTIVE', 'NEW_MEMBER')))
        AnnouncementAlert.objects.create(title='General notice', content='General feed')
        self.assertEqual(self.client.get('/api/v1/dashboard/').json(), {
            'landing_path': '/app/new-members', 'announcements': [], 'links': [],
        })

    def test_empty_dashboard_and_session_expiry(self):
        self.client.force_login(self.member())
        self.assertEqual(self.client.get('/api/v1/dashboard/').json(), {
            'landing_path': '/app/dashboard', 'announcements': [], 'links': [],
        })
        self.client.logout()
        self.assertEqual(self.client.get('/api/v1/dashboard/').status_code, 403)

    @override_settings(DEMO_MODE=True)
    def test_demo_flag_and_read_only_methods(self):
        self.assertTrue(self.client.get('/api/v1/session/').json()['demo_enabled'])
        self.client.force_login(self.member())
        self.assertEqual(self.client.post('/api/v1/session/', {}).status_code, 405)
        self.assertEqual(self.client.post('/api/v1/dashboard/', {}).status_code, 405)
