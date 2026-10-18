from django.urls import reverse

from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import csrf_client, login_actor

from .support import T0, Event, PhilanthropyCase, edit, make_event, payload


class EditReadTests(PhilanthropyCase):
    def setUp(self):
        super().setUp()
        self.c = make_user(username='chair', roles=('ACTIVE', 'PHIL_CHAIR'))
        self.d = make_user(username='old-editor')
        self.b = make_user(username='b', roles=('ACTIVE',))
        self.e = make_event(self.c, last_edited_by=self.d, last_edited_at=T0)
        self.f = make_event(self.b, title='Control', status='approved')
        login_actor(self.client, self.c)

    def test_edit_get_populates_form_without_audit_write(self):
        client = csrf_client()
        login_actor(client, self.c)
        before = self.capture(self.c, self.d, self.b, self.e, self.f)
        response = client.get(edit(self.e))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'philanthropy_request.html')
        self.assertIs(response.context['editing'], True)
        self.assertEqual(response.context['event'], self.e)
        for value in ('value="Park"', 'value="2"', 'value="2026-07-01"'):
            self.assertContains(response, value)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertIn('csrftoken', client.cookies)
        self.unchanged(before)
        self.assertEqual(Event.objects.count(), 2)

    def test_unknown_numeric_edit_target_is_404(self):
        before = self.capture(self.c, self.d, self.b, self.e, self.f)
        path = reverse('philanthropy_edit_event', args=[999999])
        for method in ('get', 'post'):
            response = getattr(self.client, method)(path, payload(hours='3'))
            self.assertEqual(response.status_code, 404)
            self.unchanged(before)
            self.assertEqual(Event.objects.count(), 2)

    def test_noninteger_edit_paths_do_not_resolve(self):
        before = self.capture(self.c, self.d, self.b, self.e, self.f)
        for segment in ('-1', 'not-an-id'):
            for method in ('get', 'post'):
                with self.subTest(segment=segment, method=method):
                    response = getattr(self.client, method)(
                        f'/philanthropy/edit/{segment}/', payload(hours='3'))
                    self.assertEqual(response.status_code, 404)
                    self.unchanged(before)
                    self.assertEqual(Event.objects.count(), 2)
