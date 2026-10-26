"""Single-open chapter voting, shared by HTML and REST request adapters."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from AUTHENTICATE.access import require_domain_roles as require_roles
from SPDWEBAPP_CORE.domain import Conflict
from .forms import VotePollForm
from .models import Brother_votes, Vote_Poll, PollWorkflowLock


def can_manage_polls(user):
    """Presentation capability uses the same ALL-role boundary as create/close."""
    try:
        require_roles(user, 'ACTIVE', 'EXEC')
    except PermissionDenied:
        return False
    return True


def lock_workflow():
    # A real UPDATE serializes even when no poll is open, including on SQLite.
    # PostgreSQL holds this row lock until the enclosing transaction commits.
    PollWorkflowLock.objects.get_or_create(pk=1)
    PollWorkflowLock.objects.filter(pk=1).update(version=F('version') + 1)


def current_poll():
    return Vote_Poll.objects.filter(Vote_Poll_End__isnull=True).order_by('-Vote_Poll_Start', '-pk').first()


@transaction.atomic
def create_poll(user, title):
    """Open one motion; reject overlapping creation without resetting any choices."""
    require_roles(user, 'ACTIVE', 'EXEC')
    form = VotePollForm({'Vote_Poll_Name': title})
    if not form.is_valid():
        raise ValidationError({'title': form.errors['Vote_Poll_Name']})
    lock_workflow()
    if current_poll():
        raise Conflict('Close the current motion before opening another.')
    poll = form.save(commit=False)
    poll.created_by = user
    poll.save()
    return poll


@transaction.atomic
def cast_vote(user, poll_id, choice):
    """Replace only the caller's ballot, rejecting a closed/stale target."""
    require_roles(user, 'ACTIVE')
    if choice not in {'Aye', 'Nay'}:
        raise ValidationError({'choice': 'Choose Aye or Nay.'})
    lock_workflow()
    poll = get_object_or_404(Vote_Poll, pk=poll_id)
    if poll.Vote_Poll_End is not None or poll != current_poll():
        raise Conflict('This motion is no longer open. Refresh before voting.')
    Brother_votes.objects.update_or_create(user=user, defaults={'user_vote_choice': choice})
    return poll


@transaction.atomic
def close_poll(user, poll_id):
    """Snapshot results and reset ballots atomically; only ACTIVE+EXEC may close."""
    require_roles(user, 'ACTIVE', 'EXEC')
    lock_workflow()
    poll = get_object_or_404(Vote_Poll, pk=poll_id)
    if poll.Vote_Poll_End is not None:
        return poll  # A repeated close cannot rewrite the saved result or another poll.
    if poll != current_poll():
        raise Conflict('Refresh before closing the current motion.')
    votes = Brother_votes.objects
    poll.Vote_Poll_Count_Yes = votes.filter(user_vote_choice='Aye').count()
    poll.Vote_Poll_Count_No = votes.filter(user_vote_choice='Nay').count()
    poll.Vote_Poll_End = timezone.now()
    poll.save(update_fields=['Vote_Poll_Count_Yes', 'Vote_Poll_Count_No', 'Vote_Poll_End'])
    votes.update(user_vote_choice='No Vote')
    return poll
