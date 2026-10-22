"""Role-specific marks reads; existing helpers remain authoritative for arithmetic."""
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from AUTHENTICATE.access import require_member_roles
from .views_functions import (
    get_new_members, calculate_member_marks, get_user_submitted_marks,
    get_personal_stats, get_active_member_analytics, get_member_mark_history,
)


class MarkSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    value = serializers.IntegerField()
    date = serializers.DateField()
    status = serializers.ChoiceField(choices=['approved', 'requested', 'denied'])


class SubmissionSerializer(MarkSerializer):
    target_name = serializers.CharField()


class PersonalSerializer(serializers.Serializer):
    total_marks = serializers.IntegerField()
    class_average = serializers.FloatField()
    standing = serializers.CharField()
    latest_mark = MarkSerializer(allow_null=True)
    history_url = serializers.CharField()
    history = MarkSerializer(many=True)


class ClassMemberSerializer(serializers.Serializer):
    display_name = serializers.CharField()
    total_marks = serializers.IntegerField()
    is_negative = serializers.BooleanField()
    history_url = serializers.CharField()


class AnalyticsSerializer(serializers.Serializer):
    total_new_members = serializers.IntegerField()
    members_in_good_standing = serializers.IntegerField()
    average_marks = serializers.FloatField()
    marks_this_week = serializers.IntegerField()
    pending_requests = serializers.IntegerField()


class MarksSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=['personal', 'active', 'review'])
    can_submit = serializers.BooleanField()
    can_review = serializers.BooleanField()
    personal = PersonalSerializer(allow_null=True)
    analytics = AnalyticsSerializer(allow_null=True)
    members = ClassMemberSerializer(many=True)
    submissions = SubmissionSerializer(many=True)


def mark_data(mark):
    """Only a caller's own approved history or own submissions may include reasons."""
    return {'id': mark.pk, 'title': mark.mark_event_title, 'value': mark.mark_value,
            'date': mark.mark_event_date, 'status': mark.mark_approval_status}


def personal_data(user):
    """Keep personal marks separate from class-wide reads, including for dual roles."""
    stats = get_personal_stats(user)
    history, _ = get_member_mark_history(user.pk)
    return {**stats, 'latest_mark': mark_data(stats['latest_mark']) if stats['latest_mark'] else None,
            'history_url': f'/newmember/history/{user.pk}/',
            'history': [mark_data(mark) for mark in history]}


def active_data(user):
    """Expose class approved totals, never other members' disciplinary reasons."""
    progress = calculate_member_marks(get_new_members())
    members = [{'display_name': item['full_name'], 'total_marks': item['total_marks'],
                'is_negative': item['is_negative'],
                'history_url': f'/newmember/history/{item["user"].pk}/'} for item in progress]
    submissions = []
    for mark in get_user_submitted_marks(user).select_related('target_user__brother_profile'):
        target = getattr(mark.target_user, 'brother_profile', None)
        name = f'{target.firstName or ""} {target.lastName or ""}'.strip() if target else 'Member'
        submissions.append({**mark_data(mark), 'target_name': name or 'Member'})
    return {'analytics': get_active_member_analytics(progress), 'members': members,
            'submissions': submissions}


class NewMemberMarksView(APIView):
    """NEW_MEMBER personal, ACTIVE class, or NM_BOARD review-only; no writes."""
    @extend_schema(responses=MarksSerializer)
    def get(self, request):
        profile = require_member_roles(request.user)
        roles = {role.name for role in profile.roles.all()}
        if not roles & {'NEW_MEMBER', 'ACTIVE', 'NM_BOARD'}:
            raise PermissionDenied('New-member tools are unavailable for your current role.')
        data = {'mode': 'review', 'can_submit': 'ACTIVE' in roles, 'can_review': 'NM_BOARD' in roles,
                'personal': None, 'analytics': None, 'members': [], 'submissions': []}
        if 'NEW_MEMBER' in roles:
            data.update(mode='personal', personal=personal_data(request.user))
        elif 'ACTIVE' in roles:
            data.update(mode='active', **active_data(request.user))
        return Response(MarksSerializer(data).data, headers={'Cache-Control': 'no-store'})
