import unittest
import csv
import io
from igfb_agent.research_report import render_markdown, render_csv
from igfb_agent.research_backlog import research_backlog

class ResearchReportTests(unittest.TestCase):
    def test_empty_backlog_reports_all_55_years(self):
        report = render_markdown([])
        self.assertIn("0/55 (0.00%)", report)
        self.assertIn("| 1971 | discover_official_source | 0 | 0 | 0 |", report)
        self.assertIn("| 2025 | discover_official_source | 0 | 0 | 0 |", report)
        self.assertEqual(sum(line.startswith("| 19") or line.startswith("| 20") for line in report.splitlines()), 55)

    def test_csv_has_one_row_per_season_and_no_approvals(self):
        rows = list(csv.DictReader(io.StringIO(render_csv([]))))
        self.assertEqual(len(rows), 55)
        self.assertEqual({int(row["year"]) for row in rows}, set(range(1971, 2026)))
        self.assertTrue(all(row["approved"] == "false" for row in rows))
        self.assertTrue(all(row["stage"] == "discover_official_source" for row in rows))

    def test_csv_preserves_current_source_ids(self):
        rows = list(csv.DictReader(io.StringIO(render_csv())))
        self.assertEqual(len(rows), 55)
        self.assertTrue(any(row["source_ids"] for row in rows))
        self.assertTrue(all(row["approved"] == "false" for row in rows))

    def test_real_sources_do_not_imply_approval(self):
        report = render_markdown()
        self.assertIn("Não é conclusão global", report)
        self.assertIn("archive_and_verify_source", report)
        current = research_backlog()
        self.assertIn("{}/{} ({:.2f}%)".format(
            current["seasons_with_leads"], current["total_seasons"],
            current["lead_coverage_percent"]), report)

if __name__ == "__main__":
    unittest.main()
