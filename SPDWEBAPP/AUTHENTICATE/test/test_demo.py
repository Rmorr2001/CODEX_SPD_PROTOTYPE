"""Actual demo persona view/middleware, using synthetic groups and secure clients."""
from copy import deepcopy
from datetime import datetime, timezone

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.test import RequestFactory, override_settings
from django.urls import reverse

from railway_demo.middleware import DemoBoundaryMiddleware
from SPDWEBAPP_CORE.testing import settings as business_settings
from SPDWEBAPP_CORE.testing.factories import make_user, TEST_PASSWORD
from SPDWEBAPP_CORE.testing.helpers import csrf_client, at_time
from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from .support import IdentityCase, real_token, member_state

CLOCK = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
DEMO_MIDDLEWARE = [*business_settings.MIDDLEWARE, "railway_demo.middleware.DemoBoundaryMiddleware"]
DEMO_TEMPLATES = deepcopy(business_settings.TEMPLATES)
DEMO_TEMPLATES[0]["OPTIONS"]["context_processors"].append("railway_demo.context.demo_state")


@override_settings(ROOT_URLCONF="railway_demo.urls", MIDDLEWARE=DEMO_MIDDLEWARE, TEMPLATES=DEMO_TEMPLATES,
                   DEMO_MODE=True, SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True)
