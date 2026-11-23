import json
import tempfile
import unittest
from pathlib import Path
from igfb_agent.project_audit import audit_project

class ProjectAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "status.json"
        self.status = {"progress_percent_estimate": 38,
                       "progress_audited": False, "approved_records": 0}
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.status), encoding="utf-8")

    def test_empty_leads(self):
        report = audit_project(status_path=self.path, candidates=[])
        self.assertEqual(report["scope"]["seasons"], 55)
        self.assertEqual(len(report["seasons_without_leads"]), 55)
        self.assertEqual(report["approved_records"], 0)
        self.assertFalse(report["legacy_progress"]["usable_as_completion_metric"])

    def test_actual_leads_remain_unapproved(self):
        report = audit_project(status_path=self.path)
        self.assertGreater(report["source_leads"], 0)
        self.assertEqual(report["approved_records"], 0)

    def test_rejects_falsely_audited_progress(self):
        self.status["progress_audited"] = True
        self.save()
        with self.assertRaises(ValueError):
            audit_project(status_path=self.path, candidates=[])

    def test_rejects_unreconciled_approved_count(self):
        self.status["approved_records"] = 1
        self.save()
        with self.assertRaises(ValueError):
            audit_project(status_path=self.path, candidates=[])

    def test_rejects_boolean_percentage(self):
        self.status["progress_percent_estimate"] = True
        self.save()
        with self.assertRaises(ValueError):
            audit_project(status_path=self.path, candidates=[])

    def test_rejects_approved_candidate(self):
        candidate = {"year": 2000, "club_id": "X", "source_id": "s1",
                     "competition": "brasileirao", "edition_id": "brasileirao:2000",
                     "outcome_claim": "champion", "status": "candidate_requires_review",
                     "approved": True}
        with self.assertRaises(ValueError):
            audit_project(status_path=self.path, candidates=[candidate])

if __name__ == "__main__":
    unittest.main()
