import hashlib
import tempfile
import unittest
from pathlib import Path
from igfb_agent.evidence_inventory import validate_evidence_inventory

class EvidenceInventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "evidence.txt").write_bytes(b"synthetic test evidence")
        self.item = {
            "evidence_id": "synthetic-1971", "file": "evidence.txt",
            "sha256": hashlib.sha256(b"synthetic test evidence").hexdigest(),
            "source_url": "https://www.cbf.com.br/teste", "source_id": "cbf-test",
            "year": 1971, "edition_id": "brasileirao:1971",
            "retrieved_at": "2026-11-23T12:00:00Z", "approved": False,
        }

    def verify(self, item=None):
        return validate_evidence_inventory(
            {"schema_version": 1, "evidence": [self.item if item is None else item]}, self.root
        )

    def test_valid_bytes_not_approved(self):
        result = self.verify()
        self.assertEqual(result["verified_archives"], 1)
        self.assertEqual(result["approved_results"], 0)

    def test_changed_bytes_rejected(self):
        (self.root / "evidence.txt").write_bytes(b"tampered")
        with self.assertRaises(ValueError):
            self.verify()

    def test_parent_path_rejected(self):
        with self.assertRaises(ValueError):
            self.verify({**self.item, "file": "../outside.txt"})

    def test_approved_archive_rejected(self):
        with self.assertRaises(ValueError):
            self.verify({**self.item, "approved": True})

    def test_out_of_scope_year_rejected(self):
        with self.assertRaises(ValueError):
            self.verify({**self.item, "year": 1970, "edition_id": "brasileirao:1970"})

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            validate_evidence_inventory(
                {"schema_version": 1, "evidence": [self.item, self.item]}, self.root
            )

    def test_missing_source_id_rejected(self):
        item = {**self.item}
        item.pop("source_id")
        with self.assertRaises(ValueError):
            self.verify(item)

    def test_invalid_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            self.verify({**self.item, "retrieved_at": "ontem"})

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            self.verify({**self.item, "retrieved_at": "2026-11-23T12:00:00"})

    def test_empty_inventory_is_valid_but_not_progress(self):
        result = validate_evidence_inventory({"schema_version": 1, "evidence": []}, self.root)
        self.assertEqual(result["verified_archives"], 0)

if __name__ == "__main__":
    unittest.main()
