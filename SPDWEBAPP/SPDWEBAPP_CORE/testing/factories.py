"""Minimal real-ORM fixtures with explicit identities and no inferred roles."""
from django.contrib.auth.models import User
from AUTHENTICATE.models import Brother_Profile, Role

TEST_PASSWORD = "Regression-fixture-only-42!"


def make_profile(user, *, roles=(), **profile_fields):
    """Create exactly one missing profile; invalid role names are fixture errors."""
    if Brother_Profile.objects.filter(user=user).exists():
        raise ValueError("User already has a profile")
    unknown = set(roles) - {name for name, _ in Role.ROLE_CHOICES}
    if unknown:
        raise ValueError(f"Undeclared fixture roles: {sorted(unknown)}")
    values = {"firstName": "Synthetic", "lastName": user.username, "hometown": "Fixture Town"}
    values.update(profile_fields)
    profile = Brother_Profile.objects.create(user=user, **values)
    profile.roles.set([Role.objects.get_or_create(name=name)[0] for name in roles])
    return profile


def make_user(*, username, roles=(), with_profile=True, password=TEST_PASSWORD,
              is_active=True, is_staff=False, is_superuser=False, profile_fields=None):
    """Return a saved User; password=None explicitly creates unusable credentials."""
    if not with_profile and (roles or profile_fields):
        raise ValueError("A profile is required for roles or profile fields")
    unknown = set(roles) - {name for name, _ in Role.ROLE_CHOICES}
    if unknown:
        raise ValueError(f"Undeclared fixture roles: {sorted(unknown)}")
    user = User.objects.create_user(
        username=username, password=password, email=f"{username}@example.invalid",
        is_active=is_active, is_staff=is_staff, is_superuser=is_superuser,
    )
    if with_profile:
        make_profile(user, roles=roles, **(profile_fields or {}))
    return user
