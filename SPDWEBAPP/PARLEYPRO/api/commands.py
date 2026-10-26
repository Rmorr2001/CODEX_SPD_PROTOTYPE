"""REST voting commands; delegate validation and mutation to shared operations."""
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from AUTHENTICATE.access import require_member_roles
from ..models import Brother_votes, Vote_Poll
from ..operations import can_manage_polls, create_poll, cast_vote, close_poll
from .reads import DecisionsView, motion_data
from .serializers import CreateInput, BallotInput, PollDetailSerializer
from django.shortcuts import get_object_or_404


def poll_response(user, poll):
    """Return saved historical totals or the current global ballot snapshot."""
    if poll.Vote_Poll_End:
        aye, nay = poll.Vote_Poll_Count_Yes, poll.Vote_Poll_Count_No
    else:
        aye = Brother_votes.objects.filter(user_vote_choice='Aye').count()
        nay = Brother_votes.objects.filter(user_vote_choice='Nay').count()
    data = {**motion_data(poll, aye, nay), 'own_choice': Brother_votes.objects.filter(user=user).values_list('user_vote_choice', flat=True).first() if poll.Vote_Poll_End is None else None,
            'can_manage': can_manage_polls(user)}
    return Response(PollDetailSerializer(data).data,
                    headers={'Cache-Control': 'no-store'})


class PollCollectionView(DecisionsView):
    @extend_schema(request=CreateInput, responses={201: PollDetailSerializer})
    def post(self, request):
        require_member_roles(request.user, 'ACTIVE', 'EXEC')
        data = CreateInput(data=request.data)
        data.is_valid(raise_exception=True)
        poll = create_poll(request.user, data.validated_data['title'])
        response = poll_response(request.user, poll)
        response.status_code = 201
        return response


class PollDetailView(APIView):
    @extend_schema(responses=PollDetailSerializer)
    def get(self, request, poll_id):
        require_member_roles(request.user, 'ACTIVE')
        return poll_response(request.user, get_object_or_404(Vote_Poll, pk=poll_id))


class BallotView(APIView):
    @extend_schema(request=BallotInput, responses=PollDetailSerializer)
    def put(self, request, poll_id):
        require_member_roles(request.user, 'ACTIVE')
        data = BallotInput(data=request.data)
        data.is_valid(raise_exception=True)
        return poll_response(request.user, cast_vote(request.user, poll_id, data.validated_data['choice']))


class CloseView(APIView):
    @extend_schema(request=None, responses=PollDetailSerializer)
    def post(self, request, poll_id):
        return poll_response(request.user, close_poll(request.user, poll_id))
