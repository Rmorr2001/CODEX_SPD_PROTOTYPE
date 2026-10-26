"""REST command adapters, distinct from legacy HTML views."""
from drf_spectacular.utils import extend_schema
from django.db import DatabaseError
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from AUTHENTICATE.access import require_member_roles
from ..models import NewMember_Mark_Event_and_Request as Mark
from ..operations import submit_marks, decide_mark, edit_mark, revoke_mark
from .serializers import SubmissionInput, EditInput, MarkDecisionInput, RevisionInput, MarkRecordSerializer, record


class DatabaseUnavailable(APIException):
    status_code = 503
    default_detail = 'The database is busy. Check current marks before retrying.'


def perform(operation, *args):
    try:
        return operation(*args)
    except DatabaseError:
        raise DatabaseUnavailable()


def result(data, status=200):
    return Response(data, status=status, headers={'Cache-Control': 'no-store'})


class SubmissionView(APIView):
    @extend_schema(request=SubmissionInput, responses={201: MarkRecordSerializer(many=True)})
    def post(self, request):
        require_member_roles(request.user, 'ACTIVE')
        data = SubmissionInput(data=request.data)
        data.is_valid(raise_exception=True)
        values = data.validated_data
        rows = perform(submit_marks, request.user, values['target_users'], values, values['request_key'])
        return result([record(mark) for mark in rows], 201)


class MarkView(APIView):
    @extend_schema(operation_id="mark_detail", responses=MarkRecordSerializer)
    def get(self, request, mark_id):
        require_member_roles(request.user, 'NM_BOARD')
        return result(record(get_object_or_404(Mark, pk=mark_id)))

    @extend_schema(request=EditInput, responses=MarkRecordSerializer)
    def patch(self, request, mark_id):
        require_member_roles(request.user, 'NM_BOARD')
        data = EditInput(data=request.data)
        data.is_valid(raise_exception=True)
        return result(record(perform(edit_mark, request.user, mark_id, data.validated_data, data.validated_data['revision'])))


class DecisionView(APIView):
    @extend_schema(request=MarkDecisionInput, responses=MarkRecordSerializer)
    def post(self, request, mark_id):
        require_member_roles(request.user, 'NM_BOARD')
        data = MarkDecisionInput(data=request.data)
        data.is_valid(raise_exception=True)
        return result(record(perform(decide_mark, request.user, mark_id, data.validated_data['action'], data.validated_data['revision'])))


class RevokeView(APIView):
    @extend_schema(request=RevisionInput, responses=MarkRecordSerializer)
    def post(self, request, mark_id):
        require_member_roles(request.user, 'NM_BOARD', 'NME')
        data = RevisionInput(data=request.data)
        data.is_valid(raise_exception=True)
        return result(record(perform(revoke_mark, request.user, mark_id, data.validated_data['revision'])))
