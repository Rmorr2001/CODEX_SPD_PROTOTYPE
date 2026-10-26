"""Public authenticated-profile and role boundary for domain read adapters."""
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import PermissionDenied as DomainPermissionDenied
from .models import Brother_Profile


def member_profile(user):
    """Return an authenticated caller's profile, or None without a profile lookup error."""
    if not user.is_authenticated:
        return None
    return Brother_Profile.objects.prefetch_related('roles').filter(user=user).first()



def require_member_roles(user, *required_roles):
    """Require an authenticated profile and ALL named roles before domain reads."""
    profile = member_profile(user)
    if profile is None:
        raise PermissionDenied("Your member profile is unavailable.")
    roles = {role.name for role in profile.roles.all()}
    if not set(required_roles).issubset(roles):
        raise PermissionDenied("Your current role cannot access this page.")
    return profile


def require_domain_roles(user, *required_roles):
    """Public domain boundary for HTML and REST operations, independent of HTTP transport."""
    profile = member_profile(user)
    if profile is None or not set(required_roles) <= {role.name for role in profile.roles.all()}:
        raise DomainPermissionDenied('Your current role cannot perform this action.')
    return profile
