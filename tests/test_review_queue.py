import unittest
from igfb_agent.review_queue import review_queue

def candidate(year, club, source):
    return {"year":year, "club_id":club, "source_id":source,
            "competition":"brasileirao", "edition_id":f"brasileirao:{year}",
            "outcome_claim":"champion", "approved":False,
            "status":"candidate_requires_review"}

class ReviewQueueTests(unittest.TestCase):
    def test_groups_same_club_sources(self):
        q = review_queue([candidate(2000,"A","s1"), candidate(2000,"A","s2")])
        self.assertEqual(len(q),1)
        self.assertEqual(q[0]["claims"][0]["source_count"],2)
        self.assertFalse(q[0]["has_competing_claims"])

    def test_competing_claims(self):
        q = review_queue([candidate(1987,"A","s1"),candidate(1987,"B","s2")])
        self.assertTrue(q[0]["has_competing_claims"])
        self.assertFalse(q[0]["approved"])

    def test_rejects_approved(self):
        c = candidate(2000,"A","s1")
        c["approved"] = True
        with self.assertRaises(ValueError):
            review_queue([c])

    def test_rejects_pre_1971(self):
        with self.assertRaises(ValueError):
            review_queue([candidate(1970,"A","s1")])

    def test_rejects_wrong_edition(self):
        c = candidate(2000,"A","s1")
        c["edition_id"] = "brasileirao:2001"
        with self.assertRaises(ValueError):
            review_queue([c])

    def test_empty(self):
        self.assertEqual(review_queue([]), ())

if __name__ == "__main__":
    unittest.main()
