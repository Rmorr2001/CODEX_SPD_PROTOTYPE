"""Read-only motion results; current vote-store totals are distinct from saved history."""
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from AUTHENTICATE.access import require_member_roles
from ..models import Brother_votes, Vote_Poll
from ..pp_functions import count_all_current_votes
from ..operations import can_manage_polls
from .serializers import MotionSerializer, DecisionsSerializer


def motion_data(poll, aye, nay):
    """Only motion metadata and aggregate tallies are public to eligible readers."""
    return {'id': poll.pk, 'title': poll.Vote_Poll_Name or 'Untitled motion',
            'started_at': poll.Vote_Poll_Start, 'ended_at': poll.Vote_Poll_End,
            'aye': aye or 0, 'nay': nay or 0}


class DecisionsView(APIView):
    """Require ACTIVE and expose no individual vote identities or ballot writes."""
    @extend_schema(operation_id='polls_list', responses=DecisionsSerializer)
    def get(self, request):
        require_member_roles(request.user, 'ACTIVE')
        current = Vote_Poll.objects.filter(Vote_Poll_End__isnull=True).order_by('-Vote_Poll_Start', '-pk').first()
        current_data = None
        if current:
            aye, nay = count_all_current_votes(Brother_votes.objects)
            current_data = motion_data(current, aye, nay)
        closed = [motion_data(poll, poll.Vote_Poll_Count_Yes, poll.Vote_Poll_Count_No)
                  for poll in Vote_Poll.objects.filter(Vote_Poll_End__isnull=False).order_by('-Vote_Poll_End', '-pk')]
        return Response(DecisionsSerializer({
            'current': current_data, 'closed': closed,
            'can_manage': can_manage_polls(request.user),
            'own_choice': Brother_votes.objects.filter(user=request.user).values_list('user_vote_choice', flat=True).first() if current else None,
        }).data, headers={'Cache-Control': 'no-store'})
