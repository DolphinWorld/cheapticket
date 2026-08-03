import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import flight_monitor


class ProviderDate:
    def __init__(self, date_parts, time_parts):
        self.date = date_parts
        self.time = time_parts


class MonitorTests(unittest.TestCase):
    def test_dates_around(self):
        self.assertEqual(
            list(flight_monitor.dates_around("2026-12-22", 2)),
            [
                "2026-12-20",
                "2026-12-21",
                "2026-12-22",
                "2026-12-23",
                "2026-12-24",
            ],
        )

    def test_dates_between(self):
        self.assertEqual(
            list(flight_monitor.dates_between("2026-12-20", "2026-12-22")),
            ["2026-12-20", "2026-12-21", "2026-12-22"],
        )

    def test_flight_datetime_skips_incomplete_provider_timestamp(self):
        self.assertIsNone(
            flight_monitor.flight_datetime(
                ProviderDate((2026, 12, 29), (None, 30))
            )
        )

    def test_flight_datetime_formats_valid_provider_timestamp(self):
        self.assertEqual(
            flight_monitor.flight_datetime(
                ProviderDate((2026, 12, 29), (6, 30))
            ),
            "2026-12-29T06:30",
        )

    def test_no_flights_provider_response_becomes_empty_result(self):
        from fast_flights.exceptions import FlightsNotFound

        def no_flights(_query):
            raise FlightsNotFound("no flights found")

        self.assertEqual(flight_monitor.flights_or_empty(no_flights, object()), [])

    def test_threshold_changes_only_after_email_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text(
                '{"threshold": 550, "last_checked_at": null, '
                '"last_price": null, "last_error": null}'
            )
            deal = flight_monitor.Deal(
                price=499,
                travel_date="2026-12-22",
                departure_at="2026-12-22T10:00",
                origin="JFK",
                destination="SEA",
                airlines=["Example Air"],
                stops=0,
                booking_url="https://example.test",
            )
            with (
                patch.object(flight_monitor, "STATE_PATH", state_path),
                patch.object(flight_monitor, "search_deals", return_value=[deal]),
                patch.object(flight_monitor, "send_email"),
                patch.dict(
                    os.environ,
                    {
                        "ALERT_EMAIL": "me@example.com",
                        "SMTP_USERNAME": "me@example.com",
                    },
                    clear=False,
                ),
            ):
                self.assertEqual(flight_monitor.run(), 0)
            self.assertEqual(flight_monitor.load_json(state_path)["threshold"], 499)

    def test_failed_email_preserves_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text(
                '{"threshold": 550, "last_checked_at": null, '
                '"last_price": null, "last_error": null}'
            )
            deal = flight_monitor.Deal(
                499, "2026-12-22", "2026-12-22T10:00", "JFK", "SEA", ["Example Air"], 0, "https://x"
            )
            with (
                patch.object(flight_monitor, "STATE_PATH", state_path),
                patch.object(flight_monitor, "search_deals", return_value=[deal]),
                patch.object(
                    flight_monitor, "send_email", side_effect=RuntimeError("SMTP down")
                ),
                patch.dict(
                    os.environ,
                    {
                        "ALERT_EMAIL": "me@example.com",
                        "SMTP_USERNAME": "me@example.com",
                    },
                    clear=False,
                ),
            ):
                with self.assertRaises(RuntimeError):
                    flight_monitor.run()
            self.assertEqual(flight_monitor.load_json(state_path)["threshold"], 550)


if __name__ == "__main__":
    unittest.main()
