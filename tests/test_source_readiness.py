import unittest
from igfb_agent.source_readiness import source_readiness
from igfb_agent.candidates import build_candidates

class SourceReadinessTests(unittest.TestCase):
    def test_actual_leads_do_not_approve_any_result(self):
        report = source_readiness()
        self.assertEqual(report["approved_results"], 0)
        self.assertGreater(report["distinct_years_with_leads"], 0)
        self.assertLessEqual(report["distinct_years_with_leads"], 55)

    def test_reject_approved_candidate(self):
        item = dict(build_candidates()[0])
        item["approved"] = True
        with self.assertRaises(ValueError):
            source_readiness([item])

    def test_reject_outside_scope(self):
        item = dict(build_candidates()[0])
        item["year"] = 1969
        with self.assertRaises(ValueError):
            source_readiness([item])

    def test_reject_wrong_edition(self):
        item = dict(build_candidates()[0])
        item["edition_id"] = "brasileirao:2025"
        with self.assertRaises(ValueError):
            source_readiness([item])

    def test_page_checked_not_archived(self):
        item = dict(build_candidates()[0])
        item["source_page_checked"] = True
        item["source_archived"] = False
        report = source_readiness([item])
        self.assertEqual(report["checked_source_pages"], 1)
        self.assertEqual(report["source_ids_without_archived_bytes"], 1)
        self.assertEqual(report["approved_results"], 0)

    def test_empty_leads_reports_all_missing(self):
        report = source_readiness([])
        self.assertEqual(len(report["years_without_leads"]), 55)
        self.assertEqual(report["total_candidates"], 0)

if __name__ == "__main__":
    unittest.main()
