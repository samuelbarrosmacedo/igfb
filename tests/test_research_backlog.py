import unittest
from igfb_agent.research_backlog import research_backlog

def candidate(year, sid="source"):
    return {
        "year": year, "edition_id": f"brasileirao:{year}",
        "competition": "brasileirao", "source_id": sid,
        "status": "candidate_requires_review", "approved": False,
        "source_page_checked": False, "source_archived": False,
    }

class ResearchBacklogTests(unittest.TestCase):
    def test_empty_sources_create_55_discovery_tasks(self):
        result = research_backlog([])
        self.assertEqual(result["seasons_without_leads"], 55)
        self.assertEqual(result["lead_coverage_percent"], 0)
        self.assertEqual(len(result["tasks"]), 55)
        self.assertTrue(all(t["stage"] == "discover_official_source" for t in result["tasks"]))

    def test_missing_seasons_come_before_existing_leads(self):
        result = research_backlog([candidate(1971)])
        self.assertEqual(result["seasons_with_leads"], 1)
        self.assertEqual(result["seasons_without_leads"], 54)
        self.assertEqual(result["lead_coverage_percent"], 1.82)
        self.assertEqual(result["tasks"][-1]["year"], 1971)
        self.assertEqual(result["tasks"][-1]["stage"], "archive_and_verify_source")

    def test_multiple_leads_do_not_inflate_coverage(self):
        result = research_backlog([candidate(1971, "a"), candidate(1971, "b")])
        self.assertEqual(result["seasons_with_leads"], 1)
        self.assertEqual(result["tasks"][-1]["candidate_count"], 2)

    def test_invalid_year_is_rejected(self):
        with self.assertRaises(ValueError):
            research_backlog([candidate(1970)])

    def test_approved_lead_is_rejected(self):
        item = candidate(2000)
        item["approved"] = True
        with self.assertRaises(ValueError):
            research_backlog([item])

    def test_current_dataset_is_not_homologated(self):
        result = research_backlog()
        self.assertEqual(result["total_seasons"], 55)
        self.assertFalse(result["ranking_approved"])
        self.assertEqual(len(result["tasks"]), 55)

if __name__ == "__main__":
    unittest.main()
