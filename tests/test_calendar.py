import unittest
from igfb_agent.calendar import brasileirao_editions, participation_editions
from igfb_agent.coverage import measure_coverage

class CalendarTests(unittest.TestCase):
    def test_all_seasons(self):
        editions = brasileirao_editions()
        self.assertEqual(len(editions), 55)
        self.assertEqual(editions[0].edition_id, "brasileirao:1971")
        self.assertEqual(editions[-1].edition_id, "brasileirao:2025")

    def test_no_pre_1971(self):
        with self.assertRaises(ValueError):
            brasileirao_editions(1970, 2025)

    def test_no_2026(self):
        with self.assertRaises(ValueError):
            brasileirao_editions(1971, 2026)

    def test_distinct_participation_identity(self):
        self.assertEqual(len(participation_editions()), 55)
        self.assertNotEqual(brasileirao_editions()[0].edition_id,
                            participation_editions()[0].edition_id)

    def test_calendar_not_approved_results(self):
        report = measure_coverage([], brasileirao_editions(), [])
        self.assertEqual(report.registered_editions, 55)
        self.assertEqual(report.approved_results, 0)
        self.assertEqual(report.approved_coverage_ratio, 0.0)

if __name__ == "__main__":
    unittest.main()
