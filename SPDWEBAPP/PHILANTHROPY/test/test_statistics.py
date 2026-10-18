from datetime import date, datetime, timezone

from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, SimpleTestCase
from django.test.signals import template_rendered

from AUTHENTICATE.models import Role
from PHILANTHROPY import views, views_functions as functions
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import at_time, login_actor

from .support import DASHBOARD, T1, PhilanthropyCase, make_event


class AcademicYearTests(SimpleTestCase):
    def test_academic_year_dates_are_july_through_june(self):
        self.assertEqual(functions.get_academic_year_dates(2025),
                         (date(2025, 7, 1), date(2026, 6, 30)))
        start, end = functions.get_academic_year_dates(2023)
        self.assertEqual((start, end), (date(2023, 7, 1), date(2024, 6, 30)))
        self.assertLessEqual(start, date(2024, 2, 29))
        self.assertGreaterEqual(end, date(2024, 2, 29))
        self.assertIs(type(start), date)
        self.assertIs(type(end), date)

    def test_available_years_before_and_after_july(self):
        for instant, expected in (
            (datetime(2026, 6, 30, 23, 59, 59, tzinfo=timezone.utc), [2025, 2024, 2023]),
            (datetime(2026, 7, 1, tzinfo=timezone.utc), [2026, 2025, 2024]),
        ):
            with self.subTest(instant=instant), at_time(instant):
                self.assertEqual(functions.get_available_academic_years(), expected)

    def test_available_year_count_can_be_zero_or_one(self):
        with at_time(T1):
            self.assertEqual(functions.get_available_academic_years(past=1), [2026])
            self.assertEqual(functions.get_available_academic_years(past=0), [])
            self.assertEqual(functions.get_available_academic_years(), [2026, 2025, 2024])


