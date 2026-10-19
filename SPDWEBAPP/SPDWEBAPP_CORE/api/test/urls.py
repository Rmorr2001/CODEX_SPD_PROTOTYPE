from django.urls import include, path
from rest_framework.response import Response
from rest_framework.views import APIView


class PrivateView(APIView):
    def get(self, request):
        return Response({'allowed': True})


urlpatterns = [path('private/', PrivateView.as_view()),
               path('', include('SPDWEBAPP_CORE.urls'))]
