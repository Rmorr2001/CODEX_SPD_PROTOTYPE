"""Explicit marks command and record contracts; domain operations validate business inputs."""
from rest_framework import serializers
from ..operations import name_for, revision
from .dashboard import mark_data


class SubmissionInput(serializers.Serializer):
    target_users = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    mark_reason = serializers.CharField(max_length=100)
    mark_value = serializers.IntegerField(min_value=-2147483648, max_value=2147483647)
    mark_date = serializers.DateField()
    request_key = serializers.UUIDField()


class EditInput(serializers.Serializer):
    target_user = serializers.IntegerField()
    mark_reason = serializers.CharField(max_length=100)
    mark_value = serializers.IntegerField(min_value=-2147483648, max_value=2147483647)
    mark_date = serializers.DateField()
    revision = serializers.CharField()


class MarkDecisionInput(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'deny'])
    revision = serializers.CharField()


class RevisionInput(serializers.Serializer):
    revision = serializers.CharField()


def record(mark):
    return {**mark_data(mark), 'requester_id': mark.requesting_user_id,
            'requester_name': name_for(mark.requesting_user),
            'target_id': mark.target_user_id, 'target_name': name_for(mark.target_user),
            'reviewed_by': mark.mark_approver_name, 'reviewed_at': mark.mark_submission_approval_date,
            'edited_by': name_for(mark.last_edited_by) if mark.last_edited_by_id else None,
            'edited_at': mark.last_edited_at, 'revision': revision(mark)}


class MarkRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    value = serializers.IntegerField()
    date = serializers.DateField()
    status = serializers.ChoiceField(choices=['requested', 'approved', 'denied'])
    requester_id = serializers.IntegerField()
    requester_name = serializers.CharField()
    target_id = serializers.IntegerField()
    target_name = serializers.CharField()
    reviewed_by = serializers.CharField(allow_null=True)
    reviewed_at = serializers.DateTimeField(allow_null=True)
    edited_by = serializers.CharField(allow_null=True)
    edited_at = serializers.DateTimeField(allow_null=True)
    revision = serializers.CharField()


class TargetSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class MarkOptionsSerializer(serializers.Serializer):
    targets = TargetSerializer(many=True)
    classes = serializers.ListField(child=serializers.CharField())


class MarkHistorySerializer(serializers.Serializer):
    target_id = serializers.IntegerField()
    target_name = serializers.CharField()
    total = serializers.IntegerField()
    marks = MarkRecordSerializer(many=True)
