"""Own-profile reads cannot select another account or mutate membership data."""
from django.contrib.auth.models import User
from django.test import TestCase
from AUTHENTICATE.models import Brother_Profile, Major, Role


class OwnProfileApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='own-account', email='own@example.invalid')
        self.profile = Brother_Profile.objects.create(user=self.user, firstName='Alex', lastName='Example', hometown='Own home', pclass='Alpha')
        self.profile.majors.add(Major.objects.create(name='Mechanical Engineering'))
        self.profile.roles.add(Role.objects.create(name='ACTIVE'))
        self.other = User.objects.create(username='other-account', email='other@example.invalid')
        self.other_profile = Brother_Profile.objects.create(user=self.other, firstName='Other', lastName='Member', hometown='Other home')

    def test_anonymous_and_profile_missing_are_denied(self):
        self.assertEqual(self.client.get('/api/v1/profile/').status_code, 403)
        self.client.force_login(User.objects.create(username='no-profile'))
        self.assertEqual(self.client.get('/api/v1/profile/').status_code, 403)

    def test_real_own_fields_and_explicit_whitelist(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/v1/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        data = response.json()
        self.assertEqual(set(data), {'display_name', 'first_name', 'last_name', 'username', 'email', 'hometown', 'pclass', 'majors', 'roles', 'image'})
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['hometown'], 'Own home')
        self.assertEqual(data['majors'], ['Mechanical Engineering'])
        self.assertIsNone(data['image'])
        self.assertNotIn('password', data)

    def test_query_parameter_injection_always_resolves_the_caller(self):
        self.client.force_login(self.user)
        for query in (f'?user_id={self.other.pk}', f'?profile_id={self.other_profile.pk}', '?username=other-account'):
            with self.subTest(query=query):
                data = self.client.get('/api/v1/profile/' + query).json()
                self.assertEqual(data['username'], self.user.username)
                self.assertNotIn('other@example.invalid', str(data))
                self.assertNotIn('Other home', str(data))
        self.assertEqual(self.client.get(f'/api/v1/profile/{self.other.pk}/').status_code, 404)

    def test_optional_fields_and_safe_image(self):
        self.client.force_login(self.other)
        data = self.client.get('/api/v1/profile/').json()
        self.assertIsNone(data['pclass'])
        self.assertEqual(data['majors'], [])
        Brother_Profile.objects.filter(pk=self.other_profile.pk).update(profileImage='profile_images/own.webp')
        self.assertEqual(self.client.get('/api/v1/profile/').json()['image'], '/media/profile_images/own.webp')

    def test_no_write_methods_and_no_other_account_changes(self):
        self.client.force_login(self.user)
        for method in ('post', 'patch', 'delete'):
            with self.subTest(method=method):
                self.assertEqual(getattr(self.client, method)('/api/v1/profile/', {'username': 'changed'}).status_code, 405)
        self.user.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(self.user.username, 'own-account')
        self.assertEqual(self.other.username, 'other-account')
