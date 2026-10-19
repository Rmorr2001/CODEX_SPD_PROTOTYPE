"""Read-only delivery status and JSON namespace errors; no member data is exposed."""
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class StatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['ok'])
    api_version = serializers.ChoiceField(choices=['v1'])


class StatusView(APIView):
    """Public liveness contract; deliberately independent of database availability."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(responses=StatusSerializer, auth=[])
    def get(self, request):
        return Response(StatusSerializer({'status': 'ok', 'api_version': 'v1'}).data,
                        headers={'Cache-Control': 'no-store'})


class ApiNotFoundView(APIView):
    """Keep unmatched API paths inside the JSON boundary for every method."""
    authentication_classes = []
    permission_classes = [AllowAny]
    schema = None

    def http_method_not_allowed(self, request, *args, **kwargs):
        raise NotFound()

    options = http_method_not_allowed
