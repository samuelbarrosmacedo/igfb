"""Confere o artefato publicado e seus bytes; não homologa resultados."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen
from urllib.parse import urljoin


def verify_publication(base_url, expected_manifest, *, read=None):
    def download(path):
        with urlopen(Request(urljoin(base_url, path), headers={'Cache-Control':'no-cache','User-Agent':'IGFB-publication-check/1.0'}), timeout=30) as response:
            return response.read()
    read = read or download
    if not base_url.startswith('https://') or not base_url.endswith('/'):
        raise ValueError('URL pública exige HTTPS e barra final')
    live=json.loads(read('data/manifest.json'))
    for field in ('schema_version','dataset_id','source_commit','generated_at'):
        if live.get(field)!=expected_manifest[field]:
            raise ValueError('Publicação anterior ou divergente: '+field)
    for name,entry in expected_manifest['datasets'].items():
        if sha256(read('data/'+entry['path'])).hexdigest()!=entry['sha256']:
            raise ValueError('Integridade divergente em produção: '+name)
    if b'<html' not in read('index.html').lower():
        raise ValueError('Entrada HTML indisponível')
    return {'source_commit':live['source_commit'],'dataset_id':live['dataset_id'],'datasets_verified':len(live['datasets'])}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='https://samuelbarrosmacedo.github.io/igfb/')
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--attempts',type=int,default=1)
    args=parser.parse_args()
    expected=json.loads(Path(args.manifest).read_text())
    for attempt in range(args.attempts):
        try:
            print(json.dumps(verify_publication(args.url,expected)))
            return
        except Exception as error:
            print(f'Tentativa {attempt+1}: {error}',flush=True)
            if attempt+1==args.attempts:raise
            time.sleep(10)

if __name__=='__main__':main()
