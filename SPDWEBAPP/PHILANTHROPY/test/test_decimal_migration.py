"""Upgrade preserves old integer data; downgrade cannot silently truncate new fractions."""
from datetime import date
from decimal import Decimal
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.exceptions import IrreversibleError
from django.test import TransactionTestCase


class DecimalMigrationTests(TransactionTestCase):
    def test_integer_upgrade_and_fractional_downgrade_guard(self):
        executor = MigrationExecutor(connection)
        leaves = executor.loader.graph.leaf_nodes()
        old = [('PHILANTHROPY', '0004_philanthropy_hours_event_and_request_last_edited_at_and_more')]
        try:
            executor.migrate(old)
            apps = executor.loader.project_state(old).apps
            user = apps.get_model('auth', 'User').objects.create(username='migration-member')
            Event = apps.get_model('PHILANTHROPY', 'Philanthropy_Hours_Event_and_Request')
            event = Event.objects.create(user_id=user.pk, philanthropy_event_title='Old integer event',
                philanthropy_event_hours=3, philanthropy_event_date=date(2026, 10, 1),
                philanthropy_approval_status='approved')
            executor = MigrationExecutor(connection)
            executor.migrate(leaves)
            from PHILANTHROPY.models import Philanthropy_Hours_Event_and_Request
            row = Philanthropy_Hours_Event_and_Request.objects.get(pk=event.pk)
            self.assertEqual(row.philanthropy_event_hours, Decimal('3.00'))
            self.assertEqual(row.philanthropy_approval_status, 'approved')
            row.philanthropy_event_hours = Decimal('3.75')
            row.save()
            with self.assertRaises(IrreversibleError):
                MigrationExecutor(connection).migrate(old)
            row.refresh_from_db()
            self.assertEqual(row.philanthropy_event_hours, Decimal('3.75'))
        finally:
            MigrationExecutor(connection).migrate(leaves)
