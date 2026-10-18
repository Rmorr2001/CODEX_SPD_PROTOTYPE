"""Route-specific ALL-role enforcement and real CSRF middleware integration."""
from urllib.parse import parse_qs, urlsplit

from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.messages import get_messages
from django.shortcuts import resolve_url
from django.test import Client
from django.urls import reverse

from PARLEYPRO.models import Brother_votes, Vote_Poll
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import at_time, csrf_client, login_actor
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope
from .support import PollTestCase, T, csrf_token, make_choice, make_poll


class AccessTests(PollTestCase):
    def denied_actors(self, *, include_active=False):
        yield None
        yield make_user(username="no-profile", with_profile=False)
        roles = [(), ("EXEC",), ("ALUMNI",), ("NEW_MEMBER",), ("PHIL_CHAIR",),
                 ("EXEC", "ALUMNI")]
        if include_active:
            roles.append(("ACTIVE",))
        for index, assigned in enumerate(roles):
            yield make_user(username=f"denied-{index}", roles=assigned)

    def assert_login_redirect(self, response, next_path):
        self.assertEqual(response.status_code, 302)
        location = urlsplit(response["Location"])
        self.assertEqual(location.path, resolve_url(settings.LOGIN_URL))
        self.assertEqual(parse_qs(location.query), {"next": [next_path]})

    def assert_denied(self, response, actor, *, next_path, login_first=False):
        self.assertEqual(response.status_code, 302)
        if actor is None and login_first:
            self.assert_login_redirect(response, next_path)
        else:
            self.assertEqual(response["Location"], reverse("login") if actor is None
                             else "/auth/login/")
            messages = " ".join(str(m) for m in get_messages(response.wsgi_request))
            self.assertTrue(messages)
            if actor is not None:
                expected = "profile not found" if actor.username == "no-profile" else "missing"
                self.assertIn(expected.lower(), messages.lower())

    def test_anonymous_create_requires_login(self):
        before = self.background()
        client = Client()
        for method in ("get", "post"):
            response = getattr(client, method)(
                "/poll/start_vote/", {} if method == "get" else {"Vote_Poll_Name": "Motion"})
            self.assert_login_redirect(response, "/poll/start_vote/")
            self.assertNotIn(SESSION_KEY, client.session)
            self.assertEqual(Vote_Poll.objects.count(), 1)
            self.assertEqual(Brother_votes.objects.count(), 1)
        self.assert_background(before)

    def test_create_denies_missing_profile_or_required_role(self):
        before = self.background()
        for actor in self.denied_actors(include_active=True):
            if actor is None:
                continue  # Anonymous transport is independently asserted above.
            with self.subTest(actor=actor.username):
                client = Client()
                login_actor(client, actor)
                actor_before = snapshot_scope([actor])
                for method in ("get", "post"):
                    response = getattr(client, method)(
                        "/poll/start_vote/", {"Vote_Poll_Name": "Motion"},
                        HTTP_REFERER="/auth/login/",
                    )
                    self.assert_denied(response, actor, next_path="/poll/start_vote/")
                    self.assertEqual(client.session[SESSION_KEY], str(actor.pk))
                    self.assertEqual(Vote_Poll.objects.count(), 1)
                    self.assertEqual(Brother_votes.objects.count(), 1)
                    assert_unchanged(actor_before)
                    self.assert_background(before)

    def test_create_allows_exact_pair_and_extra_roles(self):
        before = self.background()
        for index, roles in enumerate((("EXEC", "ACTIVE"), ("EXEC", "ACTIVE", "ALUMNI"))):
            with self.subTest(roles=roles):
                actor = make_user(username=f"allowed-{index}", roles=roles)
                client = Client()
                login_actor(client, actor)
                response = client.get("/poll/start_vote/")
                self.assertEqual(response.status_code, 200)
                self.assertFalse(response.context["form"].is_bound)
                response = client.post("/poll/start_vote/", {"Vote_Poll_Name": "Role motion"})
                self.assertRedirects(response, reverse("poll"), fetch_redirect_response=False)
                poll = Vote_Poll.objects.exclude(pk=self.h.pk).get()
                self.assertEqual((poll.Vote_Poll_Name, poll.created_by_id), ("Role motion", actor.pk))
                self.assertEqual((poll.Vote_Poll_Count_Yes, poll.Vote_Poll_Count_No), (0, 0))
                self.assertIsNone(poll.Vote_Poll_End)
                self.assert_background(before)
                poll.delete()

    def test_superuser_without_profile_cannot_create_public_poll(self):
        before = self.background()
        actor = make_user(username="super", with_profile=False, is_superuser=True)
        login_actor(self.client, actor)
        for method in ("get", "post"):
            response = getattr(self.client, method)(
                "/poll/start_vote/", {"Vote_Poll_Name": "Privileged motion"},
                HTTP_REFERER="/auth/login/",
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response["Location"], "/auth/login/")
            self.assertIn("User profile not found.", [str(m) for m in get_messages(response.wsgi_request)])
            self.assertEqual(Vote_Poll.objects.count(), 1)
            self.assertEqual(Brother_votes.objects.count(), 1)
        self.assert_background(before)

    def reject_csrf(self, path, payload, *, has_open_poll):
        poll = make_poll(creator=self.a) if has_open_poll else None
        poll_before = snapshot_scope([poll]) if poll else None
        client = csrf_client()
        login_actor(client, self.a)
        token = csrf_token(client.get(path))
        before = self.background()
        self.assertTrue(token)
        for supplied in (None, "Z" * 64):
            with self.subTest(token="absent" if supplied is None else "bad"):
                data = dict(payload)
                if supplied:
                    data["csrfmiddlewaretoken"] = supplied
                response = client.post(path, data)
                self.assertEqual(response.status_code, 403)
                self.assertEqual(Vote_Poll.objects.count(), 2 if poll else 1)
                self.assertEqual(Brother_votes.objects.count(), 1)
                self.assert_background(before)
                if poll_before:
                    assert_unchanged(poll_before)

    def test_create_rejects_missing_or_bad_csrf(self):
        self.reject_csrf("/poll/start_vote/", {"Vote_Poll_Name": "CSRF motion"}, has_open_poll=False)

    def test_cast_rejects_missing_or_bad_csrf(self):
        self.reject_csrf("/poll/", {"aye": "1"}, has_open_poll=True)

    def test_close_rejects_missing_or_bad_csrf(self):
        self.reject_csrf("/poll/", {"end_vote": "1"}, has_open_poll=True)

    def test_token_authenticated_create_succeeds(self):
        client = csrf_client()
        login_actor(client, self.a)
        token = csrf_token(client.get("/poll/start_vote/"))
        before = self.background()
        response = client.post("/poll/start_vote/", {
            "Vote_Poll_Name": "Token motion", "csrfmiddlewaretoken": token,
        })
        self.assertRedirects(response, reverse("poll"), fetch_redirect_response=False)
        poll = Vote_Poll.objects.exclude(pk=self.h.pk).get()
        self.assert_open_defaults(poll, "Token motion")
        self.assertEqual(client.session[SESSION_KEY], str(self.a.pk))
        self.assertEqual(Brother_votes.objects.count(), 1)
        self.assert_background(before)

    def test_token_authenticated_cast_succeeds(self):
        before = self.background()
        actor = make_user(username="caster", roles=("ACTIVE",))
        poll = make_poll(creator=actor)
        client = csrf_client()
        login_actor(client, actor)
        poll_before = snapshot_scope([poll, actor])
        token = csrf_token(client.get("/poll/"))
        response = client.post("/poll/", {"aye": "1", "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 200)
        self.assert_choice(actor, "Aye")
        self.assertEqual(Brother_votes.objects.count(), 2)
        assert_unchanged(poll_before)
        self.assert_background(before)

    def test_token_authenticated_close_succeeds(self):
        self.b_choice.delete()  # This case has exactly one voter, not a second global choice.
        poll = make_poll(creator=self.a)
        choice = make_choice(self.a, "Aye")
        client = csrf_client()
        login_actor(client, self.a)
        token = csrf_token(client.get("/poll/"))
        before = snapshot_scope([self.a, self.b, self.h])
        with at_time(T):
            response = client.post("/poll/", {"end_vote": "1", "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 200)
        poll.refresh_from_db()
        self.assertEqual((poll.Vote_Poll_Count_Yes, poll.Vote_Poll_Count_No), (1, 0))
        self.assertEqual(poll.Vote_Poll_End, T)
        self.assertEqual((poll.created_by_id, poll.Vote_Poll_Name), (self.a.pk, "Motion"))
        self.assert_choice(self.a, "No Vote", choice.pk)
        self.assertEqual(Brother_votes.objects.count(), 1)
        assert_unchanged(before)

    def deny_poll_routes(self, *, paths, post=False):
        before = self.background()
        poll = make_poll(creator=self.b)
        poll_before = snapshot_scope([poll])
        for actor in self.denied_actors():
            with self.subTest(actor=None if actor is None else actor.username):
                client = Client()
                if actor is not None:
                    login_actor(client, actor)
                for path in paths:
                    response = (client.post(path, {"end_vote" if post == "close" else "aye": "1"},
                                            HTTP_REFERER="/auth/login/") if post
                                else client.get(path, HTTP_REFERER="/auth/login/"))
                    self.assert_denied(response, actor, next_path=path)
                    self.assertEqual(Brother_votes.objects.count(), 1)
                    self.assertEqual(Vote_Poll.objects.count(), 2)
                    assert_unchanged(poll_before)
                    self.assert_background(before)

    def test_close_route_denies_actors_without_active(self):
        self.deny_poll_routes(paths=("/poll/",), post="close")

    def test_page_and_history_require_active_role(self):
        self.deny_poll_routes(paths=("/poll/", "/poll/past_polls/"))

    def test_cast_denial_preserves_choices(self):
        self.deny_poll_routes(paths=("/poll/",), post=True)

    def test_active_and_extra_roles_can_read_and_cast(self):
        before = self.background()
        for index, roles in enumerate((("ACTIVE",), ("ACTIVE", "ALUMNI"))):
            with self.subTest(roles=roles):
                actor = make_user(username=f"active-{index}", roles=roles)
                poll = make_poll(creator=actor)
                client = Client()
                login_actor(client, actor)
                unchanged = snapshot_scope([actor, poll])
                response = client.get("/poll/")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["current_poll"].pk, poll.pk)
                response = client.get("/poll/past_polls/")
                self.assertEqual(response.status_code, 200)
                self.assertEqual([p.pk for p in response.context["past_polls"]], [self.h.pk])
                self.assertEqual(client.post("/poll/", {"aye": "1"}).status_code, 200)
                self.assert_choice(actor, "Aye")
                assert_unchanged(unchanged)
                self.assert_background(before)
                Brother_votes.objects.filter(user=actor).delete()
                poll.delete()

    def test_route_denial_returns_to_safe_same_origin_referer(self):
        before = self.background()
        actor = make_user(username="no-roles", roles=())
        poll = make_poll(creator=self.b)
        login_actor(self.client, actor)
        unchanged = snapshot_scope([actor, poll])
        requests = [("get", path, {}) for path in
                    ("/poll/", "/poll/past_polls/", "/poll/start_vote/")]
        requests.append(("post", "/poll/start_vote/", {"Vote_Poll_Name": "Denied"}))
        for method, path, payload in requests:
            response = getattr(self.client, method)(path, payload, HTTP_REFERER="/auth/login/")
            self.assert_denied(response, actor, next_path=path)
            self.assertEqual(self.client.session[SESSION_KEY], str(actor.pk))
            self.assertEqual(Vote_Poll.objects.count(), 2)
            self.assertEqual(Brother_votes.objects.count(), 1)
            assert_unchanged(unchanged)
            self.assert_background(before)
