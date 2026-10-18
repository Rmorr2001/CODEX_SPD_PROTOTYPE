from datetime import date
import re

from django.test import SimpleTestCase
from django.utils.html import escape

from AUTHENTICATE.models import Brother_Profile, Role
from PHILANTHROPY.templatetags.philanthropy_extras import hours_remaining
from PHILANTHROPY.views_functions import retrieve_individual_brother_history
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import login_actor

from .support import (DASHBOARD, T1, Event, PhilanthropyCase,
                      edit, history, make_event, messages)


class RemainingHoursTests(SimpleTestCase):
    def test_hours_remaining_clamps_numeric_difference(self):
        for goal, current, expected in ((10, 0, 10.0), (10, 5, 5.0), (10, 10, 0),
                                         (10, 12, 0), ('10', '0.5', 9.5)):
            with self.subTest(goal=goal, current=current):
                self.assertEqual(hours_remaining(goal, current), expected)


class HistoryTests(PhilanthropyCase):
    def setUp(self):
        super().setUp()
        self.a = make_user(username='a', roles=('ACTIVE',))
        self.b = make_user(username='b', roles=('ACTIVE',))
        self.f = make_event(self.b, title='Other owner', hours=70, status='approved')
        login_actor(self.client, self.a)

    def test_history_helper_buckets_approved_events_and_lifetime(self):
        # The matching profile/user_id pair exercises the actual helper's owner scope.
        days = (date(2025, 6, 30), date(2025, 7, 1), date(2026, 6, 30), date(2026, 7, 1))
        events = [make_event(self.b, hours=i, day=day, status='approved')
                  for i, day in enumerate(days, 2)]
        requested = make_event(self.b, hours=99)
        denied = make_event(self.b, hours=99, status='denied')
        # Put the unrelated 70-hour control on A rather than the target B.
        self.f.user = self.a
        self.f.save()
        before = self.capture(self.a, self.b, self.f, requested, denied, *events)
        buckets, lifetime = retrieve_individual_brother_history(self.b.brother_profile,
                                                                self.b.pk)
        self.assertEqual([b['start'] for b in buckets], [2026, 2025, 2024])
        self.assertEqual([b['total_hours'] for b in buckets], [5, 7, 2])
        self.assertEqual([b['events'] for b in buckets],
                         [[events[3]], [events[2], events[1]], [events[0]]])
        self.assertEqual(lifetime, 14)
        self.unchanged(before)

    def test_own_history_view_renders_approved_only(self):
        approved = make_event(self.a, title='Own approved', hours=3,
                              day=date(2025, 7, 1), status='approved')
        requested = make_event(self.a, title='Own pending', hours=40)
        denied = make_event(self.a, title='Own denied', hours=50, status='denied')
        before = self.capture(self.a, self.b, self.f, approved, requested, denied)
        response = self.client.get(history(self.a))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'philanthropy_brother_history.html')
        self.assertEqual(response.context['lifetime_total'], 3)
        buckets = response.context['academic_year_totals']
        self.assertEqual([(b['start'], b['total_hours']) for b in buckets], [(2025, 3)])
        self.assertEqual(buckets[0]['events'], [approved])
        for event in (requested, denied, self.f):
            self.assertNotContains(response, event.philanthropy_event_title)
        self.unchanged(before)
        self.assert_session_actor(self.client, self.a)

    def test_empty_approved_history_renders_zero_and_empty_text(self):
        requested = make_event(self.a)
        denied = make_event(self.a, status='denied')
        before = self.capture(self.a, self.b, self.f, requested, denied)
        response = self.client.get(history(self.a))
        self.assertContains(response, 'No philanthropy hours recorded yet.')
        self.assertEqual(response.context['academic_year_totals'], [])
        self.assertEqual(response.context['lifetime_total'], 0)
        self.assertEqual(retrieve_individual_brother_history(self.a.brother_profile,
                                                             self.a.pk), ([], 0))
        self.unchanged(before)
        self.assert_session_actor(self.client, self.a)
        self.assertEqual(list(self.media_root.rglob('*')), [])

    def test_history_marks_edited_event(self):
        edited_title = 'Edited <service>'
        edited = make_event(self.a, title=edited_title, status='approved', last_edited_at=T1)
        original = make_event(self.a, title='Original service', status='approved')
        before = self.capture(self.a, self.b, self.f, edited, original)
        response = self.client.get(history(self.a))
        self.assertEqual(response.status_code, 200)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', response.content.decode(), re.S)
        edited_row = next(row for row in rows if escape(edited_title) in row)
        original_row = next(row for row in rows if 'Original service' in row)
        self.assertIn('[EDITED]', edited_row)
        self.assertNotIn('[EDITED]', original_row)
        self.assertIn('>2', edited_row)
        self.assertIn('>2', original_row)
        self.assertNotContains(response, edited_title)
        self.unchanged(before)

    def test_history_edit_link_tracks_declared_chair_role(self):
        event = make_event(self.a, status='approved')
        for is_chair in (False, True):
            with self.subTest(is_chair=is_chair):
                if is_chair:
                    self.a.brother_profile.roles.add(
                        Role.objects.get_or_create(name='PHIL_CHAIR')[0])
                before = self.capture(self.a, self.b, self.f, event)
                response = self.client.get(history(self.a))
                self.assertEqual(response.status_code, 200)
                self.assertIs(response.context['is_philanthropy_chair'], is_chair)
                if is_chair:
                    self.assertContains(response, f'href="{edit(event)}"')
                else:
                    self.assertNotContains(response, f'href="{edit(event)}"')
                self.unchanged(before)

    def test_missing_target_profile_redirects_without_record_changes(self):
        profileless = make_user(username='profileless', with_profile=False)
        before = self.capture(self.a, self.b, self.f, profileless)
        profile_count = Brother_Profile.objects.count()
        for user_id in (profileless.pk, 999999):
            with self.subTest(user_id=user_id):
                response = self.client.get(f'/philanthropy/brother/{user_id}/')
                self.assertRedirects(response, DASHBOARD, fetch_redirect_response=False)
                self.assertIn('Brother not found.', messages(response))
                self.assertNotIn('Other owner', response.content.decode())
                self.assertEqual(Brother_Profile.objects.count(), profile_count)
                self.assertFalse(Brother_Profile.objects.filter(user=profileless).exists())
                self.unchanged(before)
                self.assert_session_actor(self.client, self.a)

    def test_dashboard_and_history_remaining_text_uses_tag(self):
        event = make_event(self.a, hours=5, day=date(2025, 7, 1), status='approved')
        self.f.philanthropy_event_hours = 10
        self.f.philanthropy_event_date = date(2025, 7, 1)
        self.f.save()
        before = self.capture(self.a, self.b, self.f, event)
        dashboard = self.client.get(DASHBOARD, {'year': '2025'})
        own_history = self.client.get(history(self.a))
        self.assertContains(dashboard, '5.0 hours remaining')
        self.assertContains(dashboard, 'Complete')
        self.assertContains(own_history, '5.0 hours needed')
        self.assertNotContains(dashboard, '-5.0 hours remaining')
        self.unchanged(before)
