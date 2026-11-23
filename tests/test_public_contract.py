import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from igfb_agent.public_export import build_public_data, export_public_data

class ContractTests(unittest.TestCase):
    def test_snapshot_integrity_and_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            export_public_data(d)
            manifest = json.loads((Path(d)/'manifest.json').read_text())
            for entry in manifest['datasets'].values():
                body = (Path(d)/entry['path']).read_bytes()
                self.assertEqual(hashlib.sha256(body).hexdigest(), entry['sha256'])
            self.assertIsNone(manifest['data_published_at'])
            self.assertEqual(len(manifest['source_commit']), 40)

    def test_unknown_is_never_zero(self):
        data = build_public_data()
        for club in data['clubs.json']['clubs']:
            for metric in ('titles','score','participations','relegations'):
                self.assertIsNone(club[metric])
        for edition in data['editions.json']['editions']:
            self.assertIsNone(edition['champion'])
        self.assertFalse(data['ranking.json']['publication_authorized'])

    def test_scope_and_sources(self):
        data = build_public_data()
        self.assertEqual([e['year'] for e in data['editions.json']['editions']], list(range(1971,2026)))
        sources = {s['id'] for s in data['sources.json']['sources']}
        for club in data['clubs.json']['clubs']:
            self.assertLessEqual(set(club['source_ids']), sources)
        self.assertEqual(data['coverage.json']['source_leads'], sum(c['lead_count'] for c in data['clubs.json']['clubs']))

    def test_invalid_provenance(self):
        for kwargs in ({'commit_sha':'bad'}, {'generated_at':'2026-11-23T00:00:00'}, {'generated_at':'2026-11-23T00:00:00-03:00'}):
            with self.assertRaises(ValueError): build_public_data(**kwargs)

    def test_content_id_stable_across_build_times(self):
        a=build_public_data(generated_at='2026-11-23T00:00:00Z')
        b=build_public_data(generated_at='2026-11-23T01:00:00Z')
        self.assertEqual(a['manifest.json']['dataset_id'],b['manifest.json']['dataset_id'])
