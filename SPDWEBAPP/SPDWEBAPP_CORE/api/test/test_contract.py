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

    def test_schema_describes_current_read_contracts_and_authentication(self):
        response = self.client.get('/api/v1/schema/')
        self.assertEqual(response.status_code, 200)
        document = response.json()
        self.assertEqual(document['info']['version'], '1.0.0')
        public_paths = {'/api/v1/status/', '/api/v1/public/home/',
                        '/api/v1/public/about/', '/api/v1/public/recruitment/'}
        private_paths = {'/api/v1/dashboard/', '/api/v1/members/', '/api/v1/profile/',
                         '/api/v1/polls/', '/api/v1/service/', '/api/v1/new-members/'}
        self.assertEqual(set(document['paths']), public_paths | private_paths | {'/api/v1/session/'})
        for path, methods in document['paths'].items():
            with self.subTest(path=path):
                self.assertEqual(set(methods), {'get'})
                self.assertIn('200', methods['get']['responses'])
                if path in public_paths:
                    self.assertFalse(methods['get'].get('security'))
                elif path in private_paths:
                    self.assertEqual(methods['get']['security'], [{'cookieAuth': []}])
        self.assertIn({}, document['paths']['/api/v1/session/']['get']['security'])
        schemas = document['components']['schemas']
        self.assertEqual(schemas['LivenessStatusEnum']['enum'], ['ok'])
        self.assertEqual(schemas['ApprovalStatusEnum']['enum'], ['approved', 'requested', 'denied'])
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
