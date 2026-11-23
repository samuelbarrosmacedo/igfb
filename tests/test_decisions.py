import unittest
from dataclasses import replace
from igfb_agent.decisions import Decision, materialize_approved, validate_decisions
from igfb_agent.registry import Edition, Evidence

ED = [Edition("brasileirao:2000", "brasileirao", 2000, "Organizador em revisão")]
EV = [Evidence("archive-1", "https://example.org/archive", "a"*64, "official")]
D = Decision("approval-1", "brasileirao:2000", "clube_a", "champion",
             "archive-1", "reviewer-1", "2026-11-23T10:00:00Z",
             "Exemplo sintético para testes; não é homologação histórica")

class DecisionTests(unittest.TestCase):
    def test_empty_ledger_never_approves(self):
        self.assertEqual(materialize_approved([], ED, EV), ())

    def test_explicit_approval(self):
        records = materialize_approved([D], ED, EV)
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0].approved)

    def test_revocation(self):
        revoked = replace(D, decision_id="revoke-1", status="revoked",
                          supersedes="approval-1", decided_at="2026-11-24T10:00:00Z")
        self.assertEqual(materialize_approved([D, revoked], ED, EV), ())

    def test_revocation_without_prior_decision(self):
        rev = replace(D, decision_id="rev-1", status="revoked", supersedes="missing")
        with self.assertRaises(ValueError):
            materialize_approved([rev], ED, EV)

    def test_duplicate_id(self):
        with self.assertRaises(ValueError):
            validate_decisions([D, D], ED, EV)

    def test_missing_evidence(self):
        with self.assertRaises(ValueError):
            materialize_approved([replace(D, evidence_id="missing")], ED, EV)

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            materialize_approved([replace(D, decided_at="2026-11-23T10:00:00")], ED, EV)

    def test_conflicting_approvals_rejected(self):
        second = replace(D, decision_id="approval-2", club="clube_b")
        with self.assertRaises(ValueError):
            materialize_approved([D, second], ED, EV)

    def test_wrong_revocation_identity(self):
        rev = replace(D, decision_id="rev-1", status="revoked", supersedes="approval-1",
                      club="clube_b", decided_at="2026-11-24T10:00:00Z")
        with self.assertRaises(ValueError):
            materialize_approved([D, rev], ED, EV)

    def test_duplicate_revocation(self):
        rev = replace(D, decision_id="rev-1", status="revoked", supersedes="approval-1",
                      decided_at="2026-11-24T10:00:00Z")
        with self.assertRaises(ValueError):
            materialize_approved([D, rev, replace(rev, decision_id="rev-2")], ED, EV)

    def test_out_of_scope_edition(self):
        with self.assertRaises(ValueError):
            materialize_approved([D], [Edition("brasileirao:1970", "brasileirao", 1970, "X")], EV)

if __name__ == "__main__":
    unittest.main()
