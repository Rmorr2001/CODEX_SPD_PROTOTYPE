"""Verify namespace isolation, fixed file selection and actual WhiteNoise caching."""
from pathlib import Path
from tempfile import TemporaryDirectory
from django.conf import settings
from django.test import Client, SimpleTestCase, override_settings


class ShellTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.directory = self.enterContext(TemporaryDirectory(prefix='spd-shell-'))
        self.root = Path(self.directory)
        self.html = b'<!doctype html><title>Bundle fixture</title><div id="root"></div>'
        (self.root / 'index.html').write_bytes(self.html)
        self.enterContext(override_settings(FRONTEND_DIST_DIR=self.root))

    def test_root_and_nested_routes_serve_the_same_built_shell(self):
        for path in ('/app/', '/app/connection', '/app/unknown/deep/link'):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(b''.join(response.streaming_content), self.html)
                self.assertIn('text/html', response['Content-Type'])
                self.assertIn('no-cache', response['Cache-Control'])

    def test_path_text_never_selects_a_filesystem_file(self):
        (self.root / 'other.txt').write_text('must not be served')
        for path in ('/app/other.txt', '/app/%2e%2e/secret_config.py'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b''.join(response.streaming_content), self.html)

    def test_missing_bundle_is_a_controlled_unavailable_response(self):
        (self.root / 'index.html').unlink()
        response = self.client.get('/app/connection')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.content, b'Application temporarily unavailable.')
        self.assertNotIn(self.directory.encode(), response.content)

    def test_api_and_unrelated_routes_never_receive_the_shell(self):
        response = self.client.get('/api/v1/missing/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'application/json')
        response = self.client.get('/unrelated-missing-page/')
        self.assertEqual(response.status_code, 404)
        self.assertNotIn(b'Bundle fixture', response.content)

    def test_post_cannot_use_the_spa_as_a_write_endpoint(self):
        self.assertEqual(self.client.post('/app/connection').status_code, 405)


class AssetCacheTests(SimpleTestCase):
    def test_only_hashed_assets_are_immutable(self):
        with TemporaryDirectory(prefix='spd-static-') as directory:
            assets = Path(directory) / 'app/assets'
            assets.mkdir(parents=True)
            for name in ('index-AbCdEf12.js', 'index.js'):
                (assets / name).write_text('/* synthetic asset */')
            middleware = [settings.MIDDLEWARE[0], 'whitenoise.middleware.WhiteNoiseMiddleware',
                          *settings.MIDDLEWARE[1:]]
            with override_settings(STATIC_ROOT=directory, MIDDLEWARE=middleware,
                                   WHITENOISE_AUTOREFRESH=False, WHITENOISE_USE_FINDERS=False):
                client = Client()
                hashed = client.get('/static/app/assets/index-AbCdEf12.js')
                self.assertEqual(hashed.status_code, 200)
                self.assertIn('immutable', hashed['Cache-Control'])
                self.assertIn(b'synthetic asset', b''.join(hashed.streaming_content))
                unhashed = client.get('/static/app/assets/index.js')
                self.assertEqual(unhashed.status_code, 200)
                self.assertNotIn('immutable', unhashed['Cache-Control'])
                unhashed.close()
                self.assertEqual(client.get('/static/app/assets/missing.js').status_code, 404)
