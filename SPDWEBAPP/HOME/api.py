"""Explicit public presentation contracts; never serialize member profiles here."""
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import BannerImage, RushFormLink
from SPDWEBAPP_CORE.api.links import safe_public_url




class HomeContentSerializer(serializers.Serializer):
    banner_image = serializers.CharField(allow_null=True)
    rush_interest_url = serializers.CharField(allow_null=True)


class PublicHomeView(APIView):
    """Expose only already-public banner and recruitment link; no profile data."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(responses=HomeContentSerializer, auth=[])
    def get(self, request):
        banner = BannerImage.objects.first()
        interest = RushFormLink.objects.first()
        data = {
            'banner_image': safe_public_url(banner.image.url) if banner and banner.image else None,
            'rush_interest_url': safe_public_url(interest.link) if interest else None,
        }
        return Response(HomeContentSerializer(data).data, headers={'Cache-Control': 'no-store'})
