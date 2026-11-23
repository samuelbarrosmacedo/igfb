import hashlib
import tempfile
import unittest
from pathlib import Path
from igfb_agent.archive import verify_archive
from igfb_agent.registry import Evidence

class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = b"original historical source bytes"
        self.ev = Evidence("doc-1", "https://example.org/record",
                           hashlib.sha256(self.data).hexdigest(), "official")

    def test_matching_hash(self):
        (self.root / "doc-1.bin").write_bytes(self.data)
        self.assertEqual(verify_archive([self.ev], self.root), {"doc-1": "verified"})

    def test_missing_file(self):
        self.assertEqual(verify_archive([self.ev], self.root, strict=False), {"doc-1": "missing"})
        with self.assertRaises(ValueError):
            verify_archive([self.ev], self.root)

    def test_tampered_file(self):
        (self.root / "doc-1.bin").write_bytes(self.data + b"changed")
        self.assertEqual(verify_archive([self.ev], self.root, strict=False), {"doc-1": "mismatch"})
        with self.assertRaises(ValueError):
            verify_archive([self.ev], self.root)

    def test_reject_path_traversal(self):
        ev = Evidence("../escape", "https://example.org", self.ev.sha256, "official")
        with self.assertRaises(ValueError):
            verify_archive([ev], self.root)

    def test_empty_catalog(self):
        self.assertEqual(verify_archive([], self.root), {})

if __name__ == "__main__":
    unittest.main()
