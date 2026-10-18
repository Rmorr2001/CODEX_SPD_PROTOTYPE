"""Creation form boundaries, actor binding and the consumed view/model clocks."""
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.urls import reverse
from django.utils.html import escape

from PARLEYPRO.models import Brother_votes, Vote_Poll
from SPDWEBAPP_CORE.testing.helpers import at_time
from .support import PollTestCase, T


class CreationTests(PollTestCase):
    def test_create_form_exposes_name_and_csrf(self):
        before = self.background()
        response = self.client.get("/poll/start_vote/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_poll.html")
        form = response.context["form"]
        self.assertFalse(form.is_bound)
        self.assertEqual(list(form.fields), ["Vote_Poll_Name"])
        self.assertEqual(form.fields["Vote_Poll_Name"].label, "Poll Name")
        self.assertEqual(form.fields["Vote_Poll_Name"].widget.attrs["class"], "form-control")
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertEqual(Vote_Poll.objects.count(), 1)
        self.assertEqual(Brother_votes.objects.count(), 1)
        self.assert_background(before)

    def test_invalid_name_redisplay_escapes_html(self):
        before = self.background()
        name = "<script>" * 30
        response = self.client.post("/poll/start_vote/", {"Vote_Poll_Name": name})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].is_bound)
        self.assertEqual(response.context["form"].errors.as_data()["Vote_Poll_Name"][0].code,
                         "max_length")
        self.assertContains(response, escape(name))
        self.assertNotContains(response, name)
        self.assertEqual(Vote_Poll.objects.count(), 1)
        self.assertEqual(Brother_votes.objects.count(), 1)
        self.assert_background(before)

    def test_create_saves_name_and_open_defaults(self):
        before = self.background()
        with at_time(T):
            response = self.client.post("/poll/start_vote/", {"Vote_Poll_Name": "  Motion A  "})
        self.assertRedirects(response, reverse("poll"), fetch_redirect_response=False)
        poll = Vote_Poll.objects.exclude(pk=self.h.pk).get()
        self.assert_open_defaults(poll, "Motion A")
        self.assertEqual(poll.Vote_Poll_Start, T)
        self.assertEqual(Brother_votes.objects.count(), 1)
        self.assert_background(before)

    def test_create_ignores_forged_model_fields(self):
        before = self.background()
        payload = {
            "Vote_Poll_Name": "Motion B", "created_by": self.b.pk, "id": self.h.pk,
            "Vote_Poll_Count_Yes": 99, "Vote_Poll_Count_No": 88,
            "Vote_Poll_Start": "2000-01-01", "Vote_Poll_End": "2000-01-02",
        }
        with at_time(T):
            response = self.client.post("/poll/start_vote/", payload)
        self.assertRedirects(response, reverse("poll"), fetch_redirect_response=False)
        poll = Vote_Poll.objects.exclude(pk=self.h.pk).get()
        self.assertNotEqual(poll.pk, self.h.pk)
        self.assert_open_defaults(poll, "Motion B")
        self.assertEqual(poll.Vote_Poll_Start, T)
        self.assertEqual(Brother_votes.objects.count(), 1)
        self.assert_background(before)

    def test_create_rejects_blank_name(self):
        before = self.background()
        for payload in ({}, {"Vote_Poll_Name": ""}, {"Vote_Poll_Name": "   "}):
            with self.subTest(payload=payload):
                response = self.client.post("/poll/start_vote/", payload)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["form"].errors.as_data()["Vote_Poll_Name"][0].code,
                                 "required")
                self.assertEqual(Vote_Poll.objects.count(), 1)
                self.assertEqual(Brother_votes.objects.count(), 1)
                self.assert_background(before)

    def test_create_rejects_name_over_max_length(self):
        before = self.background()
        name = "x" * 201
        response = self.client.post("/poll/start_vote/", {"Vote_Poll_Name": name})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].errors.as_data()["Vote_Poll_Name"][0].code,
                         "max_length")
        self.assertContains(response, name)
        self.assertEqual(Vote_Poll.objects.count(), 1)
        self.assertEqual(Brother_votes.objects.count(), 1)
        self.assert_background(before)

    def test_create_accepts_name_length_boundaries_and_unicode(self):
        before = self.background()
        for name in ("x", "x" * 200, "Réunion Δ"):
            with self.subTest(name=name):
                with at_time(T):
                    response = self.client.post("/poll/start_vote/", {"Vote_Poll_Name": name})
                self.assertRedirects(response, reverse("poll"), fetch_redirect_response=False)
                poll = Vote_Poll.objects.exclude(pk=self.h.pk).get()
                self.assert_open_defaults(poll, name)
                self.assertEqual(poll.Vote_Poll_Start, T)
                self.assertEqual(Brother_votes.objects.count(), 1)
                self.assert_background(before)
                poll.delete()  # Reset each equivalent input variant to no open polls.

    def test_created_markup_name_is_escaped_on_page(self):
        before = self.background()
        name = "<b>Motion</b>"
        response = self.client.post("/poll/start_vote/", {"Vote_Poll_Name": name})
        self.assertRedirects(response, reverse("poll"), fetch_redirect_response=False)
        poll = Vote_Poll.objects.exclude(pk=self.h.pk).get()
        response = self.client.get("/poll/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, escape(name))
        self.assertNotContains(response, name)
        self.assert_open_defaults(poll, name)
        self.assert_background(before)

    def test_auto_add_uses_model_clock_after_view_clock(self):
        before = self.background()
        # Isolate clock imports only: keep actual form validation and model save.
        with at_time(T + timedelta(seconds=1)):
            with patch("PARLEYPRO.views.timezone", SimpleNamespace(now=lambda: T)):
                response = self.client.post("/poll/start_vote/", {"Vote_Poll_Name": "Two clocks"})
        self.assertRedirects(response, reverse("poll"), fetch_redirect_response=False)
        poll = Vote_Poll.objects.exclude(pk=self.h.pk).get()
        self.assert_open_defaults(poll, "Two clocks")
        self.assertEqual(poll.Vote_Poll_Start, T + timedelta(seconds=1))
        self.assert_background(before)
