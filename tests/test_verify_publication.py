import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from igfb_agent.public_export import export_public_data
from igfb_agent.verify_publication import verify_publication

class PublicationTests(unittest.TestCase):
    def test_verifies_complete_publication_and_rejects_stale_or_tampered_bytes(self):
        with TemporaryDirectory() as folder:
            path=Path(folder);export_public_data(path/'data')
            (path/'index.html').write_text('<html lang="pt-BR"></html>')
            manifest=json.loads((path/'data/manifest.json').read_text())
            read=lambda name:(path/name).read_bytes()
            self.assertEqual(verify_publication('https://example.org/',manifest,read=read)['datasets_verified'],10)
            wrong={**manifest,'source_commit':'0'*40}
            with self.assertRaises(ValueError):verify_publication('https://example.org/',wrong,read=read)
            target=path/'data'/manifest['datasets']['clubs.json']['path'];target.write_bytes(b'{}')
            with self.assertRaises(ValueError):verify_publication('https://example.org/',manifest,read=read)
