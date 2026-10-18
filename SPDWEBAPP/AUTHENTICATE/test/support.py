"""Thin domain fixtures and assertions; shared isolation stays in CORE.testing."""
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from PIL import Image

from AUTHENTICATE.models import Brother_Profile, Major, Role
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import login_actor

PROFILE_DATA = {
    "username": "updated-a", "email": "updated@example.invalid",
    "firstName": "Alex", "lastName": "Example", "hometown": "Demo Town", "pclass": "Alpha",
}
ALL_ROLES = [(), ("ACTIVE",), ("EXEC",), ("PHIL_CHAIR",), ("NM_BOARD",), ("NME",),
             ("EXEC", "ACTIVE"), ("PHIL_CHAIR", "ACTIVE"), ("NEW_MEMBER",),
             ("NEW_MEMBER", "ACTIVE"), ("NEW_MEMBER", "EXEC", "ACTIVE"),
             ("ALUMNI",), ("ALUMNI", "ACTIVE")]
BASIC_ROLES = [(), ("ACTIVE",), ("EXEC",), ("NEW_MEMBER",), ("ALUMNI",)]


def image_upload(name="new.png", size=(40, 40), image_format="PNG", color="green"):
    output = BytesIO()
    Image.new("RGB", size, color).save(output, format=image_format)
    return SimpleUploadedFile(name, output.getvalue(), content_type=f"image/{image_format.lower()}")


class FormInputs(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.inputs = {}
        self.forms = []
        self.feed(content.decode())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "input" and "name" in attrs:
            self.inputs[attrs["name"]] = attrs
        if tag == "form":
            self.forms.append(attrs)


def real_token(client, path="/auth/profile/", secure=False):
    response = client.get(path, secure=secure)
    if response.status_code != 200:
        raise AssertionError(f"CSRF form GET {path}: {response.status_code}")
    token = FormInputs(response.content).inputs["csrfmiddlewaretoken"]["value"]
    if not client.cookies.get("csrftoken"):
        raise AssertionError("Rendered form did not set a CSRF cookie")
    return token


def set_roles(user, roles):
    user.brother_profile.roles.set([Role.objects.get_or_create(name=name)[0] for name in roles])


def attach_image(user, name="old.png", color="red"):
    profile = Brother_Profile.objects.get(user=user)
    profile.profileImage = image_upload(name=name, color=color)
    profile.save()
    profile.refresh_from_db()
    return Path(profile.profileImage.path)


def member_state(user):
    """Fresh persisted identity fields and this member's owned profile relations."""
    data = {"user": User.objects.filter(pk=user.pk).values().get()}
    profile = Brother_Profile.objects.filter(user_id=user.pk).first()
    data["profile"] = Brother_Profile.objects.filter(pk=profile.pk).values().get() if profile else None
    data["roles"] = list(profile.roles.order_by("pk").values_list("pk", flat=True)) if profile else []
    data["majors"] = list(profile.majors.order_by("pk").values_list("pk", flat=True)) if profile else []
    return data


class IdentityCase(RegressionTestCase):
    def setUp(self):
        super().setUp()
        self.a = make_user(username="actor-a", roles=(), profile_fields={
            "firstName": "Alice", "lastName": "Actor", "hometown": "Town A", "pclass": "Alpha"})
        self.b = make_user(username="actor-b", roles=(), profile_fields={
            "firstName": "Brianna", "lastName": "Target", "hometown": "Town B", "pclass": "Beta"})

    def login(self, user=None, client=None):
        login_actor(client or self.client, user or self.a)

    def assert_identity(self, client, user):
        self.assertEqual(client.session.get("_auth_user_id"), str(user.pk) if user else None)

    def assert_member_unchanged(self, before, user, *, user_fields=(), profile_fields=(), relations=()):
        after = member_state(user)
        for field in user_fields:
            before["user"].pop(field, None)
            after["user"].pop(field, None)
        for field in profile_fields:
            before["profile"].pop(field, None)
            after["profile"].pop(field, None)
        for relation in relations:
            before.pop(relation, None)
            after.pop(relation, None)
        self.assertEqual(after, before)

    def pair_snapshot(self):
        return member_state(self.a), member_state(self.b)

    def assert_pair_unchanged(self, before, **a_exceptions):
        self.assert_member_unchanged(before[0], self.a, **a_exceptions)
        self.assert_member_unchanged(before[1], self.b)

    def assert_json(self, response, payload):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), payload)

    def major(self, name, user=None):
        major = Major.objects.create(name=name)
        if user:
            user.brother_profile.majors.add(major)
        return major

    def decode_image(self, user, size, image_format):
        profile = Brother_Profile.objects.get(user=user)
        self.assertTrue(profile.profileImage.storage.exists(profile.profileImage.name))
        with profile.profileImage.open("rb") as data, Image.open(data) as image:
            self.assertEqual(image.size, size)
            self.assertEqual(image.format, image_format)
        return profile
