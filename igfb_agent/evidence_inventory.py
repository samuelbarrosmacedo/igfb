"""Inventário verificável de evidências arquivadas, sem homologação automática."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

def validate_evidence_inventory(payload, root):
    """Exige bytes locais, SHA-256 real e procedência explícita."""
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("Versão do inventário inválida")
    entries = payload.get("evidence")
    if not isinstance(entries, list):
        raise ValueError("Lista de evidências inválida")
    base = Path(root).resolve()
    seen = set()
    checked = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Evidência inválida")
        eid, rel, digest = (entry.get(k) for k in ("evidence_id", "file", "sha256"))
        if not isinstance(eid, str) or not eid.strip() or eid in seen:
            raise ValueError("ID de evidência inválido ou duplicado")
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or "\\" in rel:
            raise ValueError("Caminho de evidência inválido")
        target = (base / rel).resolve()
        if not target.is_relative_to(base) or not target.is_file():
            raise ValueError("Arquivo ausente ou fora do inventário")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("SHA-256 inválido")
        url = entry.get("source_url")
        if not isinstance(url, str):
            raise ValueError("URL de origem inválida")
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
            raise ValueError("URL de origem inválida")
        year = entry.get("year")
        if type(year) is not int or not 1971 <= year <= 2025:
            raise ValueError("Ano fora do recorte")
        if entry.get("edition_id") != f"brasileirao:{year}":
            raise ValueError("Edição inválida")
        if not isinstance(entry.get("retrieved_at"), str) or not entry["retrieved_at"].strip():
            raise ValueError("Data de coleta ausente")
        if entry.get("approved") is not False:
            raise ValueError("Arquivamento não é homologação")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError("SHA-256 divergente: " + eid)
        seen.add(eid)
        checked.append({"evidence_id": eid, "year": year, "sha256": actual, "verified_bytes": True})
    return {"schema_version": 1, "verified_archives": len(checked), "approved_results": 0, "evidence": checked}

def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Verificar bytes arquivados e hashes")
    parser.add_argument("inventory")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    print(json.dumps(validate_evidence_inventory(payload, args.root), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
