import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from igfb_agent.evidence_reconciliation import reconcile_evidence
from igfb_agent.research_backlog import research_backlog

class EvidenceReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "doc.txt").write_bytes(b"synthetic")
        self.item = {
            "year": 1971, "edition_id": "brasileirao:1971", "competition": "brasileirao",
            "source_id": "cbf-test", "source_url": "https://www.cbf.com.br/teste",
            "status": "candidate_requires_review", "approved": False,
            "source_page_checked": True, "source_archived": False,
        }
        self.evidence = {
            "evidence_id": "doc-1971", "file": "doc.txt",
            "sha256": hashlib.sha256(b"synthetic").hexdigest(),
            "source_url": self.item["source_url"], "source_id": "cbf-test",
            "year": 1971, "edition_id": "brasileirao:1971",
            "retrieved_at": "2026-11-23T00:00:00Z", "approved": False,
        }

    def run_reconciliation(self, entries):
        path = self.root / "inventory.json"
        path.write_text(json.dumps({"schema_version": 1, "evidence": entries}), encoding="utf-8")
        return reconcile_evidence(candidates=[self.item], inventory_path=path, root=self.root)

    def test_verified_archive_changes_backlog_stage(self):
        result = self.run_reconciliation([self.evidence])
        self.assertEqual(result["verified_archives"], 1)
        self.assertEqual(result["archived_candidate_count"], 1)
        task = next(t for t in research_backlog(result["candidates"])["tasks"] if t["year"] == 1971)
        self.assertEqual(task["stage"], "manual_historical_review")
        self.assertFalse(result["candidates"][0]["approved"])

    def test_empty_inventory_keeps_archive_pending(self):
        result = self.run_reconciliation([])
        self.assertEqual(result["archived_candidate_count"], 0)
        self.assertFalse(result["candidates"][0]["source_archived"])

    def test_unmatched_source_rejected(self):
        with self.assertRaises(ValueError):
            self.run_reconciliation([{**self.evidence, "source_id": "unknown"}])

    def test_unmatched_url_rejected(self):
        with self.assertRaises(ValueError):
            self.run_reconciliation([{**self.evidence, "source_url": "https://www.cbf.com.br/other"}])

    def test_tampered_bytes_rejected(self):
        (self.root / "doc.txt").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.run_reconciliation([self.evidence])

if __name__ == "__main__":
    unittest.main()
