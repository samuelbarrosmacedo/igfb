import copy
import unittest
from igfb_agent.scoring import Result, WEIGHTS
from igfb_agent.registry import Edition, Evidence, validate_dataset, validate_catalog, score_verified
from igfb_agent.robustness import rank_scores, scenario_stability

HASH = "a"*64
E = Evidence("doc", "https://example.org/record", HASH, "official")
ED = Edition("br:2000", "brasileirao", 2000, "CBF")

def r(club, outcome="champion", edition="br:2000", year=2000, approved=True):
    return Result(club, year, "brasileirao", outcome, "doc", approved, edition)

class RegistryRobustnessTests(unittest.TestCase):
    def test_valid_dataset(self):
        self.assertEqual(validate_dataset([r("A")], [ED], [E]), (r("A"),))

    def test_verified_scoring(self):
        self.assertEqual(score_verified([r("A")], [ED], [E]), {"A":450.0})

    def test_verified_scoring_rejects_missing_evidence(self):
        with self.assertRaises(ValueError):
            score_verified([r("A")], [ED], [])

    def test_missing_edition(self):
        with self.assertRaises(ValueError):
            validate_dataset([r("A", edition="unknown")], [ED], [E])

    def test_mismatched_year(self):
        with self.assertRaises(ValueError):
            validate_dataset([r("A", year=2001)], [ED], [E])

    def test_missing_evidence(self):
        with self.assertRaises(ValueError):
            validate_dataset([r("A")], [ED], [])

    def test_unapproved(self):
        with self.assertRaises(ValueError):
            validate_dataset([r("A", approved=False)], [ED], [E])

    def test_two_champions(self):
        with self.assertRaises(ValueError):
            validate_dataset([r("A"), r("B")], [ED], [E])

    def test_state_requires_jurisdiction(self):
        with self.assertRaises(ValueError):
            validate_catalog([Edition("state:2000", "estadual", 2000, "Federação")], [E])

    def test_shared_champion_format_is_not_silently_supported(self):
        with self.assertRaises(ValueError):
            validate_catalog([Edition("special:2000", "brasileirao", 2000, "CBF", single_champion=False)], [E])

    def test_duplicate_edition(self):
        with self.assertRaises(ValueError):
            validate_catalog([ED, ED], [E])

    def test_invalid_hash(self):
        with self.assertRaises(ValueError):
            validate_catalog([ED], [Evidence("doc", "https://example.org", "xyz", "official")])

    def test_malformed_evidence_fields(self):
        malformed = [
            Evidence(None, "https://example.org", HASH, "official"),
            Evidence("doc", None, HASH, "official"),
            Evidence("doc", "https://example.org", None, "official"),
        ]
        for item in malformed:
            with self.subTest(item=item), self.assertRaises(ValueError):
                validate_catalog([ED], [item])

    def test_malformed_state_jurisdiction(self):
        with self.assertRaises(ValueError):
            validate_catalog([Edition("state:2000", "estadual", 2000, "Fed", None)], [E])

    def test_tie_ranks(self):
        self.assertEqual(rank_scores({"A":10,"B":10,"C":5}), {"A":1,"B":1,"C":3})

    def test_stability(self):
        altered = copy.deepcopy(WEIGHTS)
        altered["brasileirao"]["runner_up"] = 500
        out = scenario_stability([r("A"),r("B","runner_up")], [WEIGHTS, altered])
        self.assertEqual(out["A"]["rank_best"], 1)
        self.assertEqual(out["A"]["rank_worst"], 2)
        self.assertEqual(out["A"]["first_place_fraction"], .5)

    def test_iterator_reuse(self):
        out = scenario_stability(iter([r("A")]), [WEIGHTS, WEIGHTS])
        self.assertEqual(out["A"]["score_mean"], 450)

if __name__ == "__main__":
    unittest.main()
