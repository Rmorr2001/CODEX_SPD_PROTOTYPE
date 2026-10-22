"""Chapter public read model respects legacy display order and field boundaries."""
from django.test import TestCase
from AUTHENTICATE.models import Brother_Profile, Role


class PublicAboutApiTests(TestCase):
    def profile(self, first, last, *roles):
        profile = Brother_Profile.objects.create(firstName=first, lastName=last, hometown='Never serialize')
        for code in roles:
            profile.roles.add(Role.objects.get_or_create(name=code)[0])
        return profile

    def test_anonymous_empty_board_contract(self):
        response = self.client.get('/api/v1/public/about/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'active_count': 0, 'executives': []})
        self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_position_order_missing_roles_and_multi_role_members(self):
        self.profile('Robin', 'Chair', 'SOCIAL_CHAIR', 'ACTIVE')
        self.profile('Alex', 'Leader', 'PRESIDENT', 'INT_VP', 'ACTIVE')
        self.profile('Taylor', 'Alumni', 'ALUMNI')
        data = self.client.get('/api/v1/public/about/').json()
        self.assertEqual(data['active_count'], 2)
        self.assertEqual([(card['name'], card['position']) for card in data['executives']], [
            ('Alex Leader', 'President'), ('Alex Leader', 'Internal Vice President'),
            ('Robin Chair', 'Director of Social Affairs'),
        ])

    def test_card_payload_has_only_public_fields_with_null_image_fallback(self):
        self.profile('Alex', 'Example', 'PRESIDENT', 'EXEC', 'ACTIVE')
        data = self.client.get('/api/v1/public/about/').json()
        self.assertEqual(data, {'active_count': 1, 'executives': [{
            'name': 'Alex Example', 'position': 'President', 'image': None,
        }]})
        self.assertNotIn('Never serialize', str(data))

    def test_safe_public_image_url_and_no_write_methods(self):
        profile = self.profile('Alex', 'Example', 'PRESIDENT')
        profile.profileImage = 'profile_images/example.webp'
        # Update directly to avoid invoking image processing against a nonexistent fixture.
        Brother_Profile.objects.filter(pk=profile.pk).update(profileImage=profile.profileImage.name)
        response = self.client.get('/api/v1/public/about/')
        self.assertEqual(response.json()['executives'][0]['image'], '/media/profile_images/example.webp')
        self.assertEqual(self.client.post('/api/v1/public/about/', {}).status_code, 405)
        self.assertEqual(Brother_Profile.objects.count(), 1)
