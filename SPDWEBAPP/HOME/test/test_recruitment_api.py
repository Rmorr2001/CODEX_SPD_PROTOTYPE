"""Public recruitment config is ordered, safe, read-only, and honest when absent."""
from django.test import TestCase
from HOME.models import RushFormLink, RushSlide


class RecruitmentApiTests(TestCase):
    def test_empty_recruitment_contract_is_public(self):
        response = self.client.get('/api/v1/public/recruitment/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'interest_url': None, 'slides': []})
        self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_slides_preserve_order_captions_and_public_whitelist(self):
        RushSlide.objects.create(caption='Later chapter photo', order=9, image='rush_slides/later.webp')
        RushSlide.objects.create(caption='First chapter photo', order=1, image='rush_slides/first.webp')
        RushFormLink.objects.create(link='https://example.invalid/interest/')
        data = self.client.get('/api/v1/public/recruitment/').json()
        self.assertEqual(data, {'interest_url': 'https://example.invalid/interest/', 'slides': [
            {'caption': 'First chapter photo', 'image': '/media/rush_slides/first.webp'},
            {'caption': 'Later chapter photo', 'image': '/media/rush_slides/later.webp'},
        ]})

    def test_unsafe_and_self_referencing_interest_links_are_unavailable(self):
        for url in ('javascript:alert(1)', '//outside.invalid/', 'https://:80', '/app/join/', 'http://testserver/app/join?interest=1'):
            with self.subTest(url=url):
                RushFormLink.objects.create(link=url)
                self.assertIsNone(self.client.get('/api/v1/public/recruitment/').json()['interest_url'])

    def test_external_join_path_is_not_mistaken_for_self_reference(self):
        RushFormLink.objects.create(link='https://external.invalid/app/join/')
        self.assertEqual(self.client.get('/api/v1/public/recruitment/').json()['interest_url'], 'https://external.invalid/app/join/')

    def test_mutations_remain_unavailable(self):
        self.assertEqual(self.client.post('/api/v1/public/recruitment/', {}).status_code, 405)
        self.assertFalse(RushSlide.objects.exists())
