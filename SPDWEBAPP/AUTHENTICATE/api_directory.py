"""Authenticated directory read model matching existing current/alumni roster sets."""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from SPDWEBAPP_CORE.api.links import safe_public_url
from .api_session import member_profile, SessionRoleSerializer
from .models import Brother_Profile


class DirectoryMemberSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    display_name = serializers.CharField()
    roles = SessionRoleSerializer(many=True)
    majors = serializers.ListField(child=serializers.CharField())
    pclass = serializers.CharField(allow_null=True, allow_blank=True)
    image = serializers.CharField(allow_null=True)


class DirectorySerializer(serializers.Serializer):
    group = serializers.ChoiceField(choices=['current', 'alumni'])
    members = DirectoryMemberSerializer(many=True)


class DirectoryView(APIView):
    """Keep contact/User fields out of roster data; validate group before reading records."""
    @extend_schema(parameters=[OpenApiParameter('group', str, enum=['current', 'alumni'])], responses=DirectorySerializer)
    def get(self, request):
        if member_profile(request.user) is None:
            raise PermissionDenied('Your member profile is unavailable.')
        group = request.query_params.get('group', 'current')
        if group not in {'current', 'alumni'}:
            raise ValidationError({'group': 'Choose current or alumni.'})
        profiles = Brother_Profile.objects.all()
        profiles = profiles.filter(roles__name='ALUMNI') if group == 'alumni' else profiles.exclude(roles__name='ALUMNI')
        profiles = profiles.order_by('lastName', 'pk').distinct().prefetch_related('roles', 'majors')
        members = [{
            'id': profile.pk,
            'display_name': f'{profile.firstName or ""} {profile.lastName or ""}'.strip() or 'Chapter member',
            'roles': [{'code': role.name, 'label': role.get_name_display()} for role in profile.roles.all()],
            'majors': [major.name for major in profile.majors.all()],
            'pclass': profile.pclass,
            'image': safe_public_url(profile.profileImage.url) if profile.profileImage else None,
        } for profile in profiles]
        return Response(DirectorySerializer({'group': group, 'members': members}).data,
                        headers={'Cache-Control': 'no-store'})
