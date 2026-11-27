"""Import reviewed Commons SVGs into the canonical catalogue; run explicitly."""
import json
import xml.etree.ElementTree as ET
from hashlib import sha256
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from .observatory import ROOT, validate_catalog

def import_crests(root=ROOT):
    root = Path(root)
    path = root / "config/observatory.json"
    catalog = json.loads(path.read_text(encoding="utf-8"))
    sources = json.loads((root / "config/crest_sources.json").read_text(encoding="utf-8"))["sources"]
    clubs = {c["id"]: c for c in catalog["clubs"]}
    for source in sources:
        club = clubs[source["club_id"]]
        if club["crest"]:
            continue
        try:
            filename = source["file"]
            if not filename.endswith(".svg") or "/" in filename:
                raise ValueError("Invalid SVG filename")
            url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + quote(filename)
            request = Request(url, headers={"User-Agent": "IGFB/1.0 (https://github.com/samuelbarrosmacedo/igfb)"})
            with urlopen(request, timeout=30) as response:
                if urlparse(response.geturl()).hostname != "upload.wikimedia.org":
                    raise ValueError("Unexpected download host")
                data = response.read(2_000_001)
            if len(data) > 2_000_000 or b"<!ENTITY" in data.upper():
                raise ValueError(f"Unsafe SVG: {filename}")
            # Accept only the standard external SVG 1.0/1.1 declaration.
            # ElementTree does not fetch external DTDs; reject internal subsets.
            import re
            declaration = rb'<!DOCTYPE\s+svg\s+PUBLIC\s+["\x27]-//W3C//DTD SVG 1\.[01]//EN["\x27]\s+["\x27]https?://www\.w3\.org/Graphics/SVG/1\.[01]/DTD/svg1[01]\.dtd["\x27]\s*>'
            cleaned = re.sub(declaration, b"", data, count=1, flags=re.I)
            if b"<!DOCTYPE" in cleaned.upper():
                raise ValueError(f"Unexpected SVG DTD: {filename}")
            if ET.fromstring(cleaned).tag != "{http://www.w3.org/2000/svg}svg":
                raise ValueError("Not an SVG")
            digest = sha256(data).hexdigest()
            relative = f"assets/identities/{club['id']}-{digest[:12]}.svg"
            target = root / "web/public" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            club["crest"] = {"path": relative, "sha256": digest,
                             "source_url": source["source_url"], "license": source["license"],
                             "attribution": source["attribution"],
                             "usage_note": "Uso editorial de identificação; sem endosso. Arquivo sem alterações."}
            validate_catalog(catalog, root=root)
            print(f"Imported crest: {club['id']}")
        except (ValueError, OSError, ET.ParseError) as exc:
            club["crest"] = None
            print(f"::warning::Crest {club['id']} skipped: {exc}")
    validate_catalog(catalog, root=root)
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    import_crests()
