"""Marks read contracts separate personal reasons, class totals and review capability."""
from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from AUTHENTICATE.models import Brother_Profile, Role
from NEWMEMBER.models import NewMember_Mark_Event_and_Request as Mark


class MarksReadApiTests(TestCase):
    url = '/api/v1/new-members/'

    def member(self, username, *roles):
        user = User.objects.create(username=username)
        profile = Brother_Profile.objects.create(user=user, firstName=username.title(), lastName='Example')
        for role in roles:
            profile.roles.add(Role.objects.get_or_create(name=role)[0])
        return user, profile

    def setUp(self):
        self.active, _ = self.member('active', 'ACTIVE')
        self.new, self.new_profile = self.member('new', 'NEW_MEMBER')
        self.other, _ = self.member('other', 'NEW_MEMBER')
        self.today = timezone.localdate()

    def mark(self, title, value, status='approved', target=None, requester=None, days=0):
        return Mark.objects.create(requesting_user=requester or self.active,
            target_user=target or self.new, mark_event_title=title, mark_value=value,
            mark_event_date=self.today - timedelta(days=days), mark_approval_status=status)

    def test_anonymous_alumni_unclassified_and_missing_profile_denied(self):
        self.assertEqual(self.client.get(self.url).status_code, 403)
        for username, roles in [('alum', ('ALUMNI',)), ('none', ())]:
            self.client.force_login(self.member(username, *roles)[0])
            self.assertEqual(self.client.get(self.url).status_code, 403)
        self.client.force_login(User.objects.create(username='missing-profile'))
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_personal_approved_signed_sum_latest_order_and_whitelist_ignore_target_injection(self):
        older = self.mark('Own earlier', 5, days=3)
        latest = self.mark('Own latest', -7)
        self.mark('Own pending private', 100, 'requested')
        self.mark('Own denied private', 100, 'denied')
        self.mark('Other disciplinary reason', 10, target=self.other)
        self.client.force_login(self.new)
        response = self.client.get(self.url, {'user_id': self.other.pk, 'mode': 'active'})
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        data = response.json()
        self.assertEqual(data['mode'], 'personal')
        self.assertEqual((data['members'], data['submissions'], data['analytics']), ([], [], None))
        self.assertFalse(data['can_submit'])
        personal = data['personal']
        self.assertEqual((personal['total_marks'], personal['standing'], personal['class_average']),
                         (-2, 'Needs Improvement', 4.0))
        self.assertEqual(personal['latest_mark']['id'], latest.pk)
        self.assertEqual([mark['id'] for mark in personal['history']], [latest.pk, older.pk])
        self.assertEqual(personal['history_url'], f'/newmember/history/{self.new.pk}/')
        self.assertEqual(set(personal['history'][0]), {'id', 'title', 'value', 'date', 'status'})
        for private in ('Other disciplinary reason', 'Own pending private', 'Own denied private', 'username', 'mark_approver_name'):
            self.assertNotIn(private, str(data))

    def test_zero_positive_and_dual_role_personal_precedence(self):
        self.client.force_login(self.new)
        empty = self.client.get(self.url).json()['personal']
        self.assertEqual((empty['total_marks'], empty['standing'], empty['latest_mark'], empty['history']),
                         (0, 'Good Standing', None, []))
        self.mark('Positive', 4)
        self.new_profile.roles.add(Role.objects.get_or_create(name='ACTIVE')[0])
        data = self.client.get(self.url).json()
        self.assertEqual((data['mode'], data['personal']['total_marks']), ('personal', 4))
        self.assertTrue(data['can_submit'])
        self.assertIsNone(data['analytics'])

    def test_active_class_totals_order_and_analytics_do_not_expose_other_reasons(self):
        self.mark('Other private reason', -3, target=self.other)
        self.mark('Own class positive reason', 4)
        self.mark('Unapproved class reason', 80, 'requested')
        self.client.force_login(self.active)
        data = self.client.get(self.url).json()
        self.assertEqual(data['mode'], 'active')
        self.assertIsNone(data['personal'])
        self.assertEqual([m['total_marks'] for m in data['members']], [-3, 4])
        self.assertEqual([m['is_negative'] for m in data['members']], [True, False])
        self.assertEqual(data['analytics'], {'total_new_members': 2, 'members_in_good_standing': 1,
            'average_marks': 0.5, 'marks_this_week': 2, 'pending_requests': 1})
        self.assertEqual(set(data['members'][0]), {'display_name', 'total_marks', 'is_negative', 'history_url'})
        self.assertNotIn('Other private reason', str(data))
        self.assertNotIn('Own class positive reason', str(data))

    def test_submissions_are_own_requested_or_recent_denied_in_event_order(self):
        pending = self.mark('Own pending', 1, 'requested', days=30)
        recent = self.mark('Own recent denied', -1, 'denied', days=13)
        self.mark('Own old denied', -1, 'denied', days=15)
        self.mark('Own approved excluded', 3)
        self.mark('Other caller pending private', 1, 'requested', requester=self.other)
        self.client.force_login(self.active)
        data = self.client.get(self.url).json()
        self.assertEqual([m['id'] for m in data['submissions']], [recent.pk, pending.pk])
        self.assertEqual(set(data['submissions'][0]), {'id', 'title', 'value', 'date', 'status', 'target_name'})
        self.assertNotIn('Own old denied', str(data))
        self.assertNotIn('Other caller pending private', str(data))

    def test_nm_board_only_has_review_handoff_without_class_or_personal_data(self):
        board, _ = self.member('board', 'NM_BOARD')
        self.mark('Private reason', 2, 'requested')
        self.client.force_login(board)
        data = self.client.get(self.url).json()
        self.assertEqual(data, {'mode': 'review', 'can_review': True, 'can_submit': False,
            'personal': None, 'analytics': None, 'members': [], 'submissions': []})
        session = self.client.get('/api/v1/session/').json()
        self.assertTrue(session['member']['capabilities']['new_members'])

    def test_review_requires_nm_board_not_exec_or_nme(self):
        for code in ('EXEC', 'NME', 'NM_BOARD'):
            user, _ = self.member(code.lower(), 'ACTIVE', code)
            self.client.force_login(user)
            self.assertEqual(self.client.get(self.url).json()['can_review'], code == 'NM_BOARD')

    def test_empty_active_class_and_post_is_read_only(self):
        self.new_profile.roles.clear()
        self.other.brother_profile.roles.clear()
        self.client.force_login(self.active)
        data = self.client.get(self.url).json()
        self.assertEqual((data['members'], data['submissions'], data['analytics']['average_marks']), ([], [], 0.0))
        self.assertEqual(self.client.post(self.url, {'value': 10}).status_code, 405)
        self.assertFalse(Mark.objects.exists())
