"""Optional React return paths never open arbitrary redirects or bypass CSRF/demo scope."""
from pathlib import Path
from tempfile import TemporaryDirectory
from django.core.management import call_command
from django.test import Client, TestCase, override_settings


class DemoReturnTests(TestCase):
    def setUp(self):
        self.media = TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        override = override_settings(MEDIA_ROOT=Path(self.media.name), DEMO_MODE=True, ROOT_URLCONF="railway_demo.urls")
        override.enable()
        self.addCleanup(override.disable)
        call_command('seed_railway_demo', verbosity=0)

    def test_absent_and_invalid_return_use_react_defaults(self):
        self.assertEqual(self.client.post('/demo/enter/', {'persona': 'active'}).url, '/app/dashboard')
        self.assertEqual(self.client.post('/demo/enter/', {'persona': 'alumni'}).url, '/app/dashboard')
        for path in ('https://outside.invalid/', '//outside.invalid/', '/app/dashboard?next=bad', '/app/not-real'):
            with self.subTest(path=path):
                self.assertEqual(self.client.post('/demo/enter/', {'persona': 'active', 'next': path}).url, '/app/dashboard')

    def test_safe_return_and_newmember_landing(self):
        self.assertEqual(self.client.post('/demo/enter/', {'persona': 'executive', 'next': '/app/dashboard'}).url, '/app/dashboard')
        self.assertEqual(self.client.post('/demo/enter/', {'persona': 'newmember', 'next': '/app/dashboard'}).url, '/app/new-members')
        self.assertEqual(self.client.post('/demo/enter/', {'persona': 'active', 'next': '/app/new-members'}).url, '/app/new-members')

    def test_native_demo_entry_stays_csrf_protected_and_works_with_real_token(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/demo/enter/', {'persona': 'active', 'next': '/app/dashboard'}, secure=True).status_code, 403)
        client.get('/api/v1/session/', secure=True)
        response = client.post('/demo/enter/', {'persona': 'active', 'next': '/app/dashboard', 'csrfmiddlewaretoken': client.cookies['csrftoken'].value}, secure=True, HTTP_REFERER='https://testserver/app/login')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/app/dashboard')
        self.assertTrue(client.get('/api/v1/session/', secure=True).json()['authenticated'])

    def test_non_demo_entry_stays_unavailable(self):
        with override_settings(DEMO_MODE=False):
            self.assertFalse(self.client.get('/api/v1/session/').json()['demo_enabled'])
            self.assertEqual(self.client.post('/demo/enter/', {'persona': 'active', 'next': '/app/dashboard'}).status_code, 404)
