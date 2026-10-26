from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from AUTHENTICATE.models import Brother_Profile
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
    next_path = request.POST.get("next")
    if next_path in {"/app/dashboard", "/app/new-members"}:
        if Brother_Profile.objects.filter(user=user, roles__name="NEW_MEMBER").exists():
            return redirect("/app/new-members")
        return redirect(next_path)
    if next_path in {"/auth/dashboard/", "/auth/alumni_roster/", "/newmember/marks/", "/legacy/"}:
        return redirect(next_path)
    return redirect("/app/new-members" if Brother_Profile.objects.filter(user=user, roles__name="NEW_MEMBER").exists() else "/app/dashboard")
