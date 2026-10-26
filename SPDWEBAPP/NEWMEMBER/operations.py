"""Shared, transport-independent marks validation, authorization and atomic transitions."""
import hashlib
import json
import uuid
from django import forms
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from AUTHENTICATE.access import require_domain_roles, member_profile
from AUTHENTICATE.models import Brother_Profile
from SPDWEBAPP_CORE.domain import Conflict
from .models import NewMember_Mark_Event_and_Request as Mark, MarkSubmission


def roles_for(user):
    profile = require_domain_roles(user)
    return profile, {role.name for role in profile.roles.all()}


def require_marks(user):
    profile, roles = roles_for(user)
    if not roles & {'ACTIVE', 'NEW_MEMBER', 'NM_BOARD'}:
        raise PermissionDenied('Marks are unavailable for your current role.')
    return profile, roles


def name_for(user):
    profile = member_profile(user)
    return f'{profile.firstName or ""} {profile.lastName or ""}'.strip() if profile else user.username


def eligible_members():
    return Brother_Profile.objects.filter(roles__name='NEW_MEMBER').select_related('user').order_by('lastName', 'firstName', 'user_id').distinct()


class MarkFields(forms.Form):
    mark_reason = forms.CharField(max_length=100)
    mark_value = forms.IntegerField(min_value=-2147483648, max_value=2147483647)
    mark_date = forms.DateField()


def clean_fields(data):
    form = MarkFields(data)
    if not form.is_valid():
        raise ValidationError({key: list(errors) for key, errors in form.errors.items()})
    return {'mark_event_title': form.cleaned_data['mark_reason'],
            'mark_value': form.cleaned_data['mark_value'], 'mark_event_date': form.cleaned_data['mark_date']}


def clean_targets(values):
    if not isinstance(values, (list, tuple)) or not values:
        raise ValidationError({'target_users': 'Select at least one current new member.'})
    try:
        if any(isinstance(value, bool) or str(value).strip() != str(int(value)) for value in values):
            raise ValueError
        ids = [int(value) for value in values]
    except (ValueError, TypeError):
        raise ValidationError({'target_users': 'Select valid recipients.'})
    if len(set(ids)) != len(ids) or set(ids) != set(eligible_members().filter(user_id__in=ids).values_list('user_id', flat=True)):
        raise ValidationError({'target_users': 'Select distinct current new members.'})
    return sorted(ids)


def revision(mark):
    """Opaque state comparison token; neither a credential nor a permission grant."""
    values = [str(getattr(mark, field.attname)) for field in mark._meta.concrete_fields]
    return hashlib.sha256(json.dumps(values).encode()).hexdigest()


@transaction.atomic
def submit_marks(user, targets, data, request_key=None):
    require_domain_roles(user, 'ACTIVE')
    ids, fields = clean_targets(targets), clean_fields(data)
    try:
        key = uuid.UUID(str(request_key)) if request_key else uuid.uuid4()
    except (ValueError, TypeError, AttributeError):
        raise ValidationError({'request_key': 'Invalid submission key.'})
    signature = hashlib.sha256(json.dumps([ids, fields], default=str, sort_keys=True).encode()).hexdigest()
    receipt, created = MarkSubmission.objects.get_or_create(requester=user, request_key=key, defaults={'fingerprint': signature})
    if not created:
        if receipt.fingerprint != signature:
            raise Conflict('This submission key already belongs to different marks. Start a new form.')
        return list(receipt.marks.order_by('target_user_id'))
    _, roles = roles_for(user)
    audit = {'mark_approval_status': 'approved', 'mark_approver_name': name_for(user),
             'mark_submission_approval_date': timezone.now()} if 'NM_BOARD' in roles else {}
    return Mark.objects.bulk_create([Mark(requesting_user=user, target_user_id=target, submission=receipt, **fields, **audit) for target in ids])


def check_revision(mark, expected):
    if expected and revision(mark) != expected:
        raise Conflict('This mark changed. Reload it before saving.')


@transaction.atomic
def decide_mark(user, mark_id, action, expected=None):
    require_domain_roles(user, 'NM_BOARD')
    if action not in {'approve', 'deny'}:
        raise ValidationError({'action': 'Choose approve or deny.'})
    mark = get_object_or_404(Mark.objects.select_for_update(), pk=mark_id)
    desired = 'approved' if action == 'approve' else 'denied'
    if mark.mark_approval_status == desired:
        return mark  # Duplicate acknowledgement must not rewrite decision attribution/time.
    check_revision(mark, expected)
    if mark.mark_approval_status != 'requested':
        raise Conflict('This request has already been reviewed. Refresh requests.')
    mark.mark_approval_status = desired
    mark.mark_approver_name = name_for(user)
    mark.mark_submission_approval_date = timezone.now()
    mark.save(update_fields=['mark_approval_status', 'mark_approver_name', 'mark_submission_approval_date'])
    return mark


@transaction.atomic
def edit_mark(user, mark_id, data, expected=None):
    require_domain_roles(user, 'NM_BOARD')
    fields = clean_fields(data)
    mark = get_object_or_404(Mark.objects.select_for_update(), pk=mark_id)
    check_revision(mark, expected)
    target = data.get('target_user', mark.target_user_id)
    ids = clean_targets([target])
    for key, value in fields.items():
        setattr(mark, key, value)
    mark.target_user_id = ids[0]
    mark.last_edited_by, mark.last_edited_at = user, timezone.now()
    mark.save(update_fields=[*fields, 'target_user', 'last_edited_by', 'last_edited_at'])
    return mark


@transaction.atomic
def revoke_mark(user, mark_id, expected=None):
    require_domain_roles(user, 'NM_BOARD', 'NME')
    mark = get_object_or_404(Mark.objects.select_for_update(), pk=mark_id)
    if mark.mark_approval_status == 'denied':
        return mark
    check_revision(mark, expected)
    mark.mark_approval_status, mark.mark_approver_name = 'denied', name_for(user)
    mark.mark_submission_approval_date = timezone.now()
    mark.last_edited_by, mark.last_edited_at = user, timezone.now()
    mark.save(update_fields=['mark_approval_status', 'mark_approver_name', 'mark_submission_approval_date', 'last_edited_by', 'last_edited_at'])
    return mark


def history_target(user, target_id):
    _, roles = require_marks(user)
    if 'NEW_MEMBER' in roles and user.pk != target_id and 'NM_BOARD' not in roles:
        raise PermissionDenied('Only your own mark history is available.')
    return get_object_or_404(eligible_members(), user_id=target_id)
