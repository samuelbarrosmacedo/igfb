import json
from hashlib import sha256
import tempfile
import unittest
from pathlib import Path
from igfb_agent.public_export import build_public_data, export_public_data, verify_public_data

class PublicExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.inventory = self.root / "inventory.json"
        self.inventory.write_text(json.dumps({"schema_version": 1, "evidence": []}), encoding="utf-8")
        self.status = self.root / "status.json"
        self.status.write_text(json.dumps({
            "progress_percent_estimate": 38,
            "progress_audited": False,
            "approved_records": 0
        }), encoding="utf-8")

    def test_explicit_inventory_with_archived_candidate(self):
        from igfb_agent.candidates import build_candidates
        candidate = build_candidates()[0]
        blob = b"synthetic evidence fixture"
        (self.root / "fixture.txt").write_bytes(blob)
        self.inventory.write_text(json.dumps({"schema_version": 1, "evidence": [{
            "evidence_id": "fixture", "file": "fixture.txt",
            "sha256": sha256(blob).hexdigest(),
            "source_id": candidate["source_id"], "source_url": candidate["source_url"],
            "year": candidate["year"], "edition_id": candidate["edition_id"],
            "retrieved_at": "2026-11-24T12:00:00+00:00", "approved": False
        }]}), encoding="utf-8")
        folder = self.root / "data"
        export_public_data(folder, candidates=[candidate], status_path=self.status,
                           inventory_path=self.inventory, evidence_root=self.root)
        self.assertTrue(verify_public_data(folder))
        coverage = json.loads((folder / "coverage.json").read_text(encoding="utf-8"))
        self.assertEqual(coverage["verified_archives"], 1)
        self.assertEqual(coverage["archived_candidate_count"], 1)
        self.assertEqual(coverage["approved_results"], 0)

    def test_empty_export_never_publishes_ranking(self):
        files = build_public_data(candidates=[], status_path=self.status, inventory_path=self.inventory, evidence_root=self.root)
        self.assertEqual(files["ranking.json"]["ranking"], [])
        self.assertEqual(len(files["research-backlog.json"]["tasks"]), 55)
        self.assertEqual(files["ranking.json"]["approved_results"], 0)
        self.assertEqual(files["coverage.json"]["lead_coverage_percent"], 0.0)
        self.assertEqual(files["coverage.json"]["seasons_without_leads"], list(range(1971, 2026)))

    def test_legacy_percentage_is_not_audited(self):
        files = build_public_data(candidates=[], status_path=self.status, inventory_path=self.inventory, evidence_root=self.root)
        self.assertEqual(files["project-status.json"]["progress"]["percent"], 38)
        self.assertFalse(files["project-status.json"]["progress"]["usable_as_completion_metric"])
        self.assertEqual(files["project-status.json"]["measured_progress"]["percent"], 0.0)
        self.assertEqual(files["project-status.json"]["measured_progress"]["denominator"], 55)

    def test_export_files_match_manifest(self):
        folder = self.root / "data"
        exported = export_public_data(folder, candidates=[], status_path=self.status, inventory_path=self.inventory, evidence_root=self.root)
        self.assertEqual(len(exported), 7)
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest["files"]), set(exported) - {"manifest.json"})
        for filename, expected in manifest["sha256"].items():
            self.assertEqual(sha256((folder / filename).read_bytes()).hexdigest(), expected)
        self.assertEqual(set(manifest["sha256"]), set(manifest["files"]))
        for filename in exported:
            self.assertEqual(json.loads((folder / filename).read_text(encoding="utf-8"))["schema_version"], 1)

    def test_real_leads_remain_unapproved(self):
        files = build_public_data(status_path=self.status)
        self.assertGreater(files["coverage.json"]["source_leads"], 0)
        self.assertGreater(files["coverage.json"]["lead_coverage_percent"], 0)
        self.assertEqual(files["ranking.json"]["ranking"], [])

    def test_verified_export(self):
        folder = self.root / "data"
        export_public_data(folder, candidates=[], status_path=self.status, inventory_path=self.inventory, evidence_root=self.root)
        self.assertTrue(verify_public_data(folder))

    def test_tampered_dataset_is_rejected(self):
        folder = self.root / "data"
        export_public_data(folder, candidates=[], status_path=self.status, inventory_path=self.inventory, evidence_root=self.root)
        target = folder / "coverage.json"
        target.write_bytes(target.read_bytes() + b" ")
        with self.assertRaises(ValueError):
            verify_public_data(folder)

    def test_manifest_path_traversal_is_rejected(self):
        folder = self.root / "data"
        export_public_data(folder, candidates=[], status_path=self.status, inventory_path=self.inventory, evidence_root=self.root)
        manifest_path = folder / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"][0] = "../outside.json"
        manifest["sha256"]["../outside.json"] = manifest["sha256"].pop("project-status.json")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_public_data(folder)

    def test_unhashable_manifest_filename_is_rejected_cleanly(self):
        folder = self.root / "data"
        export_public_data(folder, candidates=[], status_path=self.status, inventory_path=self.inventory, evidence_root=self.root)
        path = folder / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["files"][0] = {"not": "a filename"}
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_public_data(folder)

    def test_missing_ranking_in_manifest_is_rejected(self):
        folder = self.root / "data"
        export_public_data(folder, candidates=[], status_path=self.status, inventory_path=self.inventory, evidence_root=self.root)
        path = folder / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["files"].remove("ranking.json")
        manifest["sha256"].pop("ranking.json")
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_public_data(folder)

    def test_invalid_audited_status_blocks_export(self):
        self.status.write_text(json.dumps({
            "progress_percent_estimate": 38, "progress_audited": True,
            "approved_records": 0
        }), encoding="utf-8")
        with self.assertRaises(ValueError):
            export_public_data(self.root / "data", candidates=[], status_path=self.status, inventory_path=self.inventory, evidence_root=self.root)
        self.assertFalse((self.root / "data").exists())

if __name__ == "__main__":
    unittest.main()
