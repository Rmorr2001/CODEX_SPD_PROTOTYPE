"""Cross-adapter marks integrity and permissions beyond the historical read-only milestone."""
from io import BytesIO
from uuid import uuid4
from unittest.mock import patch
from django.db import IntegrityError
from openpyxl import load_workbook
from NEWMEMBER.models import NewMember_Mark_Event_and_Request as Mark, MarkSubmission
from NEWMEMBER.operations import submit_marks
from SPDWEBAPP_CORE.testing.helpers import csrf_client
from .support import WorkflowCase


class TransactionApiTests(WorkflowCase):
    def payload(self, **changes):
        return {'target_users': [self.t1.pk, self.t2.pk], 'mark_value': -2,
                'mark_reason': 'Fictional participation', 'mark_date': '2026-10-16',
                'request_key': str(uuid4()), **changes}

    def post(self, path, data, actor=None, client=None):
        client = client or self.client
        client.force_login(actor or self.a)
        return client.post('/api/v1/new-members/' + path, data, content_type='application/json')

    def test_batch_replay_conflict_and_legacy_read_same_records(self):
        payload = self.payload(requesting_user=self.b.pk, status='approved')
        before = Mark.objects.count()
        response = self.post('submissions/', payload)
        self.assertEqual(response.status_code, 201)
        ids = [row['id'] for row in response.json()]
        self.assertEqual(len(ids), 2)
        self.assertEqual(Mark.objects.count(), before+2)
        self.assertEqual(MarkSubmission.objects.count(), 1)
        for row in response.json():
            self.assertEqual((row['status'], row['requester_id'], row['value']), ('requested', self.a.pk, -2))
        replay = self.post('submissions/', payload)
        self.assertEqual([row['id'] for row in replay.json()], ids)
        self.assertEqual(Mark.objects.count(), before+2)
        changed = self.post('submissions/', {**payload, 'mark_value': 3})
        self.assertEqual(changed.status_code, 409)
        self.assertEqual(Mark.objects.count(), before+2)
        self.client.force_login(self.r)
        legacy = self.client.get('/newmember/approve/')
        self.assertContains(legacy, 'Fictional participation')

    def test_validation_rejects_entire_invalid_batches(self):
        before = Mark.objects.count()
        for fields in [{'target_users': []}, {'target_users': [self.t1.pk, self.t1.pk]},
                       {'target_users': [self.t1.pk, self.b.pk]}, {'mark_value': 1.25},
                       {'mark_reason': ''}, {'mark_reason': 'x'*101}, {'mark_date': '2026-02-30'},
                       {'request_key': 'not-a-uuid'}, {'mark_value': 2147483648}]:
            with self.subTest(fields=fields):
                self.assertEqual(self.post('submissions/', self.payload(**fields)).status_code, 400)
                self.assertEqual(Mark.objects.count(), before)
                self.assertEqual(MarkSubmission.objects.count(), 0)
        with patch.object(Mark.objects, 'bulk_create', side_effect=IntegrityError('synthetic write failure')):
            self.assertEqual(self.post('submissions/', self.payload()).status_code, 503)
        self.assertEqual(Mark.objects.count(), before)
        self.assertEqual(MarkSubmission.objects.count(), 0)

    def test_actor_roles_and_csrf_are_enforced(self):
        for actor in [self.t1, self.r, self.b]:
            self.assertEqual(self.post('submissions/', self.payload(), actor).status_code, 403)
        for actor in [self.a, self.t1, self.b]:
            self.assertEqual(self.post(f'{self.m.pk}/decision/', {'action': 'approve', 'revision': 'forged'}, actor).status_code, 403)
            self.client.force_login(actor)
            self.assertEqual(self.client.get(f'/api/v1/new-members/{self.m.pk}/').status_code, 403)
        client = csrf_client()
        client.force_login(self.a)
        client.get('/api/v1/session/')
        response = client.post('/api/v1/new-members/submissions/', self.payload(), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(MarkSubmission.objects.count(), 0)

    def test_pending_decisions_repeat_without_overwriting_and_stale_edit_conflicts(self):
        self.client.force_login(self.r)
        original = self.client.get(f'/api/v1/new-members/{self.m.pk}/').json()
        body = {'action': 'approve', 'revision': original['revision']}
        approved = self.post(f'{self.m.pk}/decision/', body, self.r)
        self.assertEqual(approved.status_code, 200)
        self.m.refresh_from_db()
        audit = self.mark_state(self.m)
        self.assertEqual(self.post(f'{self.m.pk}/decision/', body, self.r).status_code, 200)
        self.assertEqual(self.mark_state(self.m), audit)
        self.assertEqual(self.post(f'{self.m.pk}/decision/', {**body, 'action': 'deny'}, self.r).status_code, 409)
        edit = {'target_user': self.t2.pk, 'mark_reason': 'Edited reason', 'mark_value': 0,
                'mark_date': '2026-10-17', 'revision': original['revision']}
        response = self.client.patch(f'/api/v1/new-members/{self.m.pk}/', edit, content_type='application/json')
        self.assertEqual(response.status_code, 409)
        edit['revision'] = approved.json()['revision']
        response = self.client.patch(f'/api/v1/new-members/{self.m.pk}/', edit, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.m.refresh_from_db()
        self.assertEqual((self.m.target_user_id, self.m.mark_value, self.m.mark_approval_status), (self.t2.pk, 0, 'approved'))
        self.assertEqual((self.m.requesting_user_id, self.m.mark_approver_name, self.m.mark_submission_approval_date),
                         (audit['requesting_user_id'], audit['mark_approver_name'], audit['mark_submission_approval_date']))
        self.assertEqual(self.m.last_edited_by_id, self.r.pk)
        self.assertEqual(self.client.patch(f'/api/v1/new-members/{self.m.pk}/', edit, content_type='application/json').status_code, 409)

    def test_autoapproval_and_educator_revoke_have_separate_rules(self):
        self.a.brother_profile.roles.add(self.r.brother_profile.roles.get(name='NM_BOARD'))
        response = self.post('submissions/', self.payload(mark_value=0))
        self.assertEqual(response.status_code, 201)
        row = response.json()[0]
        self.assertEqual((row['status'], row['reviewed_by']), ('approved', 'Alex Able'))
        self.assertEqual(self.post(f"{row['id']}/revoke/", {'revision': row['revision']}, self.a).status_code, 403)
        educator = self.user('educator', ('NM_BOARD', 'NME'))
        revoked = self.post(f"{row['id']}/revoke/", {'revision': row['revision']}, educator)
        self.assertEqual(revoked.status_code, 200)
        self.assertEqual((revoked.json()['status'], revoked.json()['reviewed_by'], revoked.json()['edited_by']),
                         ('denied', 'Educator Example', 'Educator Example'))
        self.assertEqual(self.post(f"{row['id']}/revoke/", {'revision': row['revision']}, educator).json(), revoked.json())

    def test_history_scope_unknown_actions_and_legacy_permission_affordance(self):
        self.client.force_login(self.t1)
        self.assertEqual(self.client.get(f'/api/v1/new-members/history/{self.t1.pk}/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/v1/new-members/history/{self.t2.pk}/').status_code, 403)
        self.client.force_login(self.a)
        self.assertEqual(self.client.get(f'/api/v1/new-members/history/{self.t2.pk}/').status_code, 200)
        legacy = self.client.get('/newmember/marks/')
        self.assertNotContains(legacy, 'Review Pending Marks')
        self.assertContains(legacy, 'Submit Marks')
        before = self.mark_state(self.m)
        self.assertEqual(self.post(f'{self.m.pk}/decision/', {'action': 'unknown', 'revision': 'unknown'}, self.r).status_code, 400)
        self.assertEqual(self.mark_state(self.m), before)

    def test_export_separates_same_named_people_and_writes_literal_text(self):
        self.t2.brother_profile.firstName = self.t1.brother_profile.firstName
        self.t2.brother_profile.lastName = self.t1.brother_profile.lastName
        self.t2.brother_profile.save()
        self.mark(self.a, self.t1, status='approved', value=3, title='=1+1')
        self.mark(self.a, self.t2, status='approved', value=-2, title='+SUM(1,2)')
        self.client.force_login(self.a)
        response = self.client.get('/api/v1/new-members/export/?pclass=Current')
        self.assertEqual(response.status_code, 200)
        sheet = load_workbook(BytesIO(response.content), data_only=False).active
        self.assertNotEqual(sheet['A1'].value, sheet['F1'].value)
        self.assertEqual(sheet['C4'].data_type, 's')
        self.assertEqual(sheet['H4'].data_type, 's')
        self.assertNotEqual(sheet['A2'].value, sheet['F2'].value)
        self.client.force_login(self.t1)
        self.assertEqual(self.client.get('/api/v1/new-members/export/?pclass=Alpha').status_code, 403)
        with patch('NEWMEMBER.exports.Workbook.save', side_effect=OSError('synthetic')):
            self.assertEqual(self.client.get('/api/v1/new-members/export/?pclass=Current').status_code, 503)
