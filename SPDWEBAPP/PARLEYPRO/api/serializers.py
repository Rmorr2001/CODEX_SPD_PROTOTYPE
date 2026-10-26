"""Explicit JSON contracts for polling reads and commands."""
from rest_framework import serializers


class MotionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    started_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField(allow_null=True)
    aye = serializers.IntegerField(min_value=0)
    nay = serializers.IntegerField(min_value=0)


class DecisionsSerializer(serializers.Serializer):
    current = MotionSerializer(allow_null=True)
    closed = MotionSerializer(many=True)
    can_manage = serializers.BooleanField()
    own_choice = serializers.CharField(allow_null=True)



class CreateInput(serializers.Serializer):
    title = serializers.CharField(max_length=200)


class BallotInput(serializers.Serializer):
    choice = serializers.ChoiceField(choices=['Aye', 'Nay'])


class PollDetailSerializer(MotionSerializer):
    own_choice = serializers.CharField(allow_null=True)
    can_manage = serializers.BooleanField()


