"""Legacy HTML dispatch; business transitions live in operations.py."""
from django.contrib import messages
from django.core.exceptions import ValidationError
from SPDWEBAPP_CORE.domain import Conflict
from .operations import cast_vote, close_poll, current_poll


def count_all_current_votes(all_votes):
    aye_votes = all_votes.filter(user_vote_choice='Aye').count()
    nay_votes = all_votes.filter(user_vote_choice='Nay').count()
    return aye_votes, nay_votes


def handling_end_vote_request(request, all_votes):
    """Retain the legacy helper interface while enforcing domain authorization."""
    poll = current_poll()
    if poll:
        close_poll(request.user, poll.pk)
    else:
        from .operations import require_roles
        require_roles(request.user, 'ACTIVE', 'EXEC')


def Vote_Yes_No_or_StartANDEndVote(request, all_votes):
    """Translate exactly one HTML action; never infer a write from unknown keys."""
    actions = set(request.POST) & {'start_vote', 'end_vote', 'aye', 'nay'}
    if len(actions) != 1:
        raise ValidationError('Choose exactly one poll action.')
    action = actions.pop()
    if action == 'end_vote':
        handling_end_vote_request(request, all_votes)
    elif action != 'start_vote':
        poll = current_poll()
        if poll is None:
            raise Conflict('There is no open motion.')
        cast_vote(request.user, poll.pk, 'Aye' if action == 'aye' else 'Nay')
