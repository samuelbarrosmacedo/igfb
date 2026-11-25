"""Fixtures isoladas: nunca exportadas para web/public/data."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from igfb_agent.observatory import ROOT, build_observatory, validate_catalog
from igfb_agent.public_export import build_public_data
from igfb_agent.scoring import Result, score_results

class ObservatoryTests(unittest.TestCase):
    def setUp(self):
        self.catalog=json.loads((ROOT/'config/observatory.json').read_text())
        self.source={'id':'fixture-source','url':'https://example.org/fixture','publisher':'Fonte sintética','note':'Somente teste','checked_on':None}
        self.catalog['sources'].append(self.source)
        self.edition={'id':'brasileirao:2027','competition_id':'brasileirao','year':2027,'label':'2027','status':'ongoing','format':'league','participant_ids':['flamengo','botafogo'],'source_ids':['fixture-source'],'updated_at':'2027-01-01T00:00:00Z'}
        self.catalog['editions'].append(self.edition)
        self.record={'id':'fixture-match','edition_id':self.edition['id'],'kind':'match','status':'provisional','club_ids':['flamengo','botafogo'],'source_ids':['fixture-source'],'label':'Partida fictícia','phase':None,'position':None,'value':None,'unit':None,'home_score':1,'away_score':None,'played_at':None,'updated_at':'2027-01-01T00:00:00Z','revision':1,'revision_note':'Fixture isolada'}
        self.catalog['records'].append(self.record)

    def build(self, year=2027):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'catalog.json';path.write_text(json.dumps(self.catalog))
            return build_observatory(catalog_path=path,current_year=year)

    def test_github_reconciliation_populates_55_provisional_results(self):
        # Use the committed research file as the source; do not manufacture titles.
        import collections
        catalog=build_observatory(current_year=2026)
        history=[r for r in catalog["records"] if r["id"].endswith(":champion-crosscheck")]
        self.assertEqual(len(history),55)
        self.assertEqual(len({r["edition_id"] for r in history}),55)
        self.assertEqual(collections.Counter(r["status"] for r in history),{"provisional":54,"disputed":1})
        self.assertEqual(len([e for e in catalog["editions"] if e["competition_id"]=="brasileirao"]),55)
        self.assertTrue(any(c["id"]=="sport" for c in catalog["clubs"]))
        disputed=next(r for r in history if r["edition_id"]=="brasileirao:1987")
        self.assertEqual(disputed["club_ids"],["sport","flamengo"])
        self.assertIn("Flamengo* e Sport*",disputed["label"])
        self.assertEqual(disputed["status"],"disputed")
        self.assertTrue(all(r["value"] is None for r in history))
        documents=build_public_data(current_year=2026)
        self.assertEqual(documents["ranking.json"]["ranking"],[])
        self.assertEqual(documents["ranking.json"]["approved_results"],0)
        self.assertEqual(len(documents["observatory.json"]["records"]),55)

    def test_new_season_and_rollover_do_not_change_historical_scope(self):
        before=self.build(2026);after=self.build(2027)
        self.assertEqual(after['current_season'],2027)
        self.assertIn(2027,after['seasons'])
        self.assertEqual(before['historical_scope'],after['historical_scope'])
        self.assertEqual(after['historical_scope']['last_year'],2025)

    def test_competition_edition_and_club_are_extensible(self):
        club=copy.deepcopy(self.catalog['clubs'][0]);club.update(id='fixture-club',name='Clube sintético',crest=None)
        self.catalog['clubs'].append(club)
        comp=copy.deepcopy(self.catalog['competitions'][0]);comp.update(id='fixture-cup',name='Copa sintética')
        self.catalog['competitions'].append(comp)
        self.edition.update(id='fixture-cup:2027',competition_id=comp['id'],participant_ids=[club['id']])
        self.record['edition_id']=self.edition['id']
        self.assertEqual(next(e for e in self.build()['editions'] if e['id']=='fixture-cup:2027')['competition_id'],'fixture-cup')

    def test_closed_edition_does_not_homologate_results(self):
        self.edition['status']='finished';self.record['status']='official_final'
        self.assertEqual(self.build()['records'][0]['status'],'official_final')
        self.record['status']='homologated'
        with self.assertRaises(ValueError):self.build()

    def test_correction_changes_snapshot_and_preserves_ranking_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'catalog.json';path.write_text(json.dumps(self.catalog))
            first=build_public_data(catalog_path=path,current_year=2027)
            self.record.update(home_score=2,revision=2,revision_note='Correção sintética')
            path.write_text(json.dumps(self.catalog))
            second=build_public_data(catalog_path=path,current_year=2027)
        self.assertNotEqual(first['manifest.json']['dataset_id'],second['manifest.json']['dataset_id'])
        self.assertEqual(second['ranking.json']['ranking'],[])

    def test_crest_hash_is_checked_and_missing_crest_allowed(self):
        self.assertTrue(validate_catalog(self.catalog))
        club=next(c for c in self.catalog['clubs'] if c['crest'])
        club['crest']['sha256']='0'*64
        with self.assertRaises(ValueError):validate_catalog(self.catalog)
        club['crest']=None
        self.assertTrue(validate_catalog(self.catalog))

    def test_state_competition_requires_identity(self):
        c=next(c for c in self.catalog['competitions'] if c['jurisdiction']=='state')
        self.assertTrue(validate_catalog(self.catalog))
        c['state']=None
        with self.assertRaises(ValueError):validate_catalog(self.catalog)

    def test_rejects_unknown_references_and_unsourced_final(self):
        self.record['club_ids']=['not-catalogued']
        with self.assertRaises(ValueError):self.build()
        self.record['club_ids']=['flamengo'];self.record['status']='official_final'
        with self.assertRaises(ValueError):self.build()

    def test_incomplete_records_do_not_become_zero(self):
        self.assertIsNone(self.build()['records'][0]['away_score'])

    def test_ineligible_results_cannot_enter_historical_scoring(self):
        for competition,year in [('brasileirao',1970),('brasileirao',2026),('taca_brasil',1971),('robertao',1971),('1937',1937)]:
            with self.subTest(competition=competition,year=year),self.assertRaises(ValueError):
                score_results([Result('fixture',year,competition,'champion','fixture',True,'fixture')])

    def test_unsupported_version_and_duplicate_ids_fail(self):
        self.catalog['schema_version']=2
        with self.assertRaises(ValueError):self.build()
        self.catalog['schema_version']=1;self.catalog['editions'].append(self.edition)
        with self.assertRaises(ValueError):self.build()
