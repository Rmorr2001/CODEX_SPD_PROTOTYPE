from django.urls import reverse

from NEWMEMBER.models import NewMember_Mark_Event_and_Request as Mark
from SPDWEBAPP_CORE.testing.helpers import at_time
from .support import WorkflowCase, NOW


class RequestTests(WorkflowCase):
    def test_request_form_lists_new_member_targets(self):
        self.login(self.a)
        before = self.capture()
        response = self.client.get(reverse('newmember_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newmember_marks_request.html')
        self.assertEqual([p.user_id for p in response.context['new_members']], [self.t1.pk, self.t2.pk])
        self.assertContains(response, 'name="target_users"')
        self.assertContains(response, 'multiple')
        for field in ['mark_value', 'mark_reason', 'mark_date', 'csrfmiddlewaretoken']:
            self.assertContains(response, 'name="' + field + '"')
        self.assertContains(response, 'value="submit"')
        self.assertNotIn(self.b.pk, [p.user_id for p in response.context['new_members']])
        self.identity(self.a)
        self.unchanged(before)

    def test_signed_multi_target_submission_creates_requested_marks(self):
        self.login(self.a)
        for value in ['-3', '0', '4']:
            with self.subTest(value=value):
                before = self.capture()
                old_ids = set(Mark.objects.values_list('pk', flat=True))
                with at_time(NOW):
                    response = self.client.post(reverse('newmember_request'), {
                        'target_users': [self.t1.pk, self.t2.pk], 'mark_value': value,
                        'mark_reason': 'Workshop', 'mark_date': '2026-10-16'})
                self.assertRedirects(response, reverse('newmember_marks_dashboard'), fetch_redirect_response=False)
                self.message(response, '2 new member(s)')
                created = list(Mark.objects.exclude(pk__in=old_ids).order_by('target_user_id'))
                self.assertEqual(len(created), 2)
                self.assertEqual([m.target_user_id for m in created], [self.t1.pk, self.t2.pk])
                for mark in created:
                    self.assertEqual((mark.requesting_user_id, mark.mark_value, mark.mark_event_title,
                                      mark.mark_event_date.isoformat(), mark.mark_approval_status),
                                     (self.a.pk, int(value), 'Workshop', '2026-10-16', 'requested'))
                    self.assertEqual(mark.mark_submission_request_date, NOW)
                    self.assertIsNone(mark.mark_submission_approval_date)
                    self.assertIsNone(mark.mark_approver_name)
                    self.assertIsNone(mark.last_edited_by_id)
                    self.assertIsNone(mark.last_edited_at)
                self.unchanged(before, count_delta=2)
                self.identity(self.a)
                Mark.objects.filter(pk__in=[m.pk for m in created]).delete()

    def test_board_submission_autoapproves_and_ignores_forged_audit(self):
        self.a.brother_profile.roles.add(self.r.brother_profile.roles.get(name='NM_BOARD'))
        self.login(self.a)
        before = self.capture()
        old_ids = set(Mark.objects.values_list('pk', flat=True))
        with at_time(NOW):
            response = self.client.post(reverse('newmember_request'), {
                'target_users': [self.t1.pk, self.t2.pk], 'mark_value': '2',
                'mark_reason': 'Workshop', 'mark_date': '2026-10-16',
                'requesting_user': self.b.pk, 'mark_approval_status': 'denied',
                'mark_approver_name': 'Forged', 'last_edited_by': self.b.pk})
        self.assertRedirects(response, reverse('newmember_marks_dashboard'), fetch_redirect_response=False)
        self.message(response, '2 new member(s)')
        created = list(Mark.objects.exclude(pk__in=old_ids).order_by('target_user_id'))
        self.assertEqual([m.target_user_id for m in created], [self.t1.pk, self.t2.pk])
        for mark in created:
            self.assertEqual((mark.requesting_user_id, mark.mark_approval_status,
                              mark.mark_approver_name, mark.mark_value, mark.mark_event_title,
                              mark.mark_event_date.isoformat()),
                             (self.a.pk, 'approved', 'Alex Able', 2, 'Workshop', '2026-10-16'))
            self.assertEqual(mark.mark_submission_request_date, NOW)
            self.assertEqual(mark.mark_submission_approval_date, NOW)
            self.assertIsNone(mark.last_edited_by_id)
            self.assertIsNone(mark.last_edited_at)
        self.identity(self.a)
        self.unchanged(before, count_delta=2)
