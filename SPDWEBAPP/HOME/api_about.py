"""Public chapter read model, matching the existing executive-board display order."""
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from AUTHENTICATE.models import Brother_Profile
from .api import safe_public_url

# Mirrors HOME.views.executive_board; these are display positions, not new permissions.
EXECUTIVE_POSITIONS = (
    ('PRESIDENT', 'President'), ('INT_VP', 'Internal Vice President'),
    ('EXT_VP', 'External Vice President'), ('AFFAIRS_DIRECTOR', 'Director of Chapter Affairs'),
    ('BUSINESS_MGR', 'Director of Business'), ('RECRUITMENT_CHAIR', 'Director of Recruitment'),
    ('PHIL_CHAIR', 'Director of Philanthropy'), ('RISK_MGR', 'Director of Risk Management'),
    ('SOCIAL_CHAIR', 'Director of Social Affairs'),
)


def public_executives():
    """Return only public card fields; a multi-role member appears in each position."""
    profiles = list(Brother_Profile.objects.filter(
        roles__name__in=[code for code, _ in EXECUTIVE_POSITIONS]
    ).distinct().prefetch_related('roles'))
    cards = []
    for role_code, display in EXECUTIVE_POSITIONS:
        for profile in profiles:
            if any(role.name == role_code for role in profile.roles.all()):
                cards.append({
                    'name': f'{profile.firstName or ""} {profile.lastName or ""}'.strip() or 'Chapter member',
                    'position': display,
                    'image': safe_public_url(profile.profileImage.url) if profile.profileImage else None,
                })
    return cards


class ExecutiveCardSerializer(serializers.Serializer):
    name = serializers.CharField()
    position = serializers.CharField()
    image = serializers.CharField(allow_null=True)


class AboutContentSerializer(serializers.Serializer):
    active_count = serializers.IntegerField(min_value=0)
    executives = ExecutiveCardSerializer(many=True)


class PublicAboutView(APIView):
    """Expose chapter counts and already-public leaders without contact fields."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(responses=AboutContentSerializer, auth=[])
    def get(self, request):
        data = {
            'active_count': Brother_Profile.objects.filter(roles__name='ACTIVE').distinct().count(),
            'executives': public_executives(),
        }
        return Response(AboutContentSerializer(data).data, headers={'Cache-Control': 'no-store'})
