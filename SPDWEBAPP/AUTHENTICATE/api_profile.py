"""Caller-only profile read contract; no arbitrary user selector or profile writes."""
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from SPDWEBAPP_CORE.api.links import safe_public_url
from .api_session import member_profile, SessionRoleSerializer


class OwnProfileSerializer(serializers.Serializer):
    display_name = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    username = serializers.CharField()
    email = serializers.CharField(allow_blank=True)
    hometown = serializers.CharField(allow_null=True, allow_blank=True)
    pclass = serializers.CharField(allow_null=True, allow_blank=True)
    majors = serializers.ListField(child=serializers.CharField())
    roles = SessionRoleSerializer(many=True)
    image = serializers.CharField(allow_null=True)


class OwnProfileView(APIView):
    """Resolve only request.user, regardless of unrecognized user/profile query parameters."""
    @extend_schema(responses=OwnProfileSerializer)
    def get(self, request):
        profile = member_profile(request.user)
        if profile is None:
            raise PermissionDenied('Your member profile is unavailable.')
        data = {
            'display_name': f'{profile.firstName or ""} {profile.lastName or ""}'.strip() or 'Member',
            'first_name': profile.firstName or '', 'last_name': profile.lastName or '',
            'username': request.user.username, 'email': request.user.email,
            'hometown': profile.hometown, 'pclass': profile.pclass,
            'majors': [major.name for major in profile.majors.all()],
            'roles': [{'code': role.name, 'label': role.get_name_display()} for role in profile.roles.all()],
            'image': safe_public_url(profile.profileImage.url) if profile.profileImage else None,
        }
        return Response(OwnProfileSerializer(data).data, headers={'Cache-Control': 'no-store'})
