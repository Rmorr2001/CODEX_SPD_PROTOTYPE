"""Service JSON mutation adapters; domain operations own policy and persistence."""
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from AUTHENTICATE.access import require_member_roles
from ..models import Philanthropy_Hours_Event_and_Request as Event
from ..operations import submit_event, decide_event, edit_event
from .reads import ServiceView
from .serializers import EventInput, DecisionInput, EventSerializer


def event_response(event, status=200):
    return Response(EventSerializer(event).data, status=status, headers={'Cache-Control': 'no-store'})


class ServiceCollectionView(ServiceView):
    @extend_schema(request=EventInput, responses={201: EventSerializer})
    def post(self, request):
        require_member_roles(request.user, 'ACTIVE')
        data = EventInput(data=request.data)
        data.is_valid(raise_exception=True)
        return event_response(submit_event(request.user, data.validated_data), 201)


class EventView(APIView):
    @extend_schema(responses=EventSerializer)
    def get(self, request, event_id):
        profile = require_member_roles(request.user)
        event = get_object_or_404(Event.objects.select_related('user__brother_profile'), pk=event_id)
        if event.user_id != request.user.pk and not profile.roles.filter(name='PHIL_CHAIR').exists():
            raise PermissionDenied('Only the owner or a chair can view this request.')
        return event_response(event)

    @extend_schema(request=EventInput, responses=EventSerializer)
    def patch(self, request, event_id):
        # An edit supplies all three editable fields; owner/status/audit are server-owned.
        require_member_roles(request.user, 'PHIL_CHAIR')
        data = EventInput(data=request.data)
        data.is_valid(raise_exception=True)
        return event_response(edit_event(request.user, event_id, data.validated_data))


class DecisionView(APIView):
    @extend_schema(request=DecisionInput, responses=EventSerializer)
    def post(self, request, event_id):
        require_member_roles(request.user, 'ACTIVE', 'PHIL_CHAIR')
        data = DecisionInput(data=request.data)
        data.is_valid(raise_exception=True)
        return event_response(decide_event(request.user, event_id, data.validated_data['action']))


class ReviewView(APIView):
    @extend_schema(responses=EventSerializer(many=True))
    def get(self, request):
        require_member_roles(request.user, 'ACTIVE', 'PHIL_CHAIR')
        events = Event.objects.filter(philanthropy_approval_status='requested').select_related(
            'user__brother_profile').order_by('-philanthropy_event_date', '-pk')
        return Response(EventSerializer(events, many=True).data, headers={'Cache-Control': 'no-store'})
