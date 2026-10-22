"""Public presentation contracts omit private information and unsafe links."""
from django.test import TestCase
from HOME.models import BannerImage, RushFormLink
from HOME.api import safe_public_url


class PublicHomeApiTests(TestCase):
    def test_missing_content_is_explicit_and_public(self):
        response = self.client.get('/api/v1/public/home/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'banner_image': None, 'rush_interest_url': None})
        self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_payload_whitelist_uses_existing_public_configuration(self):
        BannerImage.objects.create(image='banners/chapter.webp')
        RushFormLink.objects.create(link='https://example.invalid/interest/')
        response = self.client.get('/api/v1/public/home/')
        self.assertEqual(response.json(), {
            'banner_image': '/media/banners/chapter.webp',
            'rush_interest_url': 'https://example.invalid/interest/',
        })
        self.assertEqual(set(response.json()), {'banner_image', 'rush_interest_url'})

    def test_unsafe_configured_interest_url_is_not_exposed(self):
        for value in ('javascript:alert(1)', '//outside.invalid/', 'https://valid.invalid/\npath', '/\\outside.invalid/', 'https://[invalid', 'https://:80', 'https://user:password@example.invalid/'):
            with self.subTest(value=value):
                RushFormLink.objects.create(link=value)
                self.assertIsNone(self.client.get('/api/v1/public/home/').json()['rush_interest_url'])

    def test_safe_url_contract(self):
        self.assertEqual(safe_public_url('/rush/'), '/rush/')
        self.assertEqual(safe_public_url('https://example.invalid/'), 'https://example.invalid/')
        self.assertIsNone(safe_public_url('https:///missing-host'))

    def test_mutations_are_not_supported(self):
        response = self.client.post('/api/v1/public/home/', {})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(BannerImage.objects.count(), 0)
        self.assertEqual(RushFormLink.objects.count(), 0)
