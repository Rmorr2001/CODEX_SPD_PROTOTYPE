"""Shared service-hour validation and transitions for HTML and REST callers."""
from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from AUTHENTICATE.access import require_domain_roles as require_roles
from SPDWEBAPP_CORE.domain import Conflict
from .models import Philanthropy_Hours_Event_and_Request as Event


class ServiceForm(forms.Form):
    event_title = forms.CharField(max_length=100)
    hours = forms.DecimalField(min_value=Decimal('0.5'), max_digits=10, decimal_places=2, error_messages={'min_value': 'Must request at least 0.5 hours.'})
    event_date = forms.DateField()


def service_fields(data):
    form = ServiceForm(data)
    if not form.is_valid():
        raise ValidationError({key: list(value) for key, value in form.errors.items()})
    return {'philanthropy_event_title': form.cleaned_data['event_title'],
            'philanthropy_event_hours': form.cleaned_data['hours'],
            'philanthropy_event_date': form.cleaned_data['event_date']}


@transaction.atomic
def submit_event(user, data):
    """Create a pending request owned by the session user, ignoring forged audit fields."""
    require_roles(user, 'ACTIVE')
    return Event.objects.create(user=user, **service_fields(data))


@transaction.atomic
def decide_event(user, event_id, action):
    """Decide a pending request; exceptional self/reversal policies remain unresolved."""
    profile = require_roles(user, 'ACTIVE', 'PHIL_CHAIR')
    if action not in {'approve', 'deny'}:
        raise ValidationError({'action': 'Choose approve or deny.'})
    event = get_object_or_404(Event, pk=event_id)
    # Conditional update makes competing decisions observable without overwriting audit.
    if event.user_id == user.pk:
        raise Conflict('Self-review is unavailable pending an explicit chapter policy.')
    if event.philanthropy_approval_status != 'requested':
        raise Conflict('This request has already been reviewed. Refresh the queue.')
    changed = Event.objects.filter(pk=event.pk, philanthropy_approval_status='requested').update(
        philanthropy_approval_status='approved' if action == 'approve' else 'denied',
        philanthropy_event_approver_name=f'{profile.firstName} {profile.lastName}',
        philanthropy_event_submission_approval_date=timezone.now())
    if not changed:
        raise Conflict('Another reviewer already decided this request.')
    event.refresh_from_db()
    return event


@transaction.atomic
def edit_event(user, event_id, data):
    """Chair edits retain status/decision audit, matching the established HTML workflow."""
    require_roles(user, 'PHIL_CHAIR')
    fields = service_fields(data)
    event = get_object_or_404(Event.objects.select_for_update(), pk=event_id)
    for key, value in fields.items():
        setattr(event, key, value)
    event.last_edited_by, event.last_edited_at = user, timezone.now()
    event.save(update_fields=[*fields, 'last_edited_by', 'last_edited_at'])
    return event
