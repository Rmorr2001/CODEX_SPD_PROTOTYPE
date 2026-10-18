"""Domain-owned poll admin permissions, output and invalid-form state preservation."""
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth import SESSION_KEY
from django.test import Client, SimpleTestCase
from django.urls import reverse
from django.utils.safestring import SafeData

from PARLEYPRO.admin import VotePollAdmin
from PARLEYPRO.models import Brother_votes, Vote_Poll
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import csrf_client, login_actor
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope
from .support import PollTestCase, csrf_token, grant, make_poll


def admin_url(action, poll=None):
    return reverse(f"admin:PARLEYPRO_vote_poll_{action}", args=[poll.pk] if poll else None)


class IconTests(SimpleTestCase):
    def test_admin_result_icon_labels_and_safe_html(self):
        model_admin = VotePollAdmin(Vote_Poll, admin.site)
        for yes, no, label, color, symbol in (
            (2, 1, "Passed", "green", "✔️"),
            (1, 2, "Failed", "red", "❌"),
            (1, 1, "Tied", "gold", "⚖️"),
            (0, 0, "Tied", "gold", "⚖️"),
        ):
            with self.subTest(counts=(yes, no)):
                poll = Vote_Poll(Vote_Poll_Count_Yes=yes, Vote_Poll_Count_No=no)
                result = model_admin.poll_result_icon(poll)
                self.assertIsInstance(result, SafeData)
                self.assertHTMLEqual(result, f'<span style="color: {color};">{symbol} {label}</span>')
        self.assertEqual(model_admin.poll_result_icon.short_description, "Result")
        self.assertEqual(model_admin.poll_result_icon.admin_order_field, "Vote_Poll_Count_Yes")


