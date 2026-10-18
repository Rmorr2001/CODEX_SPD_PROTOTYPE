"""Current-choice ownership, change/repeat semantics, and scoped literal counts."""
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from PARLEYPRO.models import Brother_votes, Vote_Poll
from PARLEYPRO.pp_functions import count_all_current_votes
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope
from .support import PollTestCase, make_choice, make_poll


class VoteTests(PollTestCase):
    actor_roles = ("ACTIVE",)

    def setUp(self):
        super().setUp()
        self.poll = make_poll(creator=self.a)

    def cast_new(self, key, value):
        before = self.background()
        poll_before = snapshot_scope([self.poll])
        for supplied in ("1", "", "false"):
            with self.subTest(value=supplied):
                response = self.client.post("/poll/", {key: supplied})
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "poll_index.html")
                self.assert_choice(self.a, value)
                self.assertEqual(Brother_votes.objects.count(), 2)
                self.assertEqual(Vote_Poll.objects.count(), 2)
                assert_unchanged(poll_before)
                self.assert_background(before)
                Brother_votes.objects.filter(user=self.a).delete()

    def test_cast_aye_creates_own_current_choice(self):
        self.cast_new("aye", "Aye")

    def test_cast_nay_creates_own_current_choice(self):
        self.cast_new("nay", "Nay")

    def test_change_choice_keeps_user_row_identity(self):
        before = self.background()
        poll_before = snapshot_scope([self.poll])
        for previous, key, expected in (("Aye", "nay", "Nay"), ("Nay", "aye", "Aye")):
            with self.subTest(previous=previous):
                choice = make_choice(self.a, previous)
                response = self.client.post("/poll/", {key: "1"})
                self.assertEqual(response.status_code, 200)
                self.assert_choice(self.a, expected, choice.pk)
                self.assertEqual(Brother_votes.objects.count(), 2)
                assert_unchanged(poll_before)
                self.assert_background(before)
                choice.delete()

    def test_repeat_identical_choice_is_idempotent_for_current_row(self):
        for value, key in (("Aye", "aye"), ("Nay", "nay")):
            with self.subTest(value=value):
                choice = make_choice(self.a, value)
                before = snapshot_scope([choice, self.poll])
                background = self.background()
                for _ in range(2):
                    response = self.client.post("/poll/", {key: "1"})
                    self.assertEqual(response.status_code, 200)
                    self.assert_choice(self.a, value, choice.pk)
                    self.assertEqual(Brother_votes.objects.count(), 2)
                    assert_unchanged(before)
                    self.assert_background(background)
                choice.delete()

    def forged_target(self, existing):
        # B deliberately starts Aye so an ownership leak is observable after a Nay cast.
        self.b_choice.user_vote_choice = "Aye"
        self.b_choice.save()
        choice = make_choice(self.a, "Aye") if existing else None
        before = self.background()
        poll_before = snapshot_scope([self.poll])
        response = self.client.post("/poll/", {
            "nay": "1", "user": self.b.pk, "user_id": self.b.pk,
            "poll": self.h.pk, "user_vote_choice": "Aye",
        })
        self.assertEqual(response.status_code, 200)
        self.assert_choice(self.a, "Nay", choice.pk if choice else None)
        self.assertEqual(Brother_votes.objects.count(), 2)
        assert_unchanged(poll_before)
        self.assert_background(before)

    def test_forged_target_fields_cannot_create_another_users_choice(self):
        self.forged_target(existing=False)

    def test_forged_target_fields_cannot_redirect_existing_choice(self):
        self.forged_target(existing=True)

    def test_count_helper_excludes_nonchoice_literals(self):
        self.b_choice.delete()
        choices = []
        users = []
        for index, value in enumerate(("Aye", "Nay", "No Vote", None, "invalid")):
            user = make_user(username=f"counter-{index}", roles=("ACTIVE",))
            users.append(user)
            # Deliberate raw ORM corruption for NULL/invalid strings; no fixture validation claim.
            choices.append(make_choice(user, value))
        before = snapshot_scope([self.poll, self.h, *users, *choices])
        self.assertEqual(count_all_current_votes(Brother_votes.objects), (1, 1))
        self.assertEqual(Brother_votes.objects.count(), 5)
        assert_unchanged(before)

    def test_count_helper_respects_supplied_queryset(self):
        self.b_choice.user_vote_choice = "Aye"
        self.b_choice.save()
        a_choice = make_choice(self.a, "Aye")
        c = make_user(username="c", roles=("ACTIVE",))
        c_choice = make_choice(c, "Nay")
        queryset = Brother_votes.objects.filter(user__in=(self.a, c))
        before = snapshot_scope([self.a, self.b, c, a_choice, self.b_choice, c_choice, self.poll])
        self.assertEqual(count_all_current_votes(queryset), (1, 1))
        self.assertEqual(count_all_current_votes(Brother_votes.objects), (2, 1))
        self.assertEqual(set(queryset.values_list("pk", flat=True)), {a_choice.pk, c_choice.pk})
        assert_unchanged(before)

    def test_current_choice_is_unique_per_nonnull_user(self):
        choice = make_choice(self.a, "Aye")
        before = snapshot_scope([choice, self.b_choice, self.a, self.b, self.poll, self.h])
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                make_choice(self.a, "Nay")
        self.assert_choice(self.a, "Aye", choice.pk)
        self.assertEqual(Brother_votes.objects.count(), 2)
        assert_unchanged(before)

    def test_model_choice_validation_accepts_only_declared_nonnull_values(self):
        before = self.background()
        for value in ("Aye", "Nay", "No Vote"):
            with self.subTest(value=value):
                Brother_votes(user=self.a, user_vote_choice=value).full_clean()
        for value in ("aye", "Bad"):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError) as caught:
                    Brother_votes(user=self.a, user_vote_choice=value).full_clean()
                errors = caught.exception.error_dict["user_vote_choice"]
                self.assertEqual(errors[0].code, "invalid_choice")
        self.assertFalse(Brother_votes.objects.filter(user=self.a).exists())
        self.assertEqual(Brother_votes.objects.count(), 1)
        self.assert_background(before)
