import json
import tempfile
import unittest
from pathlib import Path
from igfb_agent.public_export import build_public_data, export_public_data

class PublicExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.status = self.root / "status.json"
        self.status.write_text(json.dumps({
            "progress_percent_estimate": 38,
            "progress_audited": False,
            "approved_records": 0
        }), encoding="utf-8")

    def test_empty_export_never_publishes_ranking(self):
        files = build_public_data(candidates=[], status_path=self.status)
        self.assertEqual(files["ranking.json"]["ranking"], [])
        self.assertEqual(files["ranking.json"]["approved_results"], 0)
        self.assertEqual(files["coverage.json"]["seasons_without_leads"], list(range(1971, 2026)))

    def test_legacy_percentage_is_not_audited(self):
        files = build_public_data(candidates=[], status_path=self.status)
        self.assertEqual(files["project-status.json"]["progress"]["percent"], 38)
        self.assertFalse(files["project-status.json"]["progress"]["usable_as_completion_metric"])

    def test_export_files_match_manifest(self):
        folder = self.root / "data"
        exported = export_public_data(folder, candidates=[], status_path=self.status)
        self.assertEqual(len(exported), 9)
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest["files"]), set(exported) - {"manifest.json"})
        for filename in exported:
            self.assertEqual(json.loads((folder / filename).read_text(encoding="utf-8"))["schema_version"], 2)

    def test_real_leads_remain_unapproved(self):
        files = build_public_data(status_path=self.status)
        self.assertGreater(files["coverage.json"]["source_leads"], 0)
        self.assertEqual(files["ranking.json"]["ranking"], [])

    def test_invalid_audited_status_blocks_export(self):
        self.status.write_text(json.dumps({
            "progress_percent_estimate": 38, "progress_audited": True,
            "approved_records": 0
        }), encoding="utf-8")
        with self.assertRaises(ValueError):
            export_public_data(self.root / "data", candidates=[], status_path=self.status)
        self.assertFalse((self.root / "data").exists())

if __name__ == "__main__":
    unittest.main()
