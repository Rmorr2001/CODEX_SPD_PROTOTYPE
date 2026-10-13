from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

PERSONAS = {"executive": "demo-executive", "active": "demo-active", "newmember": "demo-newmember", "alumni": "demo-alumni"}


@require_POST
def enter(request):
    """Open only a seeded, unprivileged demo account; no password is shared."""
    if not getattr(settings, "DEMO_MODE", False):
        return HttpResponseNotFound()
    username = PERSONAS.get(request.POST.get("persona", "executive"))
    if not username:
        return HttpResponseBadRequest("Unknown demo persona.")
    user = User.objects.filter(groups__name=f"railway-demo:{username}", is_active=True, is_staff=False, is_superuser=False).first()
    if user is None or user.has_usable_password():
        return HttpResponse("The demo account is not ready.", status=503)
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect("alumni_roster" if request.POST.get("persona") == "alumni" else "dashboard")
