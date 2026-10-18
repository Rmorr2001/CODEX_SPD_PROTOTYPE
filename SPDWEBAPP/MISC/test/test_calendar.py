"""Calendar-date preservation without contractualizing the physical fall defect."""
from django.test import SimpleTestCase
from django.utils import timezone

from MISC.utils import get_next_dst_change
from .support import misc_time as at_time, instant


class CalendarTests(SimpleTestCase):
    def calculate(self, value):
        with at_time(instant(value)):
            result = get_next_dst_change()
        self.assertTrue(timezone.is_aware(result))
        self.assertGreater(result, instant(value))
        return result

    def test_spring_boundary_returns_strictly_future_calendar_date(self):
        for clock, date in [("2026-03-08T07:59:59Z", "2026-03-08"),
                            ("2026-03-08T08:00:00Z", "2026-11-01"),
                            ("2026-03-08T08:00:01Z", "2026-11-01")]:
            with self.subTest(clock=clock):
                result = self.calculate(clock)
                self.assertEqual(str(result.date()), date)
                if date == "2026-03-08":
                    self.assertEqual(result, instant("2026-03-08T08:00:00Z"))

    def test_year_rollover_keeps_next_spring_date(self):
        for clock in ("2027-01-01T05:59:59Z", "2027-01-01T06:00:00Z"):
            result = self.calculate(clock)
            self.assertEqual(str(result.date()), "2027-03-14")
            self.assertEqual(result, instant("2027-03-14T08:00:00Z"))

    def test_second_and_first_sunday_dates_across_years(self):
        for clock, date in [("2027-01-01T12:00:00Z", "2027-03-14"),
                            ("2027-04-01T12:00:00Z", "2027-11-07"),
                            ("2028-01-01T12:00:00Z", "2028-03-12"),
                            ("2028-04-01T12:00:00Z", "2028-11-05")]:
            with self.subTest(clock=clock):
                self.assertEqual(str(self.calculate(clock).date()), date)

    def test_chicago_calendar_is_independent_of_django_timezone(self):
        for zone in ("UTC", "Asia/Tokyo", "America/Los_Angeles"):
            with self.subTest(zone=zone), timezone.override(zone):
                result = self.calculate("2026-01-01T05:30:00Z")
                self.assertEqual(str(result.date()), "2026-03-08")
                self.assertEqual(result, instant("2026-03-08T08:00:00Z"))
