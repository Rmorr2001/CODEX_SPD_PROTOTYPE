"""Exercise the JSON boundary and fail-closed defaults through real DRF dispatch."""
from django.test import SimpleTestCase, TestCase, override_settings
from SPDWEBAPP_CORE.testing.factories import make_user


class PublicApiTests(SimpleTestCase):
    def test_status_is_public_exact_and_database_independent(self):
        response = self.client.get('/api/v1/status/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json(), {'status': 'ok', 'api_version': 'v1'})
        self.assertEqual(response['Cache-Control'], 'no-store')

    def test_head_has_no_body_and_same_status(self):
        response = self.client.head('/api/v1/status/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')

    def test_status_rejects_writes_with_json(self):
        for method in ('post', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                response = getattr(self.client, method)('/api/v1/status/')
                self.assertEqual(response.status_code, 405)
                self.assertEqual(response['Content-Type'], 'application/json')
                self.assertIn('detail', response.json())

    def test_html_accept_is_not_a_browsable_api(self):
        response = self.client.get('/api/v1/status/', HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_unknown_namespace_paths_remain_json_for_all_methods(self):
        for path in ('/api/v1/missing/', '/api/v2/status/', '/api/'):
            for method in ('get', 'post', 'put', 'patch', 'delete', 'options'):
                with self.subTest(path=path, method=method):
                    response = getattr(self.client, method)(path)
                    self.assertEqual(response.status_code, 404)
                    self.assertEqual(response['Content-Type'], 'application/json')
                    self.assertEqual(response.json(), {'detail': 'Not found.'})

    def test_schema_describes_only_current_public_status(self):
        response = self.client.get('/api/v1/schema/')
        self.assertEqual(response.status_code, 200)
        document = response.json()
        self.assertEqual(document['info']['version'], '1.0.0')
        self.assertEqual(set(document['paths']), {'/api/v1/status/'})
        operation = document['paths']['/api/v1/status/']['get']
        self.assertIn('200', operation['responses'])
        self.assertFalse(operation.get('security'))


@override_settings(ROOT_URLCONF='SPDWEBAPP_CORE.api.test.urls')
class DefaultPermissionsTests(TestCase):
    def test_unconfigured_endpoint_denies_anonymous_access(self):
        response = self.client.get('/private/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('detail', response.json())

    def test_default_session_auth_accepts_real_authenticated_user(self):
        user = make_user(username='api-fixture', with_profile=False)
        self.client.force_login(user)
        response = self.client.get('/private/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'allowed': True})
