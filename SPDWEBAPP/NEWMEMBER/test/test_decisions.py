from types import SimpleNamespace
from unittest.mock import patch
from itertools import product

from django.urls import reverse

from NEWMEMBER import views_functions as functions
from NEWMEMBER.models import NewMember_Mark_Event_and_Request as Mark
from SPDWEBAPP_CORE.testing.helpers import at_time
from .support import WorkflowCase, NOW


class DecisionTests(WorkflowCase):
    def test_pending_review_lists_only_requested_marks(self):
        Mark.objects.filter(pk=self.m.pk).update(mark_event_date='2026-10-15')
        newer = self.mark(self.a, self.t2, day='2026-10-16')
        denied = self.mark(self.b, self.t1, status='denied')
        self.login(self.r)
        before = self.capture()
        response = self.client.get(reverse('newmember_approve'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newmember_marks_approve.html')
        self.assertEqual(list(response.context['pending_requests']), [newer, self.m])
        for user in [self.a, self.b, self.t1, self.t2]:
            self.assertContains(response, user.brother_profile.firstName)
        self.assertContains(response, 'name="mark_id"')
        for action in ['approve', 'deny']:
            self.assertContains(response, 'value="' + action + '"')
        self.unchanged(before)
        self.identity(self.r)

    def review(self, action):
        self.login(self.r)
        before = self.capture(exclude=(self.m,))
        old = self.mark_state(self.m)
        with at_time(NOW):
            response = self.client.post(reverse('newmember_approve'), {'mark_id': self.m.pk, 'action': action})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newmember_marks_approve.html')
        self.message(response, 'successfully ' + ('approved' if action == 'approve' else 'denied'))
        self.assertNotIn(self.m, response.context['pending_requests'])
        self.assert_changes(self.m, old, mark_approval_status='approved' if action == 'approve' else 'denied',
                            mark_approver_name='Rae Reviewer', mark_submission_approval_date=NOW)
        self.unchanged(before)
        self.identity(self.r)

    def test_board_approves_another_request(self):
        self.review('approve')

    def test_board_denies_another_request(self):
        self.review('deny')

    def test_unknown_mark_id_reports_not_found(self):
        self.login(self.r)
        before = self.capture()
        response = self.client.post(reverse('newmember_approve'), {'mark_id': '999999', 'action': 'approve'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newmember_marks_approve.html')
        self.message(response, 'Mark not found')
        self.assertIn(self.m, response.context['pending_requests'])
        result = functions.process_mark_approval(SimpleNamespace(user=self.r), '999999', 'approve')
        self.assertEqual(result, (False, 'Mark not found'))
        self.unchanged(before)
        self.identity(self.r)

    def test_approval_save_failure_keeps_original_row(self):
        before = self.capture()
        with patch.object(Mark, 'save', side_effect=RuntimeError('synthetic write failure')):
            success, message = functions.process_mark_approval(SimpleNamespace(user=self.r), self.m.pk, 'approve')
        self.assertIs(success, False)
        self.assertIn('Error processing request:', message)
        self.m.refresh_from_db()
        self.assertEqual(self.m.mark_approval_status, 'requested')
        self.assertIsNone(self.m.mark_submission_approval_date)
        self.assertIsNone(self.m.mark_approver_name)
        self.unchanged(before)


class EditTests(WorkflowCase):
    def test_edit_form_prefills_single_target(self):
        Mark.objects.filter(pk=self.m.pk).update(mark_approval_status='approved')
        self.login(self.r)
        before = self.capture()
        response = self.client.get(self.edit_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newmember_marks_request.html')
        self.assertIs(response.context['editing'], True)
        self.assertEqual(response.context['mark'].pk, self.m.pk)
        for snippet in ['name="target_user"', 'value="Workshop"', 'value="2"',
                        'value="2026-10-16"', 'value="update"', 'value="deny"']:
            self.assertContains(response, snippet)
        html = response.content.decode()
        select = html.split('<select ', 1)[1].split('</select>', 1)[0]
        self.assertNotIn(' multiple ', select)
        self.assertIn(f'value="{self.t1.pk}" selected', select)
        self.assertIn(f'value="{self.t2.pk}"', select)
        self.unchanged(before)
        self.identity(self.r)

    def test_board_edit_retargets_and_sets_editor_only(self):
        self.login(self.r)
        for status, value in product(['requested', 'approved', 'denied'], ['-2', '0', '3']):
            with self.subTest(status=status, value=value):
                mark = self.mark(self.a, self.t1, status=status, day='2026-10-14', title='Original')
                before = self.capture(exclude=(mark,))
                old = self.mark_state(mark)
                with at_time(NOW):
                    response = self.client.post(self.edit_url(mark), self.payload(self.t2, mark_value=value))
                self.assertRedirects(response, reverse('newmember_mark_history', args=[self.t2.pk]), fetch_redirect_response=False)
                self.message(response, 'Mark updated successfully')
                self.assert_changes(mark, old, target_user_id=self.t2.pk, mark_event_title='Lab',
                                    mark_value=int(value), mark_event_date=NOW.date().replace(day=16),
                                    last_edited_by_id=self.r.pk, last_edited_at=NOW)
                self.unchanged(before)
                self.identity(self.r)

    def test_nonexistent_retarget_leaves_entire_mark_unchanged(self):
        Mark.objects.filter(pk=self.m.pk).update(mark_approval_status='approved')
        self.login(self.r)
        before = self.capture()
        response = self.client.post(self.edit_url(), self.payload(mark_reason='Lab', target_user='999999'))
        self.assertRedirects(response, self.edit_url(), fetch_redirect_response=False)
        self.message(response, 'Invalid target user selected')
        self.unchanged(before)
        self.identity(self.r)

    def test_missing_edit_resource_returns_404(self):
        self.r.brother_profile.roles.add(self.user('educator', ('NME',)).brother_profile.roles.get(name='NME'))
        self.login(self.r)
        before = self.capture()
        for target in ['999999', 'not-an-int']:
            for method in ['get', 'post']:
                for payload in [{'action': 'deny'}, self.payload()]:
                    with self.subTest(target=target, method=method, payload=payload):
                        response = getattr(self.client, method)('/newmember/edit/' + target + '/', payload)
                        self.assertEqual(response.status_code, 404)
                        self.unchanged(before)
                        self.identity(self.r)

    def test_educator_board_edit_deny_sets_both_audits(self):
        educator = self.user('educator', ('NME',))
        self.r.brother_profile.roles.add(educator.brother_profile.roles.get(name='NME'))
        self.login(self.r)
        before = self.capture(exclude=(self.m,))
        old = self.mark_state(self.m)
        with at_time(NOW):
            response = self.client.post(self.edit_url(), {'action': 'deny'})
        self.assertRedirects(response, reverse('newmember_marks_dashboard'), fetch_redirect_response=False)
        self.message(response, 'Mark successfully denied')
        self.assert_changes(self.m, old, mark_approval_status='denied', mark_approver_name='Rae Reviewer',
                            mark_submission_approval_date=NOW, last_edited_by_id=self.r.pk,
                            last_edited_at=NOW)
        self.unchanged(before)
        self.identity(self.r)
