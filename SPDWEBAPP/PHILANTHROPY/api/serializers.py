"""Explicit JSON contracts for service transactions and chapter reporting."""
from rest_framework import serializers
from decimal import Decimal
from ..models import Philanthropy_Hours_Event_and_Request as Event


class EventInput(serializers.Serializer):
    event_title = serializers.CharField(max_length=100)
    hours = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.5"))
    event_date = serializers.DateField()


class DecisionInput(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'deny'])


class EventSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='philanthropy_event_title')
    date = serializers.DateField(source='philanthropy_event_date')
    hours = serializers.DecimalField(source='philanthropy_event_hours', max_digits=10,
                                     decimal_places=2, coerce_to_string=False)
    status = serializers.CharField(source='philanthropy_approval_status')
    owner_id = serializers.IntegerField(source='user_id')
    owner_name = serializers.SerializerMethodField()
    reviewed_by = serializers.CharField(source='philanthropy_event_approver_name', allow_null=True)
    reviewed_at = serializers.DateTimeField(source='philanthropy_event_submission_approval_date', allow_null=True)
    edited_at = serializers.DateTimeField(source='last_edited_at', allow_null=True)

    def get_owner_name(self, obj) -> str:
        profile = getattr(obj.user, 'brother_profile', None)
        return f'{profile.firstName or ""} {profile.lastName or ""}'.strip() if profile else 'Member'

    class Meta:
        model = Event
        fields = ['id', 'title', 'date', 'hours', 'status', 'owner_id', 'owner_name',
                  'reviewed_by', 'reviewed_at', 'edited_at']


class ProgressSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    approved_hours = serializers.FloatField()


class ChapterSerializer(serializers.Serializer):
    members = ProgressSerializer(many=True)
    approved_hours = serializers.FloatField()
    average_hours = serializers.FloatField()
    members_meeting_goal = serializers.IntegerField()


class HistorySerializer(serializers.Serializer):
    events = EventSerializer(many=True)
    approved_hours = serializers.FloatField()


class ReviewEventSerializer(EventSerializer):
    """Expose decision availability only in the already role-authorized review queue."""
    can_decide = serializers.SerializerMethodField()

    def get_can_decide(self, obj) -> bool:
        from ..operations import decision_is_available
        request = self.context.get('request')
        return bool(request and decision_is_available(request.user.pk, obj))

    class Meta(EventSerializer.Meta):
        fields = [*EventSerializer.Meta.fields, 'can_decide']
