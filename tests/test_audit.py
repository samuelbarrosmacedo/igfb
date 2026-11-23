import copy
import unittest
from igfb_agent.scoring import Result, WEIGHTS
from igfb_agent.audit import detect_conflicts, weighted_totals, sensitivity_envelope

def result(club, outcome, competition="brasileirao", year=2000):
    return Result(club, year, competition, outcome, "source", True)

class AuditTests(unittest.TestCase):
    def test_conflicting_placements(self):
        issues = detect_conflicts([result("A","champion"), result("A","runner_up")])
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].kind, "incompatible_outcomes")
        with self.assertRaises(ValueError):
            weighted_totals([result("A","champion"), result("A","runner_up")])

    def test_two_champions(self):
        issues = detect_conflicts([result("A","champion"),result("B","champion")])
        self.assertEqual(issues[0].kind, "multiple_champions")

    def test_duplicate_evidence(self):
        self.assertEqual(weighted_totals([result("A","champion"),result("A","champion")]), {"A":450.0})

    def test_sensitivity(self):
        scenario = copy.deepcopy(WEIGHTS)
        scenario["brasileirao"]["champion"] = 600
        bounds = sensitivity_envelope([result("A","champion")],[WEIGHTS,scenario])
        self.assertEqual(bounds["A"],{"min":450.0,"max":600.0})

    def test_state_titles_are_not_globally_exclusive(self):
        records = [result("A", "champion", "estadual"), result("B", "champion", "estadual")]
        self.assertEqual(detect_conflicts(records), [])

    def test_sensitivity_accepts_iterator(self):
        scenario = copy.deepcopy(WEIGHTS)
        scenario["brasileirao"]["champion"] = 500
        records = iter([result("A", "champion")])
        self.assertEqual(sensitivity_envelope(records, [WEIGHTS, scenario])["A"], {"min":450.0,"max":500.0})

    def test_distinct_editions_same_year(self):
        a = Result("A", 2000, "estadual", "champion", "doc1", True, "estadual:rj:2000")
        b = Result("A", 2000, "estadual", "champion", "doc2", True, "estadual:sp:2000")
        self.assertEqual(weighted_totals([a, b]), {"A":50.0})

    def test_same_edition_conflict(self):
        a = Result("A", 2000, "libertadores", "champion", "doc1", True, "lib:2000")
        b = Result("B", 2000, "libertadores", "champion", "doc2", True, "lib:2000")
        self.assertEqual(detect_conflicts([a, b])[0].kind, "multiple_champions")

    def test_distinct_editions_no_false_conflict(self):
        a = Result("A", 2000, "libertadores", "champion", "doc1", True, "lib:2000:a")
        b = Result("B", 2000, "libertadores", "champion", "doc2", True, "lib:2000:b")
        self.assertEqual(detect_conflicts([a, b]), [])

    def test_empty_scenarios(self):
        with self.assertRaises(ValueError):
            sensitivity_envelope([],[])

    def test_nonfinite_weight(self):
        scenario = copy.deepcopy(WEIGHTS)
        scenario["brasileirao"]["champion"] = float("nan")
        with self.assertRaises(ValueError):
            weighted_totals([result("A","champion")],scenario)

if __name__ == "__main__":
    unittest.main()
