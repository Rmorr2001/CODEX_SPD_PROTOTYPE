"""Caller-only session presentation contract; session cookies remain server-owned."""
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .access import member_profile




def member_identity(profile):
    """Whitelisted caller display information and navigation capabilities, never credentials."""
    roles = list(profile.roles.all())
    codes = {role.name for role in roles}
    return {
        'display_name': f'{profile.firstName or ""} {profile.lastName or ""}'.strip() or 'Member',
        'roles': [{'code': role.name, 'label': role.get_name_display()} for role in roles],
        'capabilities': {
            'dashboard': 'NEW_MEMBER' not in codes,
            'members': True, 'profile': True,
            'polls': 'ACTIVE' in codes, 'service_hours': 'ACTIVE' in codes,
            'new_members': bool(codes & {'ACTIVE', 'NEW_MEMBER'}),
        },
    }


class SessionRoleSerializer(serializers.Serializer):
    code = serializers.CharField()
    label = serializers.CharField()


class NavigationCapabilitiesSerializer(serializers.Serializer):
    dashboard = serializers.BooleanField()
    members = serializers.BooleanField()
    profile = serializers.BooleanField()
    polls = serializers.BooleanField()
    service_hours = serializers.BooleanField()
    new_members = serializers.BooleanField()


class SessionMemberSerializer(serializers.Serializer):
    display_name = serializers.CharField()
    roles = SessionRoleSerializer(many=True)
    capabilities = NavigationCapabilitiesSerializer()


class SessionSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()
    profile_available = serializers.BooleanField()
    demo_enabled = serializers.BooleanField()
    landing_path = serializers.CharField()
    member = SessionMemberSerializer(allow_null=True)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class SessionView(APIView):
    """Public session status; identity is returned only for its authenticated caller."""
    permission_classes = [AllowAny]

    @extend_schema(responses=SessionSerializer)
    def get(self, request):
        profile = member_profile(request.user)
        member = member_identity(profile) if profile else None
        path = '/app/login'
        if member:
            path = '/app/dashboard' if member['capabilities']['dashboard'] else '/app/new-members'
        data = {'authenticated': request.user.is_authenticated, 'profile_available': profile is not None,
                'demo_enabled': bool(getattr(settings, 'DEMO_MODE', False)),
                'landing_path': path, 'member': member}
        return Response(SessionSerializer(data).data, headers={'Cache-Control': 'no-store'})
