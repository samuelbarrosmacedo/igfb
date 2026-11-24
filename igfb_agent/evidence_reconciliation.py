"""Reconcilia inventário de arquivos verificados com pistas, sem homologá-las."""
import json
from pathlib import Path
from .candidates import build_candidates
from .evidence_inventory import validate_evidence_inventory

ROOT = Path(__file__).resolve().parents[1]

def reconcile_evidence(*, candidates=None, inventory_path=None, root=None):
    records = tuple(build_candidates() if candidates is None else candidates)
    base = Path(root) if root is not None else ROOT
    path = Path(inventory_path) if inventory_path is not None else base / "config/evidence_inventory.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    verified = validate_evidence_inventory(payload, base)
    by_id = {item["evidence_id"]: item for item in payload["evidence"]}
    known = {(r["source_id"], r["year"], r["source_url"]) for r in records}
    archived = set()
    for record in verified["evidence"]:
        item = by_id[record["evidence_id"]]
        source_id = item.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("Evidência sem ID de fonte")
        key = (source_id, item["year"], item["source_url"])
        if key not in known:
            raise ValueError("Evidência sem pista correspondente")
        archived.add((source_id, item["year"]))
    enriched = []
    for item in records:
        enriched.append({**item, "source_archived": (item["source_id"], item["year"]) in archived})
    return {
        "verified_archives": verified["verified_archives"],
        "archived_candidate_count": sum(r["source_archived"] for r in enriched),
        "approved_results": 0,
        "candidates": enriched,
    }

def main():
    from .research_backlog import research_backlog
    result = reconcile_evidence()
    backlog = research_backlog(result["candidates"])
    print(json.dumps({
        "verified_archives": result["verified_archives"],
        "archived_candidate_count": result["archived_candidate_count"],
        "seasons_with_leads": backlog["seasons_with_leads"],
        "lead_coverage_percent": backlog["lead_coverage_percent"],
        "approved_results": 0,
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
