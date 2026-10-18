from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import Client, RequestFactory, override_settings
from django.urls import reverse
from django.utils.html import escape

from AUTHENTICATE.models import Brother_Profile, Major, Role
from HOME import views
from HOME.models import BannerImage, RushFormLink, RushSlide
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing import demo_settings
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import csrf_client, login_actor
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope

from .helpers import HTML, content, file_path, slide, upload


ROUTES = {
    "/": "HOME/home.html", "/ourHistory/": "HOME/ourHistory.html",
    "/codeOfEthics/": "HOME/codeOfEthics.html", "/rush/": "HOME/rush.html",
    "/executive-board/": "HOME/executive_board.html",
}


class PublicPageTests(RegressionTestCase):
    def test_public_routes_render_for_narrow_actors(self):
        rows = content()
        for index, roles in enumerate((None, (), ("ACTIVE",), ("NEW_MEMBER",), ("ALUMNI",), ("EXEC",))):
            client = Client()
            actor = None if roles is None else make_user(username=f"actor-{index}", roles=roles)
            if actor:
                login_actor(client, actor)
            before = snapshot_scope(list(rows) + ([actor, actor.brother_profile] if actor else []),
                                    relations=[actor.brother_profile.roles] if actor else [],
                                    files=[file_path(rows[0].image), file_path(rows[2].image)])
            for path, template in ROUTES.items():
                with self.subTest(roles=roles, path=path):
                    response = client.get(path)
                    self.assertEqual(response.status_code, 200)
                    self.assertTemplateUsed(response, template)
                    hrefs = [a.get("href") for a in HTML(response).attrs("a")]
                    for name in ("home", "ourHistory", "rush", "codeOfEthics", "executive_board"):
                        self.assertIn(reverse(name), hrefs)
                    self.assertEqual(client.session.get("_auth_user_id"), str(actor.pk) if actor else None)
                    assert_unchanged(before)

    def test_home_without_banner_omits_banner_image(self):
        keep = slide()
        before = snapshot_scope([keep], files=[file_path(keep.image)])
        response = self.client.get("/")
        self.assertContains(response, "Sigma Phi Delta: Beta-Omicron Chapter")
        self.assertNotIn("Fraternity Banner", [i.get("alt") for i in HTML(response).attrs("img")])
        self.assertIn("/rush/", [a.get("href") for a in HTML(response).attrs("a")])
        self.assertEqual(BannerImage.objects.count(), 0)
        assert_unchanged(before)

    def test_history_empty_profile_count_is_zero(self):
        keep = RushFormLink.objects.create(link="https://example.invalid/rush")
        before = snapshot_scope([keep])
        response = self.client.get("/ourHistory/")
        self.assertEqual(response.context["num_actives"], 0)
        self.assertContains(response, "0 active members")
        self.assertFalse(Brother_Profile.objects.exists())
        self.assertFalse(Role.objects.exists())
        assert_unchanged(before)

    def test_rush_without_slides_renders_empty_slideshow(self):
        link = RushFormLink.objects.create(link="https://example.invalid/rush")
        before = snapshot_scope([link])
        response = self.client.get("/rush/")
        self.assertContains(response, "Rush Information")
        html = HTML(response)
        self.assertFalse([a for a in html.attrs("div") if "mySlides" in a.get("class", "").split()])
        self.assertEqual([a.get("href") for a in html.attrs("a")].count(link.link), 2)
        self.assertEqual(len([a for a in html.attrs("a") if a.get("class") in ("prev", "next")]), 2)
        self.assertFalse(RushSlide.objects.exists())
        assert_unchanged(before)

    def test_board_without_officers_has_empty_message(self):
        a = make_user(username="active", roles=("ACTIVE",))
        b = make_user(username="exec", roles=("EXEC",))
        banner = BannerImage.objects.create(image=upload())
        before = snapshot_scope([a.brother_profile, b.brother_profile, banner], files=[file_path(banner.image)])
        response = self.client.get("/executive-board/")
        self.assertContains(response, "No Executive Board members found")
        self.assertEqual(response.context["exec_board_brothers"], [])
        assert_unchanged(before)
        self.assertFalse(hasattr(Brother_Profile.objects.get(user=a), "position"))

    def test_public_shell_without_actor_profile_uses_fallback(self):
        actor = make_user(username="profileless", with_profile=False)
        rows = content()
        login_actor(self.client, actor)
        actor.refresh_from_db()
        before = snapshot_scope([actor, *rows], files=[file_path(rows[0].image)])
        response = self.client.get("/")
        self.assertContains(response, "profileless")
        self.assertTrue(any(i.get("src", "").endswith("images/default_profile.png")
                            for i in HTML(response).attrs("img")))
        self.assertFalse(Brother_Profile.objects.filter(user=actor).exists())
        self.assertEqual(self.client.session["_auth_user_id"], str(actor.pk))
        assert_unchanged(before)

    def test_active_count_uses_distinct_role_membership(self):
        actors = [make_user(username=n, roles=r) for n, r in (
            ("a", ("ACTIVE",)), ("b", ("ACTIVE", "EXEC")), ("c", ("ALUMNI",)), ("d", ())) ]
        before = snapshot_scope([u.brother_profile for u in actors])
        roles_before = [set(u.brother_profile.roles.values_list("name", flat=True)) for u in actors]
        for _ in range(2):
            response = self.client.get("/ourHistory/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["num_actives"], 2)
        assert_unchanged(before)
        self.assertEqual(roles_before, [set(u.brother_profile.roles.values_list("name", flat=True)) for u in actors])

    def test_board_role_order_and_multi_office_pairs(self):
        offices = ["PRESIDENT", "INT_VP", "EXT_VP", "AFFAIRS_DIRECTOR", "BUSINESS_MGR",
                   "RECRUITMENT_CHAIR", "PHIL_CHAIR", "RISK_MGR", "SOCIAL_CHAIR"]
        for name in reversed(offices):
            Role.objects.create(name=name)
        actors = [make_user(username=code, roles=("ACTIVE", "EXEC", code))
                  for code in offices if code != "INT_VP"]
        a = actors[0]
        a.brother_profile.roles.add(Role.objects.get(name="PHIL_CHAIR"))
        b = make_user(username="second-president", roles=("ACTIVE", "EXEC", "PRESIDENT"))
        before = snapshot_scope([u.brother_profile for u in [*actors, b]],
                                relations=[u.brother_profile.roles for u in [*actors, b]])
        expected = ["President", "External Vice President", "Director of Chapter Affairs",
                    "Director of Business", "Director of Recruitment", "Director of Philanthropy",
                    "Director of Risk Management", "Director of Social Affairs"]
        for _ in range(2):
            response = self.client.get("/executive-board/")
            self.assertEqual(response.status_code, 200)
            pairs = [(position, brother.pk) for position, brother in response.context["exec_board_brothers"]]
            self.assertEqual(list(dict.fromkeys(p for p, _ in pairs)), expected)
            self.assertEqual(len(pairs), len(set(pairs)))
            self.assertEqual(pairs.count(("President", a.brother_profile.pk)), 1)
            self.assertEqual(pairs.count(("President", b.brother_profile.pk)), 1)
            self.assertEqual(pairs.count(("Director of Philanthropy", a.brother_profile.pk)), 1)
        assert_unchanged(before)
        self.assertTrue(all(not hasattr(p, "position") for p in Brother_Profile.objects.all()))

    def test_slide_order_preserves_all_ties(self):
        slides = [slide(caption, order) for caption, order in (("A", -1), ("B", 0), ("C", 3), ("D", 3))]
        before = snapshot_scope(slides, files=[file_path(s.image) for s in slides])
        response = self.client.get("/rush/")
        self.assertEqual(response.status_code, 200)
        result = list(response.context["rush_slides"])
        self.assertEqual([s.caption for s in result[:2]], ["A", "B"])
        self.assertEqual({s.caption for s in result[2:]}, {"C", "D"})
        self.assertEqual(len([i for i in HTML(response).attrs("img")
                              if i.get("class") == "image-cropped"]), 4)
        assert_unchanged(before)

    def test_slide_caption_and_image_attributes_escape_markup(self):
        caption = '<script>alert(1)</script> "quoted"'
        obj = RushSlide.objects.create(caption=caption, image='rush_slides/a"&.png')
        before = snapshot_scope([obj])
        response = self.client.get("/rush/")
        self.assertContains(response, escape(caption))
        html = HTML(response)
        images = [i for i in html.attrs("img") if i.get("class") == "image-cropped"]
        self.assertEqual(len(images), 1)
        self.assertEqual(set(images[0]), {"class", "src", "style", "loading"})
        self.assertNotIn(caption, response.content.decode())
        assert_unchanged(before)

    def test_board_fields_escape_injected_markup(self):
        payload = '<script>alert(1)</script> "x"'
        actor = make_user(username="officer", roles=("ACTIVE", "EXEC", "PRESIDENT"),
                          profile_fields={"firstName": payload, "lastName": payload})
        actor.email = 'x"<b>@example.invalid'
        actor.save()
        major = Major.objects.create(name=payload)
        actor.brother_profile.majors.add(major)
        before = snapshot_scope([actor, actor.brother_profile, major],
                                relations=[actor.brother_profile.roles, actor.brother_profile.majors])
        response = self.client.get("/executive-board/")
        self.assertContains(response, escape(payload))
        self.assertContains(response, escape(actor.email))
        self.assertNotIn(payload, response.content.decode())
        self.assertFalse(any("onmouseover" in attrs for _, attrs in HTML(response).tags))
        assert_unchanged(before)

    def test_shell_errors_messages_and_username_escape(self):
        actor = make_user(username="<b>actor</b>")
        login_actor(self.client, actor)
        rows = content()
        before = snapshot_scope([actor, *rows])
        request = RequestFactory().get("/", {"error": "<img src=x onerror=alert(1)>"})
        request.user, request.session = actor, self.client.session
        request._messages = FallbackStorage(request)
        messages.error(request, "<script>alert(1)</script>")
        response = views.home(request)
        for payload in (actor.username, "<script>alert(1)</script>", "<img src=x onerror=alert(1)>"):
            self.assertContains(response, escape(payload))
            self.assertNotIn(payload, response.content.decode())
        self.assertEqual(self.client.session["_auth_user_id"], str(actor.pk))
        assert_unchanged(before)

    def test_configured_interest_link_renders_in_three_buttons(self):
        rows = content()
        link = rows[1]
        link.link = "https://example.invalid/rush?a=1&b=2"
        link.save()
        before = snapshot_scope(list(rows), files=[file_path(rows[0].image), file_path(rows[2].image)])
        for path, count in (("/", 1), ("/rush/", 2)):
            response = self.client.get(path)
            self.assertEqual([a.get("href") for a in HTML(response).attrs("a")].count(link.link), count)
            self.assertContains(response, "a=1&amp;b=2", count=count)
        assert_unchanged(before)

    def test_board_optional_fields_use_fallbacks(self):
        a = make_user(username="a", roles=("ACTIVE", "EXEC", "PRESIDENT"))
        b = make_user(username="b", roles=("ACTIVE", "EXEC", "PHIL_CHAIR"))
        for user in (a, b):
            user.email = ""
            user.save()
        Brother_Profile.objects.filter(user=b).update(profileImage="profile_images/absent.png")
        orphan = Brother_Profile.objects.create(firstName="Null", lastName="User", user=None)
        orphan.roles.add(Role.objects.get(name="PRESIDENT"))
        before = snapshot_scope([a.brother_profile, b.brother_profile, orphan],
                                relations=[a.brother_profile.roles, b.brother_profile.roles, orphan.roles])
        response = self.client.get("/executive-board/")
        self.assertEqual(response.status_code, 200)
        imgs = HTML(response).attrs("img")
        self.assertTrue(any(i.get("src", "").endswith("default_profile.png") for i in imgs))
        self.assertTrue(any("default_profile.png" in i.get("onerror", "") for i in imgs))
        self.assertFalse([a for a in HTML(response).attrs("a") if a.get("href", "").startswith("mailto:")
                          and "example.invalid" in a.get("href", "")])
        self.assertNotContains(response, "<strong>Major")
        assert_unchanged(before)

    def test_missing_nonempty_image_keeps_page_renderable(self):
        banner = BannerImage.objects.create(image="banners/absent.webp")
        obj = RushSlide.objects.create(image="rush_slides/absent.webp", caption="Absent")
        before = snapshot_scope([banner, obj])
        for path, field in (("/", banner.image), ("/rush/", obj.image)):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(field.url, [i.get("src") for i in HTML(response).attrs("img")])
            self.assertFalse(file_path(field).exists())
        assert_unchanged(before)

    def test_public_head_and_irrelevant_query_are_read_only(self):
        actor = make_user(username="reader", roles=("ACTIVE",))
        login_actor(self.client, actor)
        rows = content()
        before = snapshot_scope([actor, *rows], files=[file_path(rows[0].image), file_path(rows[2].image)])
        for path, template in ROUTES.items():
            head, get = self.client.head(path), self.client.get(path, {"unused": "1"})
            self.assertEqual((head.status_code, head.content, get.status_code), (200, b"", 200))
            self.assertTemplateUsed(get, template)
            self.assertEqual(self.client.session["_auth_user_id"], str(actor.pk))
        assert_unchanged(before)

    @override_settings(ROOT_URLCONF=demo_settings.ROOT_URLCONF,
                       MIDDLEWARE=demo_settings.MIDDLEWARE, TEMPLATES=demo_settings.TEMPLATES,
                       DEMO_MODE=True, CSRF_COOKIE_SECURE=True, SESSION_COOKIE_SECURE=True)
    def test_public_unsafe_request_rejects_bad_csrf(self):
        client = csrf_client()
        rows = content()
        client.get("/", secure=True)
        self.assertIn("csrftoken", client.cookies)
        before = snapshot_scope(list(rows), files=[file_path(rows[0].image)])
        for path in ROUTES:
            for token in (None, "bad-token"):
                response = client.post(path, {} if token is None else {"csrfmiddlewaretoken": token}, secure=True)
                self.assertEqual(response.status_code, 403)
        self.assertIsNone(client.session.get("_auth_user_id"))
        assert_unchanged(before)
