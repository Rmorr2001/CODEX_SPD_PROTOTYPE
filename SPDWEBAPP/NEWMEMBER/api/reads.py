"""Authorized marks options, review and history reads."""
from drf_spectacular.utils import extend_schema, OpenApiTypes, OpenApiParameter
from rest_framework.exceptions import APIException
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from AUTHENTICATE.access import require_member_roles
from ..models import NewMember_Mark_Event_and_Request as Mark
from ..operations import require_marks, eligible_members, history_target
from ..exports import export_marks, class_choices
from .serializers import record, MarkOptionsSerializer, MarkHistorySerializer, MarkRecordSerializer


class OptionsView(APIView):
    @extend_schema(responses=MarkOptionsSerializer)
    def get(self, request):
        _, roles = require_marks(request.user)
        targets = eligible_members() if roles & {'ACTIVE', 'NM_BOARD'} else []
        classes = ['Current'] if 'NEW_MEMBER' in roles else ['Current', *class_choices()]
        return Response({'targets': [{'id': member.user_id, 'name': f'{member.firstName} {member.lastName}'} for member in targets],
                         'classes': classes}, headers={'Cache-Control': 'no-store'})


class ReviewView(APIView):
    @extend_schema(responses=MarkRecordSerializer(many=True))
    def get(self, request):
        require_member_roles(request.user, 'NM_BOARD')
        marks = Mark.objects.filter(mark_approval_status='requested').select_related('requesting_user', 'target_user', 'last_edited_by').order_by('-mark_event_date', '-pk')
        return Response([record(mark) for mark in marks], headers={'Cache-Control': 'no-store'})


class HistoryView(APIView):
    @extend_schema(responses=MarkHistorySerializer)
    def get(self, request, user_id):
        target = history_target(request.user, user_id)
        marks = list(Mark.objects.filter(target_user_id=user_id, mark_approval_status='approved').select_related('requesting_user', 'target_user', 'last_edited_by').order_by('-mark_event_date', '-pk'))
        return Response({'target_id': user_id, 'target_name': f'{target.firstName} {target.lastName}',
                         'total': sum(mark.mark_value for mark in marks), 'marks': [record(mark) for mark in marks]}, headers={'Cache-Control': 'no-store'})


class ExportView(APIView):
    @extend_schema(responses=OpenApiTypes.BINARY, parameters=[OpenApiParameter("pclass", str)])
    def get(self, request):
        require_marks(request.user)
        try:
            return export_marks(request.user, request.GET.get('pclass', 'Current'))
        except (ValidationError, PermissionDenied):
            raise
        except Exception:
            error = APIException('Unable to prepare this workbook. Please retry.')
            error.status_code = 503
            raise error
