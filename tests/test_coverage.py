import unittest
from igfb_agent.coverage import measure_coverage
from igfb_agent.registry import Edition, Evidence
from igfb_agent.scoring import Result

ED = [Edition("br:2000", "brasileirao", 2000, "CBF"),
      Edition("br:2001", "brasileirao", 2001, "CBF")]
EV = [Evidence("doc", "https://example.org/source", "a"*64, "official")]

class CoverageTests(unittest.TestCase):
    def test_empty_catalog(self):
        x = measure_coverage([], [], [])
        self.assertEqual(x.registered_editions, 0)
        self.assertIsNone(x.approved_coverage_ratio)

    def test_empty_results(self):
        x = measure_coverage([], ED, EV)
        self.assertEqual(x.missing_edition_ids, ("br:2000", "br:2001"))
        self.assertEqual(x.approved_coverage_ratio, 0.0)

    def test_approved_and_pending(self):
        a = Result("A", 2000, "brasileirao", "champion", "doc", True, "br:2000")
        b = Result("B", 2001, "brasileirao", "runner_up", "doc", False, "br:2001")
        x = measure_coverage([a,b], ED, EV)
        self.assertEqual(x.approved_results, 1)
        self.assertEqual(x.pending_results, 1)
        self.assertEqual(x.editions_with_results, 2)
        self.assertEqual(x.approved_coverage_ratio, .5)

    def test_missing_evidence(self):
        r = Result("A", 2000, "brasileirao", "champion", "missing", True, "br:2000")
        with self.assertRaises(ValueError):
            measure_coverage([r], ED, EV)

    def test_wrong_edition(self):
        r = Result("A", 2000, "brasileirao", "champion", "doc", True, "br:2001")
        with self.assertRaises(ValueError):
            measure_coverage([r], ED, EV)

if __name__ == "__main__":
    unittest.main()
