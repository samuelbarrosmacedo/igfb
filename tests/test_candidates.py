import unittest
from igfb_agent.candidates import build_candidates, validate_leads

def lead(years):
    return {"schema_version": 1, "status": "source_leads_not_homologated",
            "sources": [{"source_id": "source1", "url": "https://www.cbf.com.br/record",
                         "publisher": "CBF", "source_type": "official",
                         "claim_club": "clube", "claim_years": years}]}

class CandidatesTests(unittest.TestCase):
    def test_real_leads_are_unapproved(self):
        records = build_candidates()
        self.assertGreater(len(records), 0)
        self.assertTrue(all(r["approved"] is False for r in records))
        self.assertTrue(all(r["status"] == "candidate_requires_review" for r in records))

    def test_no_earlier_seasons(self):
        for year in (1937, 1959, 1967, 1970, 2026):
            with self.subTest(year=year), self.assertRaises(ValueError):
                validate_leads(lead([year]))

    def test_duplicate_source(self):
        payload = lead([1971])
        payload["sources"].append(payload["sources"][0].copy())
        with self.assertRaises(ValueError):
            validate_leads(payload)

    def test_invalid_scheme(self):
        payload = lead([1971])
        payload["sources"][0]["url"] = "http://www.cbf.com.br/record"
        with self.assertRaises(ValueError):
            validate_leads(payload)

    def test_rejects_non_cbf_domain(self):
        payload = lead([1971])
        payload["sources"][0]["url"] = "https://cbf.com.br.evil.example/record"
        with self.assertRaises(ValueError):
            validate_leads(payload)

    def test_rejects_duplicate_year(self):
        with self.assertRaises(ValueError):
            validate_leads(lead([1971, 1971]))

    def test_rejects_non_string_url(self):
        payload = lead([1971])
        payload["sources"][0]["url"] = None
        with self.assertRaises(ValueError):
            validate_leads(payload)

    def test_boolean_year_rejected(self):
        with self.assertRaises(ValueError):
            validate_leads(lead([True]))

    def test_unverified_flag(self):
        record = validate_leads(lead([1971]))[0]
        self.assertEqual(record["claim_verification"], "unverified")
        self.assertIs(record["source_archived"], False)

    def test_malformed_ipv6_url_rejected(self):
        payload = lead([1971])
        payload["sources"][0]["url"] = "https://[invalid/record"
        with self.assertRaises(ValueError):
            validate_leads(payload)

    def test_nonstandard_port_rejected(self):
        payload = lead([1971])
        payload["sources"][0]["url"] = "https://www.cbf.com.br:444/record"
        with self.assertRaises(ValueError):
            validate_leads(payload)

    def test_checked_page_does_not_approve_claim(self):
        payload = lead([1971])
        payload["sources"][0]["source_check_status"] = "page_content_checked_not_archived"
        candidate = validate_leads(payload)[0]
        self.assertTrue(candidate["source_page_checked"])
        self.assertFalse(candidate["source_archived"])
        self.assertEqual(candidate["claim_verification"], "unverified")

    def test_invalid_source_status(self):
        payload = lead([1971])
        payload["sources"][0]["source_check_status"] = "homologated"
        with self.assertRaises(ValueError):
            validate_leads(payload)

    def test_valid_1971(self):
        records = validate_leads(lead([1971]))
        self.assertEqual(records[0]["edition_id"], "brasileirao:1971")
        self.assertFalse(records[0]["approved"])

if __name__ == "__main__":
    unittest.main()