class DemoTests(IdentityCase):
    def setUp(self):
        super().setUp()
        self.enterContext(at_time(CLOCK))

    def persona(self, name="active", **kwargs):
        roles = {"executive": ("EXEC", "ACTIVE"), "active": ("ACTIVE",),
                 "newmember": ("NEW_MEMBER",), "alumni": ("ALUMNI",)}[name]
        fields = {"password": None, "roles": roles, **kwargs}
        user = make_user(username=f"demo-{name}", **fields)
        user.groups.add(Group.objects.get_or_create(name=f"railway-demo:demo-{name}")[0])
        return user

    def secure_client(self, user=None):
        client = csrf_client()
        client.defaults["HTTP_REFERER"] = "https://testserver/auth/login/"
        if user:
            self.login(user, client)
        token = real_token(client, "/auth/login/", secure=True)
        return client, token

    def enter(self, client, token, data=None):
        with at_time(CLOCK):
            return client.post("/demo/enter/", {"csrfmiddlewaretoken": token, **(data or {})}, secure=True)

    def demo_snapshot(self, *extra):
        users = [self.a, self.b, *extra]
        rows = users + [u.brother_profile for u in users]
        relations = {f"{u.pk}-groups": u.groups for u in users}
        relations.update({f"{u.pk}-roles": u.brother_profile.roles for u in users})
        relations.update({f"{u.pk}-majors": u.brother_profile.majors for u in users})
        return snapshot_scope(rows, relations=relations)

    def assert_entered(self, client, response, user, destination):
        self.assertRedirects(response, "/app/new-members" if user.brother_profile.roles.filter(name="NEW_MEMBER").exists() else "/app/dashboard", fetch_redirect_response=False)
        self.assert_identity(client, user)
        user.refresh_from_db()
        self.assertEqual(user.last_login, CLOCK)
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_demo_persona_entry_identity(self):
        users = {name: self.persona(name) for name in ("executive", "active", "newmember", "alumni")}
        for name, user in users.items():
            with self.subTest(persona=name):
                client, token = self.secure_client()
                before = self.demo_snapshot(*users.values())
                response = self.enter(client, token, {"persona": name})
                self.assert_entered(client, response, user, "alumni_roster" if name == "alumni" else "dashboard")
                assert_unchanged(before, except_fields={user: {"last_login"}})

    def test_demo_default_persona(self):
        user = self.persona("executive")
        client, token = self.secure_client()
        before = self.demo_snapshot(user)
        count = (User.objects.count(), Group.objects.count())
        self.assert_entered(client, self.enter(client, token), user, "dashboard")
        self.assertEqual((User.objects.count(), Group.objects.count()), count)
        assert_unchanged(before, except_fields={user: {"last_login"}})

    def test_demo_entry_after_username_change(self):
        user = self.persona()
        User.objects.filter(pk=user.pk).update(username="renamed-active")
        user.refresh_from_db()
        client, token = self.secure_client()
        before, count = self.demo_snapshot(user), User.objects.count()
        self.assert_entered(client, self.enter(client, token, {"persona": "active"}), user, "dashboard")
        self.assertEqual(User.objects.count(), count)
        assert_unchanged(before, except_fields={user: {"last_login"}})

    def test_demo_newmember_dashboard_redirect(self):
        user = self.persona("newmember")
        client, token = self.secure_client()
        self.enter(client, token, {"persona": "newmember"})
        before = self.demo_snapshot(user)
        response = client.get("/auth/dashboard/", secure=True)
        self.assertRedirects(response, "/newmember/", fetch_redirect_response=False)
        self.assert_identity(client, user)
        assert_unchanged(before)

    def test_demo_entry_post_only(self):
        for enabled in (True, False):
            for actor in (None, self.a):
                with self.subTest(enabled=enabled, authenticated=actor is not None):
                    client, _ = self.secure_client(actor)
                    before = self.demo_snapshot()
                    with override_settings(DEMO_MODE=enabled):
                        response = client.get("/demo/enter/", secure=True)
                    self.assertEqual(response.status_code, 405)
                    self.assertEqual(response["Allow"], "POST")
                    self.assert_identity(client, actor)
                    assert_unchanged(before)

    def test_demo_unknown_persona(self):
        user = self.persona("executive")
        for actor in (None, self.a):
            for name in ("unknown", ""):
                with self.subTest(actor=actor, name=name):
                    client, token = self.secure_client(actor)
                    before = self.demo_snapshot(user)
                    response = self.enter(client, token, {"persona": name})
                    self.assertEqual(response.status_code, 400)
                    self.assertEqual(response.content, b"Unknown demo persona.")
                    self.assert_identity(client, actor)
                    assert_unchanged(before)

    def test_demo_entry_disabled(self):
        user = self.persona()
        client, token = self.secure_client(self.a)
        before = self.demo_snapshot(user)
        with override_settings(DEMO_MODE=False):
            response = self.enter(client, token, {"persona": "active"})
        self.assertEqual(response.status_code, 404)
        self.assert_identity(client, self.a)
        assert_unchanged(before)

    def test_demo_ineligible_account_rejected(self):
        user = self.persona()
        variants = ["absent", "inactive", "staff", "superuser", "usable-password"]
        for variant in variants:
            with self.subTest(variant=variant):
                user.groups.clear()
                User.objects.filter(pk=user.pk).update(is_active=True, is_staff=False, is_superuser=False)
                user.refresh_from_db()
                user.set_unusable_password()
                user.save()
                if variant != "absent":
                    user.groups.add(Group.objects.get(name="railway-demo:demo-active"))
                if variant == "inactive":
                    user.is_active = False
                elif variant == "staff":
                    user.is_staff = True
                elif variant == "superuser":
                    user.is_superuser = True
                elif variant == "usable-password":
                    user.set_password(TEST_PASSWORD)
                user.save()
                client, token = self.secure_client(self.a)
                before = self.demo_snapshot(user)
                response = self.enter(client, token, {"persona": "active"})
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.content, b"The demo account is not ready.")
                self.assert_identity(client, self.a)
                assert_unchanged(before)

    def test_demo_csrf_rejects_absent_and_bad_tokens(self):
        user = self.persona()
        for actor in (None, self.a):
            for bad in (None, "invalid"):
                with self.subTest(actor=actor, bad=bad):
                    client, _ = self.secure_client(actor)
                    before = self.demo_snapshot(user)
                    payload = {"persona": "active"}
                    if bad:
                        payload["csrfmiddlewaretoken"] = bad
                    response = client.post("/demo/enter/", payload, secure=True)
                    self.assertEqual(response.status_code, 403)
                    self.assert_identity(client, actor)
                    assert_unchanged(before)

    def test_demo_csrf_accepts_token_and_rotates_identity(self):
        user = self.persona()
        client, token = self.secure_client(self.a)
        previous_key = client.session.session_key
        before = self.demo_snapshot(user)
        self.assert_entered(client, self.enter(client, token, {"persona": "active"}), user, "dashboard")
        self.assertNotEqual(client.session.session_key, previous_key)
        assert_unchanged(before, except_fields={user: {"last_login"}})

    def test_demo_admin_http_boundary(self):
        staff = make_user(username="staff", is_staff=True)
        superuser = make_user(username="superuser", is_staff=True, is_superuser=True)
        for actor in (None, self.a, staff, superuser):
            client, token = self.secure_client(actor)
            before = self.demo_snapshot(staff, superuser)
            for path in ("/admin/", "/admin/auth/user/"):
                for method in ("get", "post"):
                    with self.subTest(actor=actor, path=path, method=method):
                        data = {} if method == "get" else {"csrfmiddlewaretoken": token}
                        response = getattr(client, method)(path, data, secure=True)
                        self.assertEqual(response.status_code, 403)
                        self.assertEqual(response.json(), {"error": "Admin is unavailable on the public demo."})
                        self.assertNotIn("Location", response)
                        self.assertEqual(response.templates, [])
                        self.assert_identity(client, actor)
            self.assertFalse(LogEntry.objects.exists())
            assert_unchanged(before)

    def test_demo_admin_middleware_short_circuit(self):
        calls = []
        def downstream(request):
            calls.append(request.path)
            return HttpResponse("unreachable")
        middleware = DemoBoundaryMiddleware(downstream)
        before = self.demo_snapshot()
        for path in ("/admin/", "/admin/auth/user/"):
            for method in ("get", "post", "put", "delete"):
                with self.subTest(path=path, method=method):
                    request = getattr(RequestFactory(), method)(path)
                    response = middleware(request)
                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(response.content, b'{"error": "Admin is unavailable on the public demo."}')
        self.assertEqual(calls, [])
        assert_unchanged(before)
