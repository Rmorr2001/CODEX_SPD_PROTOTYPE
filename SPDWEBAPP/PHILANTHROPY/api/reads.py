"""Own service-hours reads preserve existing academic-year and stored-hours behavior."""
import re
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from AUTHENTICATE.access import require_member_roles
from ..models import Philanthropy_Hours_Event_and_Request
from ..views_functions import get_academic_year_dates, get_available_academic_years, get_user_events_and_total_hours


def selected_academic_year(value):
    """Accept four-digit years in a bounded date-safe range; default to current helper year."""
    if value is None:
        return get_available_academic_years()[0]
    if not re.fullmatch(r'[0-9]{4}', value):
        raise ValidationError({'year': 'Use a four-digit academic-year starting year.'})
    year = int(value)
    if not 1900 <= year <= timezone.now().year + 1:
        raise ValidationError({'year': 'Academic year is outside the supported range.'})
    return year


class ServiceEventSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    date = serializers.DateField()
    hours = serializers.FloatField()
    status = serializers.ChoiceField(choices=Philanthropy_Hours_Event_and_Request.STATUS_CHOICES)


class ServiceSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    available_years = serializers.ListField(child=serializers.IntegerField())
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    approved_hours = serializers.FloatField()
    can_review = serializers.BooleanField()
    history_url = serializers.CharField()
    events = ServiceEventSerializer(many=True)


class ServiceView(APIView):
    """Read only the caller's events and approved totals; ACTIVE gates all domain queries."""
    @extend_schema(operation_id='service_list', parameters=[OpenApiParameter('year', int, description='Academic-year starting year')], responses=ServiceSerializer)
    def get(self, request):
        profile = require_member_roles(request.user, 'ACTIVE')
        year = selected_academic_year(request.query_params.get('year'))
        start, end = get_academic_year_dates(year)
        events, approved_hours = get_user_events_and_total_hours(request, start, end)
        years = sorted(set(get_available_academic_years()) | {year}, reverse=True)
        data = {'year': year, 'available_years': years, 'start_date': start, 'end_date': end,
                'approved_hours': approved_hours, 'can_review': profile.roles.filter(name='PHIL_CHAIR').exists(),
                'history_url': f'/philanthropy/brother/{request.user.pk}/',
                'events': [{'id': event.pk, 'title': event.philanthropy_event_title,
                            'date': event.philanthropy_event_date, 'hours': event.philanthropy_event_hours,
                            'status': event.philanthropy_approval_status} for event in events]}
        return Response(ServiceSerializer(data).data, headers={'Cache-Control': 'no-store'})
