import math
import unittest
from igfb_agent.scoring import Result, score_results, temporal_consistency, standardize_season, logistic_index

class ScoringTests(unittest.TestCase):
    def test_deduplication(self):
        a = Result("A", 2000, "brasileirao", "champion", "doc1", True)
        b = Result("A", 2000, "brasileirao", "champion", "doc2", True)
        self.assertEqual(score_results([a,b]), {"A":450.0})

    def test_unapproved(self):
        with self.assertRaises(ValueError):
            score_results([Result("A", 2001, "libertadores", "champion", "doc")])

    def test_cutoff(self):
        with self.assertRaises(ValueError):
            score_results([Result("A", 1968, "brasileirao", "champion", "doc", True)])

    def test_relegation(self):
        r = Result("A", 2002, "relegation_a_b", "relegated", "doc", True)
        self.assertEqual(score_results([r]), {"A":-400.0})

    def test_consistency(self):
        self.assertAlmostEqual(temporal_consistency([5,5,5]), 1.0)
        self.assertAlmostEqual(temporal_consistency([10,0,0,0]), .25)
        self.assertEqual(temporal_consistency([0,0]), 0)
        with self.assertRaises(ValueError):
            temporal_consistency([-1,2])

    def test_zscore(self):
        z = standardize_season({"A":1,"B":2,"C":3})
        self.assertAlmostEqual(sum(z.values()), 0)
        self.assertEqual(standardize_season({"A":4,"B":4}), {"A":0,"B":0})

    def test_logistic(self):
        self.assertEqual(logistic_index(0), 50)
        self.assertAlmostEqual(logistic_index(4)+logistic_index(-4), 100)
        self.assertTrue(math.isfinite(logistic_index(-1000)))
        self.assertTrue(math.isfinite(logistic_index(1000)))

if __name__ == "__main__":
    unittest.main()
