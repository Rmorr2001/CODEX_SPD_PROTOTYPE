"""Read responses use real templates/JSON and preserve saved poll/choice state."""
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

from django.conf import settings
from django.shortcuts import resolve_url
from django.test import Client
from django.urls import resolve, reverse

from PARLEYPRO import views
from PARLEYPRO.models import Brother_votes, Vote_Poll
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope
from .support import PollTestCase, T, make_choice, make_poll


class ReadTests(PollTestCase):
    actor_roles = ("ACTIVE",)

    def test_current_page_shows_open_poll_and_live_counts(self):
        poll = make_poll(creator=self.a, name="Current motion")
        choice = make_choice(self.a, "Aye")
        c = make_user(username="c", roles=("ACTIVE",))
        c_choice = make_choice(c, "Aye")
        before = snapshot_scope([poll, choice, c, c.brother_profile, c_choice],
                                relations=[c.brother_profile.roles])
        background = self.background()
        response = self.client.get("/poll/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "poll_index.html")
        self.assertEqual(response.context["current_poll"].pk, poll.pk)
        self.assertEqual((response.context["aye_votes"], response.context["nay_votes"]), (2, 1))
        self.assertContains(response, "2 Aye")
        self.assertContains(response, "1 Nay")
        self.assertContains(response, "Jan 15, 2026 11:59 AM")
        assert_unchanged(before)
        self.assert_background(background)

    def test_no_open_poll_page_remains_read_only_with_residual_choices(self):
        choice = make_choice(self.a, "Aye")
        c = make_user(username="c", roles=("ACTIVE",))
        c_choice = make_choice(c, "Aye")
        before = snapshot_scope([choice, c, c.brother_profile, c_choice],
                                relations=[c.brother_profile.roles])
        background = self.background()
        response = self.client.get("/poll/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["current_poll"])
        self.assertContains(response, "No active poll at the moment")
        self.assertEqual((response.context["aye_votes"], response.context["nay_votes"]), (2, 1))
        self.assertNotContains(response, 'name="aye"')
        self.assertNotContains(response, 'name="end_vote"')
        self.assertEqual(Brother_votes.objects.count(), 3)
        assert_unchanged(before)
        self.assert_background(background)

    def test_active_actor_reads_another_creators_current_poll(self):
        poll = make_poll(creator=self.b, name="Chapter motion")
        before = snapshot_scope([poll])
        background = self.background()
        response = self.client.get("/poll/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_poll"].pk, poll.pk)
        self.assertContains(response, "Chapter motion")
        self.assertFalse(Brother_votes.objects.filter(user=self.a).exists())
        assert_unchanged(before)
        self.assert_background(background)

    def test_history_contains_closed_polls_in_descending_end_order(self):
        poll = make_poll(creator=self.a, name="Still open")
        older = make_poll(creator=self.a, name="Older closed", end=T-timedelta(seconds=2), yes=2, no=1)
        # Historical sentinel ends at T-1, so it sorts first despite creator B.
        choice = make_choice(self.a, "Aye")
        before = snapshot_scope([poll, older, choice])
        background = self.background()
        response = self.client.get("/poll/past_polls/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "past_polls.html")
        self.assertEqual([p.pk for p in response.context["past_polls"]], [self.h.pk, older.pk])
        self.assertContains(response, "Older closed")
        self.assertContains(response, "Historical sentinel")
        self.assertContains(response, "Created by: a")
        self.assertContains(response, "Created by: b")
        self.assertContains(response, "4 Aye")
        self.assertContains(response, "2 Nay")
        self.assertNotContains(response, "Still open")
        assert_unchanged(before)
        self.assert_background(background)

    def test_empty_history_renders_no_polls_message(self):
        self.h.delete()
        poll = make_poll(creator=self.a, name="Open sentinel")
        before = snapshot_scope([self.a, self.b, poll, self.b_choice])
        response = self.client.get("/poll/past_polls/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["past_polls"]), [])
        self.assertContains(response, "No past polls available")
        self.assertNotContains(response, "Open sentinel")
        self.assertEqual(Vote_Poll.objects.count(), 1)
        assert_unchanged(before)

    def test_history_formats_chicago_dst_without_changing_sort_order(self):
        self.h.delete()
        first_end = datetime(2026, 11, 1, 6, 30, tzinfo=timezone.utc)
        second_end = first_end + timedelta(hours=1)
        first = make_poll(creator=self.a, name="First repeated hour",
                          start=first_end-timedelta(hours=2), end=first_end)
        second = make_poll(creator=self.a, name="Second repeated hour",
                           start=first_end-timedelta(hours=1), end=second_end)
        before = snapshot_scope([self.a, self.b, first, second, self.b_choice])
        response = self.client.get("/poll/past_polls/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([p.pk for p in response.context["past_polls"]], [second.pk, first.pk])
        self.assertContains(response, "Ended: Nov 01, 2026 1:30 AM", count=2)
        assert_unchanged(before)

    def test_active_live_results_have_exact_integer_json_payload(self):
        self.b_choice.user_vote_choice = "Aye"
        self.b_choice.save()
        poll = make_poll(creator=self.a)
        a_choice = make_choice(self.a, "Aye")
        c = make_user(username="c", roles=("ACTIVE",))
        c_choice = make_choice(c, "Nay")
        before = snapshot_scope([poll, a_choice, c, c_choice])
        background = self.background()
        response = self.client.get("/poll/poll-results/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json(), {"aye_votes": 2, "nay_votes": 1})
        self.assertTrue(all(type(value) is int for value in response.json().values()))
        assert_unchanged(before)
        self.assert_background(background)

    def test_anonymous_live_results_redirect_without_counts(self):
        poll = make_poll(creator=self.b)
        before = snapshot_scope([poll])
        background = self.background()
        response = Client().get("/poll/poll-results/")
        self.assertEqual(response.status_code, 302)
        url = urlsplit(response["Location"])
        self.assertEqual(url.path, resolve_url(settings.LOGIN_URL))
        self.assertEqual(parse_qs(url.query), {"next": ["/poll/poll-results/"]})
        self.assertNotContains(response, "aye_votes", status_code=302)
        assert_unchanged(before)
        self.assert_background(background)

    def test_live_zero_counts_are_integer_zeros(self):
        self.b_choice.delete()
        poll = make_poll(creator=self.a)
        before = snapshot_scope([self.a, self.b, self.h, poll])
        for with_choice in (False, True):
            with self.subTest(with_choice=with_choice):
                choice = make_choice(self.a, "No Vote") if with_choice else None
                response = self.client.get("/poll/poll-results/")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "application/json")
                self.assertEqual(response.json(), {"aye_votes": 0, "nay_votes": 0})
                self.assertTrue(all(type(value) is int for value in response.json().values()))
                if choice:
                    self.assert_choice(self.a, "No Vote", choice.pk)
                    choice.delete()
                assert_unchanged(before)

    def test_poll_routes_reverse_and_resolve_to_mounted_views(self):
        before = self.background()
        for name, path, view in (
            ("poll", "/poll/", views.poll_index),
            ("start_vote", "/poll/start_vote/", views.start_vote),
            ("past_polls", "/poll/past_polls/", views.past_polls),
            ("poll_results", "/poll/poll-results/", views.poll_results),
        ):
            with self.subTest(name=name):
                self.assertEqual(reverse(name), path)
                match = resolve(path)
                self.assertIs(match.func, view)
                self.assertEqual(match.url_name, name)
        self.assert_background(before)
