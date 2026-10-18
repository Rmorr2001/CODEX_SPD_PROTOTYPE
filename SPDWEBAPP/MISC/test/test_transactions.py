"""Injected failures establish stock admin transaction behavior with real writes."""
from unittest.mock import patch

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.test import TransactionTestCase
from django.db import router

from SPDWEBAPP_CORE.testing.state import snapshot_scope, assert_unchanged
from .support import AdminAssertions, MODELS, create, payload, admin_url


class AdminTransactionTests(AdminAssertions, TransactionTestCase):
    def test_admin_save_log_failure_rolls_back_model_write(self):
        for model in MODELS:
            target = create(model, "Before")
            before = snapshot_scope([target])
            alias = router.db_for_write(model)
            count = model.objects.using(alias).count()
            model_admin = admin.site._registry[model]
            for action, hook in (("add", "log_addition"), ("change", "log_change")):
                with self.subTest(model=model.__name__, action=action):
                    def fail_after_real_log(*args, **kwargs):
                        original(*args, **kwargs)
                        raise RuntimeError("synthetic log failure")
                    original = getattr(model_admin, hook)
                    with patch.object(model_admin, hook, side_effect=fail_after_real_log):
                        with self.assertRaisesMessage(RuntimeError, "synthetic log failure"):
                            self.client.post(admin_url(model, action, target.pk if action == "change" else None),
                                             payload(model, _save="1"))
                    self.assertEqual(model.objects.using(alias).count(), count)
                    assert_unchanged(before)
                    self.assertFalse(LogEntry.objects.using(alias).exists())
                    self.identity()

    def test_admin_model_save_failure_creates_no_audit_entry(self):
        for model in MODELS:
            target = create(model, "Before")
            before = snapshot_scope([target])
            count = model.objects.count()
            for action in ("add", "change"):
                with patch.object(admin.site._registry[model], "save_model",
                                  side_effect=RuntimeError("synthetic save failure")):
                    with self.assertRaisesMessage(RuntimeError, "synthetic save failure"):
                        self.client.post(admin_url(model, action, target.pk if action == "change" else None),
                                         payload(model, _save="1"))
                self.assertEqual(model.objects.count(), count)
                assert_unchanged(before)
                self.assertFalse(LogEntry.objects.exists())
                self.identity()

    def test_detail_delete_failure_rolls_back_preceding_delete_log(self):
        for model in MODELS:
            target = create(model, "Before")
            before = snapshot_scope([target])
            model_admin = admin.site._registry[model]
            original = model_admin.delete_model
            count = model.objects.count()
            for after_delete in (False, True):
                def fail(request, obj):
                    if after_delete:
                        original(request, obj)
                    raise RuntimeError("synthetic delete failure")
                with patch.object(model_admin, "delete_model", side_effect=fail):
                    with self.assertRaisesMessage(RuntimeError, "synthetic delete failure"):
                        self.client.post(admin_url(model, "delete", target.pk), {"post": "yes"})
                self.assertEqual(model.objects.count(), count)
                assert_unchanged(before)
                self.assertFalse(LogEntry.objects.exists())
                self.identity()