class AdminTests(PollTestCase):
    def staff_client(self, name, *permissions, is_superuser=False, is_active=True):
        actor = make_user(username=name, roles=(), is_staff=True,
                          is_superuser=is_superuser, is_active=is_active)
        grant(actor, *permissions)
        client = csrf_client()
        login_actor(client, actor)
        return actor, client

    def token(self, client):
        return csrf_token(client.get(reverse("admin:index")))

    def assert_no_admin_writes(self, before):
        assert_unchanged(before)
        self.assertEqual(LogEntry.objects.count(), 0)
        self.assertEqual(Vote_Poll.objects.count(), 1)
        self.assertEqual(Brother_votes.objects.count(), 1)

    def test_admin_result_column_sorts_by_yes_count(self):
        actor, client = self.staff_client("viewer", "view_vote_poll")
        self.h.delete()
        first = make_poll(creator=self.b, name="Two yes", yes=2, no=0)
        second = make_poll(creator=self.b, name="Three yes losing", yes=3, no=4)
        third = make_poll(creator=self.b, name="One yes", yes=1, no=0)
        before = snapshot_scope([actor, self.a, self.b, self.b_choice, first, second, third])
        response = client.get(admin_url("changelist"), {"o": "6"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row.pk for row in response.context["cl"].result_list],
                         [third.pk, first.pk, second.pk])
        self.assertEqual(tuple(response.context["cl"].list_display), (
            "Vote_Poll_Name", "created_by", "Vote_Poll_Start", "Vote_Poll_End",
            "Vote_Poll_Count_Yes", "Vote_Poll_Count_No", "poll_result_icon",
        ))
        self.assertContains(response, "Passed")
        self.assertContains(response, "Failed")
        assert_unchanged(before)
        self.assertEqual(LogEntry.objects.count(), 0)

    def test_admin_denies_anonymous_and_nonstaff_domain_executive(self):
        before = self.background()
        for client in (Client(), self.client):
            for action in ("changelist", "add", "change", "delete"):
                with self.subTest(authenticated=SESSION_KEY in client.session, action=action):
                    path = admin_url(action, self.h if action in ("change", "delete") else None)
                    response = client.get(path)
                    self.assertRedirects(response, f'{reverse("admin:login")}?next={path}',
                                         fetch_redirect_response=False)
                    self.assertNotContains(response, self.h.Vote_Poll_Name, status_code=302)
                    self.assert_background(before)

    def test_admin_staff_without_model_permissions_cannot_read_or_write(self):
        actor, client = self.staff_client("no-permissions")
        token = self.token(client)
        before = snapshot_scope([actor, self.a, self.b, self.h, self.b_choice])
        for action in ("changelist", "add", "change", "delete"):
            path = admin_url(action, self.h if action in ("change", "delete") else None)
            response = client.get(path)
            self.assertEqual(response.status_code, 403)
            self.assert_no_admin_writes(before)
        for action, payload in (("change", {"Vote_Poll_Name": "Unauthorized"}),
                                ("delete", {"post": "yes"})):
            response = client.post(admin_url(action, self.h),
                                   {**payload, "csrfmiddlewaretoken": token})
            self.assertEqual(response.status_code, 403)
            self.assert_no_admin_writes(before)

    def test_admin_view_only_actor_cannot_post_change_or_delete(self):
        actor, client = self.staff_client("view-only", "view_vote_poll")
        token = self.token(client)
        before = snapshot_scope([actor, self.a, self.b, self.h, self.b_choice])
        for action in ("changelist", "change"):
            path = admin_url(action, self.h if action == "change" else None)
            self.assertEqual(client.get(path).status_code, 200)
        self.assertEqual(client.get(admin_url("add")).status_code, 403)
        for action, payload in (("change", {"Vote_Poll_Name": "Unauthorized"}),
                                ("delete", {"post": "yes"})):
            response = client.post(admin_url(action, self.h),
                                   {**payload, "csrfmiddlewaretoken": token})
            self.assertEqual(response.status_code, 403)
            self.assert_no_admin_writes(before)

    def test_admin_granular_permissions_gate_corresponding_actions(self):
        before = self.background()
        variants = [(action, (f"{action}_vote_poll",), False)
                    for action in ("add", "change", "delete")]
        variants.append(("super", (), True))
        for permitted, permissions, superuser in variants:
            with self.subTest(permission=permitted):
                actor, client = self.staff_client(f"staff-{permitted}", *permissions,
                                                  is_superuser=superuser)
                actor_before = snapshot_scope([actor])
                for action in ("add", "change", "delete"):
                    path = admin_url(action, self.h if action != "add" else None)
                    expected = 200 if superuser or action == permitted else 403
                    self.assertEqual(client.get(path).status_code, expected)
                    assert_unchanged(actor_before)
                    self.assert_background(before)

    def test_inactive_staff_is_not_admitted_to_admin(self):
        actor, client = self.staff_client(
            "inactive-staff", "add_vote_poll", "change_vote_poll", "view_vote_poll",
            "delete_vote_poll", is_active=False,
        )
        before = snapshot_scope([actor, self.a, self.b, self.h, self.b_choice])
        path = admin_url("changelist")
        response = client.get(path)
        self.assertRedirects(response, f'{reverse("admin:login")}?next={path}',
                             fetch_redirect_response=False)
        self.assert_no_admin_writes(before)

    def test_admin_invalid_poll_form_preserves_database(self):
        actor, client = self.staff_client("editor", "add_vote_poll", "change_vote_poll")
        token = self.token(client)
        before = snapshot_scope([actor, self.a, self.b, self.h, self.b_choice])
        baseline = {"Vote_Poll_Name": "Edited motion", "created_by": str(self.b.pk),
                    "Vote_Poll_Count_Yes": "4", "Vote_Poll_Count_No": "2",
                    "Vote_Poll_End_0": "2026-01-15", "Vote_Poll_End_1": "17:59:59"}
        variants = [
            ({"Vote_Poll_Name": ""}, "Vote_Poll_Name", "required"),
            ({"created_by": ""}, "created_by", "required"),
            ({"Vote_Poll_Name": "x"*201}, "Vote_Poll_Name", "max_length"),
            ({"Vote_Poll_Count_Yes": "abc"}, "Vote_Poll_Count_Yes", "invalid"),
            ({"Vote_Poll_End_0": "bad-date"}, "Vote_Poll_End", "invalid"),
        ]
        for action in ("add", "change"):
            for changes, field, code in variants:
                with self.subTest(action=action, field=field):
                    payload = {**baseline, **changes, "csrfmiddlewaretoken": token, "_save": "Save"}
                    path = admin_url(action, self.h if action == "change" else None)
                    response = client.post(path, payload)
                    self.assertEqual(response.status_code, 200)
                    errors = response.context["adminform"].form.errors.as_data()
                    self.assertIn(field, errors)
                    self.assertEqual(errors[field][0].code, code)
                    self.assert_no_admin_writes(before)
