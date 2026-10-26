"""Primary React landing, retained HTML routes, safe auth destinations and POST logout."""
from django.test import Client
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user, TEST_PASSWORD


class ReactEntryTests(RegressionTestCase):
    def test_primary_home_and_original_home_are_distinct(self):
        self.assertRedirects(self.client.get('/'), '/app/', fetch_redirect_response=False)
        self.assertTemplateUsed(self.client.get('/legacy/'), 'HOME/home.html')
        self.assertEqual(self.client.get('/rush/').status_code, 200)

    def test_login_uses_role_landing_and_rejects_external_next(self):
        for role, landing in [('ACTIVE', '/app/dashboard'), ('NEW_MEMBER', '/app/new-members')]:
            user = make_user(username=f'member-{role}', roles=(role,))
            for query in ('', '?next=https://attacker.invalid/', '?next=//attacker.invalid/'):
                self.client.logout()
                response = self.client.post('/auth/login/' + query, {'username': user.username, 'password': TEST_PASSWORD})
                self.assertRedirects(response, landing, fetch_redirect_response=False)

    def test_explicit_legacy_next_still_works(self):
        user = make_user(username='legacy-member', roles=('ACTIVE',))
        response = self.client.post('/auth/login/?next=/auth/roster/', {'username': user.username, 'password': TEST_PASSWORD})
        self.assertRedirects(response, '/auth/roster/', fetch_redirect_response=False)

    def test_logout_get_only_confirms_and_post_requires_csrf(self):
        user = make_user(username='logout-member', roles=('ACTIVE',))
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        self.assertEqual(client.get('/auth/logout/').status_code, 200)
        self.assertEqual(client.session['_auth_user_id'], str(user.pk))
        self.assertEqual(client.post('/auth/logout/').status_code, 403)
        token = client.cookies['csrftoken'].value
        response = client.post('/auth/logout/', {'csrfmiddlewaretoken': token})
        self.assertRedirects(response, '/app/', fetch_redirect_response=False)
        self.assertNotIn('_auth_user_id', client.session)

    def test_denied_legacy_route_never_redirects_to_itself_or_external_referrer(self):
        user = make_user(username='alumni-denied', roles=('ALUMNI',))
        self.client.force_login(user)
        for referrer in ('https://attacker.invalid/', '/poll/'):
            response = self.client.get('/poll/', HTTP_REFERER=referrer)
            self.assertRedirects(response, '/legacy/', fetch_redirect_response=False)
