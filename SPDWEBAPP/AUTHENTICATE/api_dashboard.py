"""Authenticated dashboard presentation without inventing new chapter business rules."""
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from MISC.models import AnnouncementAlert
from SPDWEBAPP_CORE.api.links import safe_public_url
from .api_session import member_profile
from .models import DashboardLink


class AnnouncementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField()


class DashboardLinkSerializer(serializers.Serializer):
    text = serializers.CharField()
    url = serializers.CharField()


class DashboardSerializer(serializers.Serializer):
    landing_path = serializers.CharField()
    announcements = AnnouncementSerializer(many=True)
    links = DashboardLinkSerializer(many=True)


class DashboardView(APIView):
    """Honor the existing NEW_MEMBER landing rule before reading general announcements."""
    @extend_schema(responses=DashboardSerializer)
    def get(self, request):
        profile = member_profile(request.user)
        if profile is None:
            raise PermissionDenied('Your member profile is unavailable.')
        if profile.roles.filter(name='NEW_MEMBER').exists():
            data = {'landing_path': '/app/new-members', 'announcements': [], 'links': []}
        else:
            links = []
            for link in DashboardLink.objects.order_by('order', 'pk'):
                url = safe_public_url(link.link)
                if url:
                    links.append({'text': link.text, 'url': url})
            data = {'landing_path': '/app/dashboard',
                    'announcements': AnnouncementAlert.objects.filter(is_active=True).order_by('pk'),
                    'links': links}
        return Response(DashboardSerializer(data).data,
                        headers={'Cache-Control': 'no-store'})
