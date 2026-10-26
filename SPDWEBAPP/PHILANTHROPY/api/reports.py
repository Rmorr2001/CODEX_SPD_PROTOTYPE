"""Approved-history, chapter statistics and XLSX delivery adapters."""
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from AUTHENTICATE.access import require_member_roles
from AUTHENTICATE.models import Brother_Profile
from ..models import Philanthropy_Hours_Event_and_Request as Event
from ..views_functions import get_academic_year_dates, collect_philanthropy_statistics
from ..exports import export_approved_philanthropy_hours
from .reads import selected_academic_year
from .serializers import ChapterSerializer, HistorySerializer


class ChapterView(APIView):
    @extend_schema(responses=ChapterSerializer)
    def get(self, request):
        require_member_roles(request.user, 'ACTIVE')
        start, end = get_academic_year_dates(selected_academic_year(request.query_params.get('year')))
        profiles = Brother_Profile.objects.filter(roles__name='ACTIVE').distinct().select_related('user')
        rows, total, meeting_goal = collect_philanthropy_statistics(profiles, start, end)
        data = {'members': [{'user_id': row['user'].pk, 'name': row['full_name'],
                             'approved_hours': row['total_hours']} for row in rows],
                'approved_hours': total, 'average_hours': total / len(rows) if rows else 0,
                'members_meeting_goal': meeting_goal}
        return Response(ChapterSerializer(data).data, headers={'Cache-Control': 'no-store'})


class HistoryView(APIView):
    @extend_schema(operation_id='service_member_history', responses=HistorySerializer)
    def get(self, request, user_id=None):
        user_id = user_id or request.user.pk
        # Match existing ACTIVE member access to approved member histories.
        require_member_roles(request.user, 'ACTIVE')
        get_object_or_404(Brother_Profile, user_id=user_id)
        events = Event.objects.filter(user_id=user_id, philanthropy_approval_status='approved').select_related(
            'user__brother_profile').order_by('-philanthropy_event_date', '-pk')
        return Response(HistorySerializer({'events': events, 'approved_hours': sum(
            (event.philanthropy_event_hours for event in events), 0)}).data,
            headers={'Cache-Control': 'no-store'})


class ExportView(APIView):
    @extend_schema(responses={(200, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'): bytes})
    def get(self, request):
        # Preserve the existing authenticated export scope; do not silently invent chair-only policy.
        response = export_approved_philanthropy_hours(request)
        response['Cache-Control'] = 'no-store'
        return response


class OwnHistoryView(HistoryView):
    @extend_schema(operation_id='service_own_history', responses=HistorySerializer)
    def get(self, request):
        return super().get(request, request.user.pk)
