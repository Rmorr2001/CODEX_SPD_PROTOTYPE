"""Public recruitment content, without invented schedules or signup workflows."""
from urllib.parse import urlsplit
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from SPDWEBAPP_CORE.api.links import safe_public_url
from .models import RushFormLink, RushSlide


class RecruitmentSlideSerializer(serializers.Serializer):
    caption = serializers.CharField(allow_blank=True)
    image = serializers.CharField(allow_null=True)


class RecruitmentContentSerializer(serializers.Serializer):
    interest_url = serializers.CharField(allow_null=True)
    slides = RecruitmentSlideSerializer(many=True)


class PublicRecruitmentView(APIView):
    """Return configured recruitment content; unavailable data remains explicit."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(responses=RecruitmentContentSerializer, auth=[])
    def get(self, request):
        interest = RushFormLink.objects.first()
        url = safe_public_url(interest.link) if interest else None
        # A self-referencing recruitment link cannot serve as an interest destination.
        parsed = urlsplit(url) if url else None
        if parsed and parsed.path.rstrip('/') == '/app/join' and parsed.netloc in {'', request.get_host()}:
            url = None
        data = {
            'interest_url': url,
            'slides': [{'caption': slide.caption,
                        'image': safe_public_url(slide.image.url) if slide.image else None}
                       for slide in RushSlide.objects.order_by('order', 'pk')],
        }
        return Response(RecruitmentContentSerializer(data).data, headers={'Cache-Control': 'no-store'})
