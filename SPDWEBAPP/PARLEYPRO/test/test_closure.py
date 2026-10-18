"""Authorized single-poll closure only; known unauthorized-close defect stays blocked."""
from datetime import timedelta

from PARLEYPRO.models import Brother_votes, Vote_Poll
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import at_time
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope
from .support import PollTestCase, T, make_choice, make_poll


class ClosureTests(PollTestCase):
    def close(self, when=T):
        with at_time(when):
            response = self.client.post("/poll/", {"end_vote": "1"})
        self.assertEqual(response.status_code, 200)
        return response

    def assert_closed(self, poll, counts, *, when=T, original_start=None):
        poll.refresh_from_db()
        self.assertEqual((poll.Vote_Poll_Count_Yes, poll.Vote_Poll_Count_No), counts)
        self.assertEqual(poll.Vote_Poll_End, when)
        self.assertEqual(poll.created_by_id, self.a.pk)
        self.assertEqual(poll.Vote_Poll_Name, "Motion")
        if original_start is not None:
            self.assertEqual(poll.Vote_Poll_Start, original_start)

    def test_close_saves_exact_totals_and_end_without_rewriting_metadata(self):
        poll = make_poll(creator=self.a)
        a_choice = make_choice(self.a, "Aye")
        c = make_user(username="c", roles=("ACTIVE",))
        c_choice = make_choice(c, "Aye")
        unchanged = snapshot_scope([self.a, self.b, c, self.h])
        self.close()
        self.assert_closed(poll, (2, 1), original_start=T-timedelta(seconds=10))
        response = self.client.get("/poll/past_polls/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["past_polls"][0].pk, poll.pk)
        self.assertContains(response, "2 Aye")
        self.assertContains(response, "1 Nay")
        self.assert_choice(self.a, "No Vote", a_choice.pk)
        self.assert_choice(self.b, "No Vote", self.b_choice.pk)
        self.assert_choice(c, "No Vote", c_choice.pk)
        self.assertEqual(Brother_votes.objects.count(), 3)
        assert_unchanged(unchanged)

    def test_close_resets_current_rows_without_deleting_identity(self):
        poll = make_poll(creator=self.a)
        a_choice = make_choice(self.a, "Aye")
        c = make_user(username="c", roles=("ACTIVE",))
        c_choice = make_choice(c, "No Vote")
        unchanged = snapshot_scope([self.a, self.b, c, self.h])
        rows = {u.pk: choice.pk for u, choice in
                ((self.a, a_choice), (self.b, self.b_choice), (c, c_choice))}
        self.close()
        self.assert_closed(poll, (1, 1), original_start=T-timedelta(seconds=10))
        for user in (self.a, self.b, c):
            self.assert_choice(user, "No Vote", rows[user.pk])
        self.assertEqual(set(Brother_votes.objects.values_list("pk", flat=True)), set(rows.values()))
        response = self.client.get("/poll/poll-results/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"aye_votes": 0, "nay_votes": 0})
        assert_unchanged(unchanged)

    def test_close_without_open_poll_is_noop(self):
        choice = make_choice(self.a, "Aye")
        before = self.background()
        choice_before = snapshot_scope([choice])
        response = self.close()
        self.assertContains(response, "No active poll at the moment")
        self.assertEqual(Vote_Poll.objects.count(), 1)
        self.assertEqual(Brother_votes.objects.count(), 2)
        assert_unchanged(choice_before)
        self.assert_background(before)

    def test_repeat_close_does_not_rewrite_single_closed_poll(self):
        self.b_choice.delete()
        poll = make_poll(creator=self.a)
        choice = make_choice(self.a, "Aye")
        self.close()
        self.assert_closed(poll, (1, 0))
        self.assert_choice(self.a, "No Vote", choice.pk)
        before = snapshot_scope([self.a, self.b, self.h, poll, choice])
        response = self.close(T+timedelta(seconds=1))
        self.assertContains(response, "No active poll at the moment")
        self.assertEqual(Brother_votes.objects.count(), 1)
        self.assertEqual(Vote_Poll.objects.count(), 2)
        assert_unchanged(before)

    def test_close_tie_stores_equal_counts(self):
        poll = make_poll(creator=self.a)
        choice = make_choice(self.a, "Aye")
        unchanged = snapshot_scope([self.a, self.b, self.h])
        self.close()
        self.assert_closed(poll, (1, 1))
        response = self.client.get("/poll/past_polls/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 Aye")
        self.assertContains(response, "1 Nay")
        self.assert_choice(self.a, "No Vote", choice.pk)
        self.assert_choice(self.b, "No Vote", self.b_choice.pk)
        self.assertEqual(Brother_votes.objects.count(), 2)
        assert_unchanged(unchanged)

    def test_close_zero_votes_stores_zero_and_renders_no_votes(self):
        self.b_choice.delete()
        unchanged = snapshot_scope([self.a, self.b, self.h])
        for has_no_vote in (False, True):
            with self.subTest(has_no_vote=has_no_vote):
                poll = make_poll(creator=self.a)
                choice = make_choice(self.a, "No Vote") if has_no_vote else None
                self.close()
                self.assert_closed(poll, (0, 0))
                response = self.client.get("/poll/past_polls/")
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "No votes recorded")
                self.assertEqual(Brother_votes.objects.count(), int(has_no_vote))
                if choice:
                    self.assert_choice(self.a, "No Vote", choice.pk)
                    choice.delete()
                assert_unchanged(unchanged)
                poll.delete()
