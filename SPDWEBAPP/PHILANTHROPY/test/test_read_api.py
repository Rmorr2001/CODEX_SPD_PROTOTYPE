"""Own service reads retain academic boundaries, approvals and exact decimal storage."""
from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase
from AUTHENTICATE.models import Brother_Profile, Role
from PHILANTHROPY.models import Philanthropy_Hours_Event_and_Request as Event
from PHILANTHROPY.views_functions import get_available_academic_years


class ServiceReadApiTests(TestCase):
    def member(self, username, *roles):
        user = User.objects.create(username=username)
        profile = Brother_Profile.objects.create(user=user, firstName='Alex', lastName='Example')
        for code in roles:
            profile.roles.add(Role.objects.get_or_create(name=code)[0])
        return user, profile

    def setUp(self):
        self.user, self.profile = self.member('active', 'ACTIVE')
        self.other, _ = self.member('other', 'ACTIVE')
        self.year = get_available_academic_years()[0]

    def event(self, title, hours, day, status='approved', user=None):
        return Event.objects.create(user=user or self.user, philanthropy_event_title=title,
            philanthropy_event_hours=hours, philanthropy_event_date=day, philanthropy_approval_status=status)

    def test_anonymous_wrong_roles_and_missing_profile_denied(self):
        self.assertEqual(self.client.get('/api/v1/service/').status_code, 403)
        for username, roles in [('alum', ('ALUMNI',)), ('chair-only', ('PHIL_CHAIR',))]:
            self.client.force_login(self.member(username, *roles)[0])
            self.assertEqual(self.client.get('/api/v1/service/').status_code, 403)
        self.client.force_login(User.objects.create(username='no-profile'))
        self.assertEqual(self.client.get('/api/v1/service/').status_code, 403)

    def test_inclusive_july_june_own_records_and_approved_only_arithmetic(self):
        self.client.force_login(self.user)
        first = self.event('First day', 2, date(self.year, 7, 1))
        last = self.event('Last day', 3, date(self.year + 1, 6, 30))
        pending = self.event('Pending', 7, date(self.year, 8, 1), 'requested')
        denied = self.event('Denied', 11, date(self.year, 9, 1), 'denied')
        self.event('Prior year', 50, date(self.year, 6, 30))
        self.event('Next year', 50, date(self.year + 1, 7, 1))
        self.event('Other member private event', 100, date(self.year, 8, 1), user=self.other)
        response = self.client.get(f'/api/v1/service/?year={self.year}&user_id={self.other.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        data = response.json()
        self.assertEqual(data['approved_hours'], 5)
        self.assertEqual({event['id'] for event in data['events']}, {first.pk, last.pk, pending.pk, denied.pk})
        self.assertEqual({event['status'] for event in data['events']}, {'approved', 'requested', 'denied'})
        self.assertEqual(data['start_date'], f'{self.year}-07-01')
        self.assertEqual(data['end_date'], f'{self.year + 1}-06-30')
        self.assertEqual(data['history_url'], f'/philanthropy/brother/{self.user.pk}/')
        self.assertEqual(set(data['events'][0]), {'id', 'title', 'date', 'hours', 'status'})
        self.assertNotIn('Other member private event', str(data))

    def test_empty_default_and_year_options(self):
        self.client.force_login(self.user)
        data = self.client.get('/api/v1/service/').json()
        self.assertEqual(data['year'], self.year)
        self.assertEqual(data['available_years'], get_available_academic_years())
        self.assertEqual((data['approved_hours'], data['events']), (0, []))

    def test_year_validation_rejects_malformed_and_extreme_values(self):
        self.client.force_login(self.user)
        for year in ('', '2025.5', '+2025', ' 2025', '20x5', '9999', '1899', '2025,2026'):
            with self.subTest(year=year):
                self.assertEqual(self.client.get('/api/v1/service/', {'year': year}).status_code, 400)

    def test_approval_capability_requires_chair_and_active(self):
        self.client.force_login(self.user)
        self.assertFalse(self.client.get('/api/v1/service/').json()['can_review'])
        self.profile.roles.add(Role.objects.get_or_create(name='PHIL_CHAIR')[0])
        self.assertTrue(self.client.get('/api/v1/service/').json()['can_review'])
        self.profile.roles.remove(Role.objects.get(name='ACTIVE'))
        self.assertEqual(self.client.get('/api/v1/service/').status_code, 403)

    def test_fractional_input_preserves_decimal_storage(self):
        self.client.force_login(self.user)
        event = self.event('Fractional legacy record', 1.75, date(self.year, 8, 1))
        event.refresh_from_db()
        self.assertEqual(event.philanthropy_event_hours, 1.75)
        data = self.client.get('/api/v1/service/').json()
        self.assertEqual((data['approved_hours'], data['events'][0]['hours']), (1.75, 1.75))

    def test_submission_requires_complete_validated_fields(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post('/api/v1/service/', {'hours': 2}).status_code, 400)
        self.assertFalse(Event.objects.exists())
