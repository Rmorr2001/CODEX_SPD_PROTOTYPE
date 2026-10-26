from copy import deepcopy
from pathlib import Path
from types import ModuleType
from urllib.parse import unquote, urlsplit

from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase, override_settings
from django.urls import include, path, re_path
from django.views.static import serve

from HOME.models import BannerImage
from railway_demo.static_headers import add_headers
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.factories import make_user
from SPDWEBAPP_CORE.testing.helpers import login_actor
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope

from .helpers import HTML, content, file_path, image_bytes, upload
from .test_public_pages import ROUTES


class MediaCompositionTests(RegressionTestCase):
    def setUp(self):
        super().setUp()
        # Core binds document_root at import time. This isolated URLconf binds the
        # identical view/regex to this test's MEDIA_ROOT, never a runtime media path.
        self.urlconf = ModuleType("HOME_test_media_urls")
        self.urlconf.urlpatterns = [
            re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
            path("", include("SPDWEBAPP_CORE.urls")),
        ]
        self.enterContext(override_settings(ROOT_URLCONF=self.urlconf, DEBUG=False))

    def test_media_serves_synthetic_image_bytes(self):
        banner = BannerImage.objects.create(image=upload("a.webp"))
        before = snapshot_scope([banner], files=[file_path(banner.image)])
        response = self.client.get(banner.image.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), image_bytes())
        self.assertEqual(response["Content-Type"], "image/webp")
        self.assertIsNone(self.client.session.get("_auth_user_id"))
        assert_unchanged(before)

    def test_missing_media_and_directories_do_not_disclose(self):
        banner = BannerImage.objects.create(image=upload())
        directory = Path(settings.MEDIA_ROOT) / "subdirectory"
        directory.mkdir()
        before = snapshot_scope([banner], files=[file_path(banner.image)])
        for url in ("/media/absent.webp", "/media/subdirectory/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
            self.assertNotIn(str(settings.MEDIA_ROOT).encode(), response.content)
            self.assertNotContains(response, "Directory indexes", status_code=404)
        self.assertFalse((Path(settings.MEDIA_ROOT) / "absent.webp").exists())
        assert_unchanged(before)

    def test_lexical_media_traversal_is_denied(self):
        banner = BannerImage.objects.create(image=upload())
        outside = Path(settings.MEDIA_ROOT).parent / (Path(settings.MEDIA_ROOT).name + "-outside.txt")
        outside.write_bytes(b"synthetic-outside-canary")
        self.addCleanup(outside.unlink, missing_ok=True)
        before = snapshot_scope([banner], files=[file_path(banner.image), outside])
        for url in (f"/media/../{outside.name}", f"/media/%2e%2e/{outside.name}",
                    f"/media/%2F{outside.name}", f"/media/a/%2e%2e/%2e%2e/{outside.name}"):
            response = self.client.get(url)
            self.assertIn(response.status_code, (400, 403, 404))
            self.assertNotIn(b"synthetic-outside-canary", response.content)
            self.assertNotIn(str(outside).encode(), response.content)
        assert_unchanged(before)

    def test_public_templates_reference_local_assets(self):
        rows = content()
        before = snapshot_scope(list(rows), files=[file_path(rows[0].image), file_path(rows[2].image)])
        seen = set()
        for route in ROUTES:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200)
            for tag, attrs in HTML(response).tags:
                if tag not in ("img", "link", "script"):
                    continue
                value = attrs.get("src", attrs.get("href", ""))
                if value.startswith(settings.STATIC_URL):
                    relative = unquote(urlsplit(value).path[len(settings.STATIC_URL):])
                    self.assertIsNotNone(finders.find(relative), relative)
                    seen.add(relative)
        self.assertTrue({"css/PARLEYPRO.CSS", "images/favicon.webp", "css/main.css"} <= seen)
        assert_unchanged(before)

    def test_demo_shell_context_controls_banner(self):
        rows = content()
        actor = make_user(username="shell-reader", roles=("ACTIVE",))
        login_actor(self.client, actor)
        actor.refresh_from_db()
        before = snapshot_scope([actor, *rows], files=[file_path(rows[0].image)])
        business = self.client.get("/legacy/")
        self.assertEqual(business.status_code, 200)
        self.assertNotContains(business, "railway-demo-banner")
        templates = deepcopy(settings.TEMPLATES)
        templates[0]["OPTIONS"]["context_processors"].append("railway_demo.context.demo_state")
        with override_settings(ROOT_URLCONF="railway_demo.urls", DEMO_MODE=True, TEMPLATES=templates,
                               MIDDLEWARE=[*settings.MIDDLEWARE, "railway_demo.middleware.DemoBoundaryMiddleware"]):
            demo = self.client.get("/legacy/", secure=True)
        self.assertEqual(demo.status_code, 200)
        self.assertContains(demo, "Enter demo")
        self.assertTemplateUsed(demo, "railway_demo/banner.html")
        for response in (business, demo):
            self.assertNotContains(response, "Traceback")
            self.assertNotContains(response, settings.SECRET_KEY)
            for route in ROUTES:
                self.assertIn(route, [a.get("href") for a in HTML(response).attrs("a")])
        self.assertEqual(self.client.session["_auth_user_id"], str(actor.pk))
        assert_unchanged(before)


class CacheHeaderTests(SimpleTestCase):
    def test_explorer_cache_header_is_scoped(self):
        headers = {"X-Fixture": "keep", "Cache-Control": "max-age=60"}
        add_headers(headers, "/unused", "/static/railway_demo/file-tree.html")
        self.assertEqual(headers, {"X-Fixture": "keep", "Cache-Control": "no-cache"})
        for url in ("/static/css/main.css", "/static/railway_demo/file-tree.html.extra"):
            headers = {"X-Fixture": "keep", "Cache-Control": "max-age=60"}
            add_headers(headers, "/unused", url)
            self.assertEqual(headers, {"X-Fixture": "keep", "Cache-Control": "max-age=60"})
