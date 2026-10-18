"""Django TestCase with per-test temporary media and real application behavior."""
from django.test import TestCase
from .helpers import temporary_media


class RegressionTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.media_root = self.enterContext(temporary_media())
