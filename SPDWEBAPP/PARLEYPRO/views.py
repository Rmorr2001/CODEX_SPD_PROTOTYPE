"""Legacy HTML adapters; shared operations also serve the React REST interface."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from SPDWEBAPP_CORE.domain import Conflict
from .forms import VotePollForm
from .models import Brother_votes, Vote_Poll
from .operations import create_poll, current_poll
from .pp_decorators import requires_role
from .pp_functions import count_all_current_votes, Vote_Yes_No_or_StartANDEndVote


@requires_role('ACTIVE')
@login_required
def poll_index(request):
    all_votes = Brother_votes.objects
    if request.method == 'POST':
        actions = set(request.POST) & {'start_vote', 'end_vote', 'aye', 'nay'}
        if actions == {'start_vote'}:
            return redirect('start_vote')
        try:
            Vote_Yes_No_or_StartANDEndVote(request, all_votes)
        except ValidationError as exc:
            messages.error(request, '; '.join(exc.messages))
        except Conflict as exc:
            messages.error(request, str(exc))
        except DatabaseError:
            messages.error(request, 'Unable to save this action. Refresh before retrying.')
    aye_votes, nay_votes = count_all_current_votes(all_votes)
    context = {
        'nay_votes': nay_votes,
        'aye_votes': aye_votes,
        'current_poll': current_poll(),
    }
    return render(request, 'poll_index.html', context)


@login_required
@requires_role('EXEC', 'ACTIVE')
def start_vote(request):
    form = VotePollForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            create_poll(request.user, form.cleaned_data['Vote_Poll_Name'])
            return redirect('poll')
        except Conflict as exc:
            form.add_error(None, str(exc))
        except DatabaseError:
            form.add_error(None, 'Unable to open the motion. Refresh before retrying.')
    return render(request, 'create_poll.html', {'form': form})


@requires_role('ACTIVE')
@login_required
def past_polls(request):
    polls = Vote_Poll.objects.filter(Vote_Poll_End__isnull=False).order_by('-Vote_Poll_End')
    return render(request, 'past_polls.html', {'past_polls': polls})


@login_required
def poll_results(request):
    """Preserve the legacy login-only aggregate audience pending policy clarification."""
    aye, nay = count_all_current_votes(Brother_votes.objects)
    return JsonResponse({'aye_votes': aye, 'nay_votes': nay}, headers={'Cache-Control': 'no-store'})
