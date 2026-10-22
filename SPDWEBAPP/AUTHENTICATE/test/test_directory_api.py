"""Directory contracts preserve roster membership sets and omit private fields."""
from django.contrib.auth.models import User
from django.test import TestCase
from AUTHENTICATE.models import Brother_Profile, Major, Role


class DirectoryApiTests(TestCase):
    def profile(self, username, last, *roles):
        user = User.objects.create(username=username, email='do-not-expose@example.invalid')
        profile = Brother_Profile.objects.create(user=user, firstName='Alex', lastName=last, hometown='Private home', pclass='Alpha')
        for code in roles:
            profile.roles.add(Role.objects.get_or_create(name=code)[0])
        return user, profile

    def setUp(self):
        self.user, self.current = self.profile('caller', 'Zulu', 'ACTIVE', 'EXEC')
        self.alumni, _ = self.profile('alum', 'Alpha', 'ALUMNI', 'ACTIVE')
        _, self.new_member = self.profile('new-member', 'Beta', 'NEW_MEMBER')

    def test_anonymous_and_missing_profile_are_denied(self):
        self.assertEqual(self.client.get('/api/v1/members/').status_code, 403)
        self.client.force_login(User.objects.create(username='missing-profile'))
        self.assertEqual(self.client.get('/api/v1/members/').status_code, 403)

    def test_current_roster_excludes_any_alumni_and_sorts_last_name_distinctly(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/v1/members/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertEqual([member['id'] for member in response.json()['members']], [self.new_member.pk, self.current.pk])
        self.assertEqual(len(response.json()['members']), 2)

    def test_alumni_roster_includes_dual_role_profile(self):
        self.client.force_login(self.user)
        data = self.client.get('/api/v1/members/?group=alumni').json()
        self.assertEqual(data['group'], 'alumni')
        self.assertEqual([member['display_name'] for member in data['members']], ['Alex Alpha'])
        self.assertEqual({role['code'] for role in data['members'][0]['roles']}, {'ACTIVE', 'ALUMNI'})

    def test_whitelist_major_image_and_pclass(self):
        self.current.majors.add(Major.objects.create(name='Mechanical Engineering'))
        Brother_Profile.objects.filter(pk=self.current.pk).update(profileImage='profile_images/member.webp')
        self.client.force_login(self.user)
        data = self.client.get('/api/v1/members/').json()
        member = next(member for member in data['members'] if member['id'] == self.current.pk)
        self.assertEqual(set(member), {'id', 'display_name', 'roles', 'majors', 'pclass', 'image'})
        self.assertEqual(member['majors'], ['Mechanical Engineering'])
        self.assertEqual(member['pclass'], 'Alpha')
        self.assertEqual(member['image'], '/media/profile_images/member.webp')
        for private in ('do-not-expose@example.invalid', 'Private home', 'username', 'password'):
            self.assertNotIn(private, str(data))

    def test_invalid_group_read_only_methods_and_empty_roster(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/api/v1/members/?group=invalid').status_code, 400)
        self.assertEqual(self.client.post('/api/v1/members/', {}).status_code, 405)
        Brother_Profile.objects.filter(roles__name='ALUMNI').delete()
        self.assertEqual(self.client.get('/api/v1/members/?group=alumni').json()['members'], [])
