from datetime import date

from django.template import Context, Template
from django.test import SimpleTestCase
from django.urls import reverse
from django.utils import timezone

from NEWMEMBER import views_functions as f
from NEWMEMBER.models import NewMember_Mark_Event_and_Request as Mark
from NEWMEMBER.templatetags.newmember_extras import hours_remaining
from .support import MarkCase, NOW
from SPDWEBAPP_CORE.testing.helpers import at_time


class ReadModelTests(MarkCase):
    def setUp(self):
        super().setUp()
        self.a = self.user('a', ('ACTIVE',))
        self.b = self.user('b', ('ALUMNI',))
        self.t1 = self.user('t1', ('NEW_MEMBER',), profile_fields={'lastName': 'Able'})
        self.t2 = self.user('t2', ('NEW_MEMBER',), profile_fields={'lastName': 'Baker'})
        self.t3 = self.user('t3', ('NEW_MEMBER',), profile_fields={'lastName': 'Zed'})

    def signed_marks(self):
        plus = self.mark(self.a, self.t1, status='approved', value=5, day='2026-10-14')
        minus = self.mark(self.a, self.t1, status='approved', value=-8)
        self.mark(self.a, self.t2, status='approved', value=0)
        for status in ['requested', 'denied']:
            self.mark(self.a, self.t1, status=status, value=99, day='2026-10-17')
        return plus, minus

    def test_signed_class_totals_and_order_exclude_unapproved(self):
        self.signed_marks()
        self.mark(self.a, self.b, status='approved', value=90)
        before = self.capture()
        members = f.get_new_members()
        self.assertEqual([p.user_id for p in members], [self.t1.pk, self.t2.pk, self.t3.pk])
        progress = f.calculate_member_marks(members)
        self.assertEqual([p['user'].pk for p in progress], [self.t1.pk, self.t2.pk, self.t3.pk])
        self.assertEqual([p['total_marks'] for p in progress], [-3, 0, 0])
        self.assertEqual([p['is_negative'] for p in progress], [True, False, False])
        self.unchanged(before)

    def test_personal_stats_use_approved_signed_totals(self):
        _, minus = self.signed_marks()
        before = self.capture()
        personal = f.get_personal_stats(self.t1)
        self.assertEqual(personal, {'total_marks': -3, 'class_average': -1.0,
                                   'standing': 'Needs Improvement', 'latest_mark': minus})
        second = f.get_personal_stats(self.t2)
        self.assertEqual(second['total_marks'], 0)
        self.assertEqual(second['standing'], 'Good Standing')
        self.assertEqual(second['class_average'], -1.0)
        self.unchanged(before)

    def test_two_bound_date_ranges_are_inclusive(self):
        requested = {}
        for day, value in [(9, 1), (10, 2), (12, 4), (13, 8)]:
            self.mark(self.a, self.t1, status='approved', value=value, day=f'2026-10-{day:02d}')
            requested[day] = self.mark(self.a, self.t1, day=f'2026-10-{day:02d}')
        self.mark(self.b, self.t1, day='2026-10-11')
        before = self.capture()
        progress = f.calculate_member_marks([self.t1.brother_profile], date(2026, 10, 10), date(2026, 10, 12))
        self.assertEqual(progress[0]['total_marks'], 6)
        self.assertFalse(progress[0]['is_negative'])
        with at_time(NOW):
            submitted = list(f.get_user_submitted_marks(self.a, date(2026, 10, 10), date(2026, 10, 12)))
        self.assertEqual(submitted, [requested[12], requested[10]])
        self.unchanged(before)

    def test_active_analytics_count_events_and_signed_standing(self):
        for day, target in [(9, self.t1), (10, self.t1), (11, self.b)]:
            self.mark(self.a, target, status='approved', value=20, day=f'2026-10-{day:02d}')
        self.mark(self.a, self.t1)
        self.mark(self.b, self.t2)
        self.mark(self.a, self.t1, status='denied')
        before = self.capture()
        progress = [{'total_marks': total, 'is_negative': total < 0} for total in [-3, 0, 6]]
        with at_time(NOW), timezone.override('UTC'):
            analytics = f.get_active_member_analytics(progress)
        self.assertEqual(analytics, {'total_new_members': 3, 'members_in_good_standing': 2,
                                    'average_marks': 1.0, 'marks_this_week': 2, 'pending_requests': 2})
        self.unchanged(before)

    def test_own_denied_visibility_uses_actual_fourteen_days(self):
        denied = {day: self.mark(self.a, self.t1, status='denied', day=f'2026-10-{day:02d}',
                                mark_submission_approval_date=NOW) for day in [2, 3, 4]}
        old = self.mark(self.a, self.t1, day='2026-09-01', title='Old requested')
        recent = self.mark(self.a, self.t1, title='Recent requested')
        self.mark(self.a, self.t1, status='approved', value=99)
        self.mark(self.b, self.t1)
        self.mark(self.b, self.t1, status='denied')
        self.login(self.a)
        before = self.capture()
        expected = [recent, denied[4], denied[3], old]
        with at_time(NOW), timezone.override('UTC'):
            self.assertEqual(list(f.get_user_submitted_marks(self.a)), expected)
            response = self.client.get(reverse('newmember_marks_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['user_submitted_marks']), expected)
        self.assertContains(response, 'Old requested')
        self.assertContains(response, 'Recent requested')
        self.assertContains(response, 'Oct 04, 2026')
        self.assertNotContains(response, 'Oct 02, 2026')
        self.unchanged(before)
        self.identity(self.a)

    def test_single_role_dashboard_selects_matching_context(self):
        self.mark(self.a, self.t1, status='approved', value=-3)
        own = self.mark(self.a, self.t1)
        self.mark(self.b, self.t1)
        for actor in [self.a, self.t1]:
            self.login(actor)
            before = self.capture()
            with at_time(NOW):
                response = self.client.get(reverse('newmember_marks_dashboard'))
            self.assertEqual(response.status_code, 200)
            if actor == self.a:
                self.assertTemplateUsed(response, 'ACTIVE_newmember_marks_dashboard.html')
                self.assertEqual(list(response.context['user_submitted_marks']), [own])
                self.assertIsNone(response.context['personal_stats'])
                self.assertEqual(response.context['analytics']['total_new_members'], 3)
                self.assertIs(response.context['is_active'], True)
            else:
                self.assertTemplateUsed(response, 'newmember_marks_dashboard.html')
                self.assertEqual(response.context['personal_stats']['total_marks'], -3)
                self.assertIsNone(response.context['analytics'])
                self.assertIs(response.context['is_active'], False)
            self.unchanged(before)
            self.identity(actor)

    def test_class_choices_follow_reverse_enum_order(self):
        for user, pclass in [(self.a, 'Alpha'), (self.b, 'Beta'), (self.t1, 'Beta Gamma'),
                             (self.t2, 'Current'), (self.t3, 'Beta')]:
            profile = user.brother_profile
            profile.pclass = pclass  # Current intentionally bypasses model choice validation.
            profile.save()
        self.login(self.a)
        before = self.capture()
        response = self.client.get(reverse('newmember_marks_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pclasses'], ['Beta Gamma', 'Beta', 'Alpha'])
        for value in ['Beta Gamma', 'Beta', 'Alpha']:
            self.assertContains(response, f'<option value="{value}">')
        self.unchanged(before)
        self.identity(self.a)

    def test_pending_query_handles_missing_related_profiles(self):
        r = self.user('review', ('NM_BOARD',))
        bare_requester = self.user('bare-requester', with_profile=False)
        bare_target = self.user('bare-target', with_profile=False)
        older = self.mark(bare_requester, self.t1, day='2026-10-15')
        newer = self.mark(self.a, bare_target)
        self.mark(self.a, self.t1, status='approved')
        self.mark(self.a, self.t1, status='denied')
        self.login(r)
        before = self.capture()
        self.assertEqual(list(f.get_pending_mark_requests()), [newer, older])
        response = self.client.get(reverse('newmember_approve'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['pending_requests']), [newer, older])
        for mark in [newer, older]:
            self.assertContains(response, f'value="{mark.pk}"')
        self.unchanged(before)
        self.identity(r)

    def test_history_helper_returns_approved_target_total(self):
        plus = self.mark(self.a, self.t1, status='approved', value=4, day='2026-10-14')
        minus = self.mark(self.a, self.t1, status='approved', value=-7)
        for status in ['requested', 'denied']:
            self.mark(self.a, self.t1, status=status, value=99)
        self.mark(self.a, self.t2, status='approved', value=20)
        before = self.capture()
        marks, total = f.get_member_mark_history(self.t1.pk)
        self.assertEqual(list(marks), [minus, plus])
        self.assertEqual(total, -3)
        self.unchanged(before)

    def test_missing_or_non_new_member_history_redirects(self):
        bare = self.user('bare', with_profile=False)
        self.mark(self.a, self.t1)
        self.login(self.a)
        before = self.capture()
        for target in [999999, self.b.pk, bare.pk]:
            response = self.client.get(reverse('newmember_mark_history', args=[target]))
            self.assertRedirects(response, reverse('newmember_dashboard'), fetch_redirect_response=False)
            self.message(response, 'New Member not found')
            self.unchanged(before)
            self.identity(self.a)

    def test_empty_target_history_helper_returns_zero(self):
        mark = self.mark(self.a, self.t2, status='approved', value=-4)
        before = self.capture()
        marks, total = f.get_member_mark_history(self.t1.pk)
        self.assertEqual(list(marks), [])
        self.assertEqual(total, 0)
        marks, total = f.get_member_mark_history(self.t2.pk)
        self.assertEqual(list(marks), [mark])
        self.assertEqual(total, -4)
        self.unchanged(before)


class EmptyReadTests(MarkCase):
    def test_empty_analytics_and_personal_totals_are_zero(self):
        actor = self.user('active', ('ACTIVE',))
        for has_member in [False, True]:
            target = self.user('empty-member', ('NEW_MEMBER',)) if has_member else None
            for viewer in [actor] + ([target] if target else []):
                self.login(viewer)
                before = self.capture()
                with at_time(NOW):
                    members = f.get_new_members()
                    progress = f.calculate_member_marks(members)
                    analytics = f.get_active_member_analytics(progress)
                    response = self.client.get(reverse('newmember_marks_dashboard'))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(analytics, {'total_new_members': int(has_member),
                    'members_in_good_standing': int(has_member), 'average_marks': 0,
                    'marks_this_week': 0, 'pending_requests': 0})
                if target:
                    self.assertEqual(progress[0]['total_marks'], 0)
                    self.assertFalse(progress[0]['is_negative'])
                    self.assertEqual(f.get_personal_stats(target), {'total_marks': 0,
                        'class_average': 0.0, 'standing': 'Good Standing', 'latest_mark': None})
                else:
                    self.assertEqual(progress, [])
                self.unchanged(before)
                self.identity(viewer)


class FilterTests(SimpleTestCase):
    def test_hours_remaining_converts_numbers_and_floors_zero(self):
        for goal, current, expected in [(10, 3, 7), (10, 12, 0), (0, 0, 0), ('10', '2.5', 7.5), (-2, -5, 3)]:
            with self.subTest(goal=goal, current=current):
                self.assertEqual(hours_remaining(goal, current), expected)
                template = Template('{% load newmember_extras %}{{ goal|hours_remaining:current }}')
                self.assertEqual(float(template.render(Context({'goal': goal, 'current': current}))), expected)