class StatisticsTests(PhilanthropyCase):
    def setUp(self):
        super().setUp()
        self.a = make_user(username='a', roles=('ACTIVE',))
        self.b = make_user(username='b', roles=('ACTIVE',))
        self.f = make_event(self.b, title='Outside control', hours=7,
                            day=date(2024, 7, 1), status='approved')
        login_actor(self.client, self.a)

    def default_year(self, instant, day, year):
        event = make_event(self.a, day=day, status='approved')
        before = self.capture(self.a, self.b, event, self.f)
        with at_time(instant):
            response = self.client.get(DASHBOARD)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_year'], year)
        self.assertEqual(response.context['year_label'], f'{year}–{year + 1} Academic Year')
        self.assertEqual(list(response.context['user_events']), [event])
        self.assertEqual(response.context['user_total_hours'], 2)
        self.unchanged(before)

    def test_dashboard_default_year_before_july(self):
        self.default_year(datetime(2026, 6, 30, 23, 59, 59, tzinfo=timezone.utc),
                          date(2026, 6, 30), 2025)

    def test_dashboard_default_year_from_july(self):
        self.default_year(datetime(2026, 7, 1, tzinfo=timezone.utc), date(2026, 7, 1), 2026)

    def test_explicit_dashboard_year_overrides_clock(self):
        event = make_event(self.a, day=date(2024, 7, 1), status='approved')
        before = self.capture(self.a, self.b, event, self.f)
        with at_time(T1):
            response = self.client.get(DASHBOARD, {'year': '2024'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_year'], 2024)
        self.assertEqual(response.context['year_label'], '2024–2025 Academic Year')
        self.assertEqual(response.context['user_total_hours'], 2)
        self.assertEqual(response.context['available_years'], [2026, 2025, 2024])
        self.unchanged(before)

    def test_chapter_and_personal_approved_totals_are_scoped(self):
        c = make_user(username='zero', roles=('ACTIVE',))
        d = make_user(username='inactive', roles=('ALUMNI',))
        events = [make_event(self.a, hours=10, day=date(2025, 7, 1), status='approved'),
                  make_event(self.b, hours=5, day=date(2025, 7, 1), status='approved'),
                  make_event(d, hours=99, day=date(2025, 7, 1), status='approved'),
                  make_event(self.a, hours=40, day=date(2025, 7, 2)),
                  make_event(self.a, hours=50, day=date(2025, 7, 3), status='denied'),
                  make_event(self.a, hours=70, day=date(2025, 6, 30), status='approved')]
        before = self.capture(self.a, self.b, c, d, self.f, *events)
        response = self.client.get(DASHBOARD, {'year': '2025'})
        self.assertEqual(response.status_code, 200)
        context = response.context
        for key, value in {'total_chapter_hours': 15, 'total_active_members': 3,
                           'avg_hours_per_brother': 5, 'members_meeting_goal': 1,
                           'user_total_hours': 10}.items():
            self.assertEqual(context[key], value, key)
        self.assertEqual([(p['user'].pk, p['total_hours']) for p in
                          context['brothers_progress']],
                         [(self.a.pk, 10), (self.b.pk, 5), (c.pk, 0)])
        self.assertCountEqual(context['user_events'], [events[0], events[3], events[4]])
        request = RequestFactory().get(DASHBOARD)
        request.user = self.a
        own, total = functions.get_user_events_and_total_hours(
            request, date(2025, 7, 1), date(2026, 6, 30))
        self.assertEqual(total, 10)
        self.assertEqual(list(own), [events[4], events[3], events[0]])
        progress, total, goal = functions.collect_philanthropy_statistics(
            [self.a.brother_profile, self.b.brother_profile, c.brother_profile],
            date(2025, 7, 1), date(2026, 6, 30))
        self.assertEqual((total, goal), (15, 1))
        self.assertEqual([p['total_hours'] for p in progress], [10, 5, 0])
        self.unchanged(before)

    def test_goal_threshold_is_ten_approved_hours(self):
        for hours, goal in ((0, 0), (4, 0), (5, 0), (9, 0), (10, 1), (11, 1)):
            with self.subTest(hours=hours):
                event = make_event(self.a, hours=hours, day=date(2025, 7, 1),
                                   status='approved') if hours else None
                rows = [self.a, self.b, self.f] + ([event] if event else [])
                before = self.capture(*rows)
                progress, total, count = functions.collect_philanthropy_statistics(
                    [self.a.brother_profile], date(2025, 7, 1), date(2026, 6, 30))
                self.assertEqual((total, count), (hours, goal))
                self.assertEqual(len(progress), 1)
                self.assertEqual(progress[0]['user'], self.a)
                self.assertEqual(progress[0]['total_hours'], hours)
                self.unchanged(before)
                if event:
                    event.delete()

    def test_multiple_nonactive_roles_do_not_duplicate_statistics(self):
        for role in ('EXEC', 'PHIL_CHAIR'):
            self.a.brother_profile.roles.add(Role.objects.get_or_create(name=role)[0])
        self.b.brother_profile.roles.add(Role.objects.get_or_create(name='ALUMNI')[0])
        event = make_event(self.a, day=date(2025, 7, 1), status='approved')
        other = make_event(self.b, hours=3, day=date(2025, 7, 1), status='approved')
        before = self.capture(self.a, self.b, event, other, self.f)
        response = self.client.get(DASHBOARD, {'year': '2025'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['brothers_progress']), 2)
        for key, value in {'total_chapter_hours': 5, 'total_active_members': 2,
                           'avg_hours_per_brother': 2.5}.items():
            self.assertEqual(response.context[key], value)
        self.unchanged(before)

    def test_year_range_includes_july_first_and_june_thirtieth(self):
        days = (date(2025, 6, 30), date(2025, 7, 1), date(2026, 6, 30), date(2026, 7, 1))
        events = [make_event(self.a, hours=i, day=day, status='approved')
                  for i, day in enumerate(days, 1)]
        before = self.capture(self.a, self.b, self.f, *events)
        response = self.client.get(DASHBOARD, {'year': '2025'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['user_events']), [events[2], events[1]])
        self.assertEqual(response.context['user_total_hours'], 5)
        a_progress = next(p for p in response.context['brothers_progress']
                          if p['user'] == self.a)
        self.assertEqual(a_progress['total_hours'], 5)
        self.unchanged(before)

    def test_empty_selected_year_retains_zero_active_members(self):
        event = make_event(self.a, day=date(2024, 7, 1), status='approved')
        other = make_event(self.b, day=date(2026, 7, 1), status='approved')
        before = self.capture(self.a, self.b, event, other, self.f)
        response = self.client.get(DASHBOARD, {'year': '2025'})
        self.assertContains(response, 'No events submitted for this academic year.')
        self.assertEqual(list(response.context['user_events']), [])
        for key in ('user_total_hours', 'total_chapter_hours',
                    'avg_hours_per_brother', 'members_meeting_goal'):
            self.assertEqual(response.context[key], 0)
        self.assertEqual(response.context['total_active_members'], 2)
        self.assertCountEqual([(p['user'].pk, p['total_hours']) for p in
                               response.context['brothers_progress']],
                              [(self.a.pk, 0), (self.b.pk, 0)])
        self.unchanged(before)

    def test_statistics_empty_profile_input_returns_zeroes(self):
        event = make_event(self.a, status='approved')
        before = self.capture(self.a, self.b, event, self.f)
        self.assertEqual(functions.collect_philanthropy_statistics(
            [], date(2025, 7, 1), date(2026, 6, 30)), ([], 0, 0))
        self.unchanged(before)

    def test_unwrapped_dashboard_zero_denominator_is_safe(self):
        self.a.brother_profile.roles.clear()
        self.b.brother_profile.roles.set([Role.objects.get_or_create(name='ALUMNI')[0]])
        before = self.capture(self.a, self.b, self.f)
        request = RequestFactory().get(DASHBOARD)
        request.user = self.a
        SessionMiddleware(lambda r: None).process_request(request)
        MessageMiddleware(lambda r: None).process_request(request)
        contexts = []

        def receive(sender, template, context, **kwargs):
            if template.name == 'philanthropy_dashboard.html':
                contexts.append(context.flatten())

        template_rendered.connect(receive, weak=False)
        try:
            response = views.philanthropy_dashboard.__wrapped__.__wrapped__(request)
        finally:
            template_rendered.disconnect(receive)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(contexts), 1)
        for key in ('total_active_members', 'avg_hours_per_brother',
                    'total_chapter_hours', 'members_meeting_goal'):
            self.assertEqual(contexts[0][key], 0)
        self.assertEqual(contexts[0]['brothers_progress'], [])
        self.unchanged(before)
