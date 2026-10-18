"""Test sentinel behind the production decorator and full request middleware."""
from django.http import HttpResponse
from django.urls import include, path
from PARLEYPRO.pp_decorators import requires_role

calls = []


@requires_role("EXEC", "ACTIVE")
def gated_sentinel(request):
    calls.append(request.user.pk)
    return HttpResponse("reached")


urlpatterns = [path("test-role-gate/", gated_sentinel), path("", include("SPDWEBAPP_CORE.urls"))]
