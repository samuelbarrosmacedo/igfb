"""Contrato público v2. Exporta pesquisa, nunca homologa ou fabrica ranking.

Amplia o exportador v1. Snapshots endereçados por conteúdo evitam misturar
arquivos de publicações diferentes. O manifesto é sempre gravado por último.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from .project_audit import audit_project
from .source_readiness import source_readiness
from .review_queue import review_queue
from .research_backlog import research_backlog
from .evidence_reconciliation import reconcile_evidence
from .candidates import build_candidates, LEADS
from .calendar import brasileirao_editions
from .scoring import WEIGHTS, BASELINE_YEAR, THROUGH_YEAR

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 2
PUBLIC_FILES = ("project-status.json", "coverage.json", "methodology.json", "review-queue.json", "ranking.json", "clubs.json", "editions.json", "sources.json", "research-backlog.json")
REPO = "https://github.com/samuelbarrosmacedo/igfb"


def encode(payload):
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def source_commit():
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def build_public_data(*, candidates=None, status_path=None, commit_sha=None, generated_at=None):
    records = tuple(build_candidates() if candidates is None else candidates)
    evidence = reconcile_evidence(candidates=records)
    records = tuple(evidence["candidates"])
    inventory = json.loads((ROOT / "config/evidence_inventory.json").read_text(encoding="utf-8"))["evidence"]
    audit = audit_project(status_path=status_path, candidates=records)
    readiness = source_readiness(records)
    queue = review_queue(records)
    rules = json.loads((ROOT / "config/project_rules.json").read_text(encoding="utf-8"))
    if (rules["baseline_year"], rules["through_year"]) != (BASELINE_YEAR, THROUGH_YEAR):
        raise ValueError("Regras divergem do núcleo matemático")
    if set(rules["excluded"]) != {"Taça Brasil", "Robertão", "1937"}:
        raise ValueError("Exclusões históricas obrigatórias ausentes")
    commit = commit_sha or source_commit()
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise ValueError("Commit SHA inválido")
    generated = generated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    parsed = datetime.fromisoformat(generated.replace("Z", "+00:00"))
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("Geração exige UTC")
    labels = json.loads((ROOT / "config/public_labels.json").read_text(encoding="utf-8"))
    lead_sources = json.loads(LEADS.read_text(encoding="utf-8"))["sources"]
    known_sources = {s["source_id"]: s for s in lead_sources}
    for r in records:
        if r["source_id"] not in known_sources or r["source_url"] != known_sources[r["source_id"]]["url"]:
            raise ValueError("Fonte pública sem procedência no catálogo")
    source_ids = sorted({r["source_id"] for r in records})
    counts = Counter(r["club_id"] for r in records)
    club_ids = sorted(counts)
    checked = {r["source_id"] for r in records if r["source_page_checked"]}
    by_year = {row["year"]: row for row in queue}
    documents = {}
    def add(name, **payload):
        documents[name + ".json"] = {"schema_version": SCHEMA_VERSION, **payload}
    add("project-status", stage="research_in_progress", progress=audit["legacy_progress"],
        measured_progress=audit["measured_progress"], approved_results=0, scope=audit["scope"], audit_status="research_state_checked_results_not_homologated",
        last_collection_at=json.loads((Path(status_path) if status_path else ROOT / "state/status.json").read_text()).get("last_run_utc"),
        ranking_publication="blocked", publication_reason="Sem decisões homologadas e sem autorização expressa de publicação.")
    add("coverage", source_leads=readiness["total_candidates"], seasons_with_leads=readiness["distinct_years_with_leads"],
        seasons_without_leads=readiness["years_without_leads"], checked_source_pages=len(checked),
        source_ids_without_archived_bytes=readiness["source_ids_without_archived_bytes"], approved_results=0,
        catalogued_sources=len(source_ids), distinct_source_urls=len({known_sources[sid]["url"] for sid in source_ids}),
        archived_evidence_documents=evidence["verified_archives"], verified_archives=evidence["verified_archives"],
        archived_candidate_count=evidence["archived_candidate_count"],
        lead_coverage_percent=audit["measured_progress"]["percent"],
        coverage_metric="temporadas com pelo menos uma pista / 55; não mede homologação",
        archive_status="inventory_verified", review_editions=len(queue),
        competing_claim_editions=audit["competing_claim_editions"],
        denominator="55 temporadas do calendário da Série A; não mede conclusão global nem cobertura de outros torneios.")
    add("methodology", weights_status="experimental", weights=WEIGHTS, scope=audit["scope"],
        exclusions=rules["excluded"], flamengo_1987=rules["flamengo_1987"],
        competition_labels=labels["competitions"], outcome_labels=labels["outcomes"],
        documents=[{"path": p, "url": f"{REPO}/blob/{commit}/{p}",
                    "sha256": sha256((ROOT / p).read_bytes()).hexdigest(),
                    "markdown": (ROOT / p).read_text(encoding="utf-8")} for p in
                   ["docs/PROTOCOLO_AUDITORIA.md", "docs/DECISOES_HOMOLOGACAO.md"]])
    add("review-queue", status="manual_review_required", items=list(queue))
    backlog = research_backlog(records)
    backlog["schema_version"] = SCHEMA_VERSION
    documents["research-backlog.json"] = backlog
    add("ranking", status="unavailable_pending_homologation", approved_results=0,
        publication_authorized=False, ranking=[],
        reason="Ranking histórico em construção. A publicação depende da homologação documental dos resultados.")
    add("clubs", status="identities_from_source_leads", scope_note="Identidades presentes nas pistas; não é um cadastro completo dos clubes brasileiros.",
        clubs=[{"id": cid, "name": labels["clubs"].get(cid, cid.replace("_", " ").title()),
                "identity_status": "source_lead_identity", "crest": None,
                "lead_count": counts[cid], "source_ids": sorted({r["source_id"] for r in records if r["club_id"] == cid}),
                "years_with_leads": sorted({r["year"] for r in records if r["club_id"] == cid}),
                "titles": None, "score": None, "participations": None, "relegations": None}
               for cid in club_ids])
    add("editions", status="calendar_with_research_states", competition="brasileirao",
        editions=[{"id": e.edition_id, "year": e.year, "competition": e.competition,
                   "evidence_state": ("archived_pending_review" if e.year in by_year and all(r["source_archived"] for r in records if r["year"] == e.year) else "lead_found" if e.year in by_year else "no_lead"),
                   "source_ids": sorted({r["source_id"] for r in records if r["year"] == e.year}),
                   "has_competing_claims": by_year.get(e.year, {}).get("has_competing_claims", False),
                   "approved_results": 0, "champion": None} for e in brasileirao_editions()])
    add("sources", status="source_leads_not_homologated",
        sources=[{"id": sid, "url": known_sources[sid]["url"], "publisher": known_sources[sid]["publisher"],
                  "note": known_sources[sid]["note"], "checked_on": known_sources[sid].get("source_checked_on"),
                  "state": ("archived_pending_review" if all(r["source_archived"] for r in records if r["source_id"] == sid) else "partially_archived" if any(r["source_archived"] for r in records if r["source_id"] == sid) else "page_checked_not_archived" if sid in checked else "unverified_lead"),
                  "archives": [{"evidence_id": a["evidence_id"], "year": a["year"], "sha256": a["sha256"], "retrieved_at": a["retrieved_at"]} for a in inventory if a["source_id"] == sid],
                  "archived_sha256": None, "approved": False,
                  "club_ids": sorted({r["club_id"] for r in records if r["source_id"] == sid}),
                  "years": sorted({r["year"] for r in records if r["source_id"] == sid})} for sid in source_ids])
    digest = sha256(encode(documents)).hexdigest()
    hashes = {filename: sha256(encode(doc)).hexdigest() for filename, doc in documents.items()}
    manifest = {"schema_version": SCHEMA_VERSION, "dataset_status": "research_in_progress", "approved_results": 0,
                "source_commit": commit, "generated_at": generated, "data_published_at": None,
                "dataset_id": digest, "scope": audit["scope"],
                "audit_status": "research_state_checked_results_not_homologated",
                "files": list(documents), "sha256": hashes,
                "datasets": {filename: {"path": f"snapshots/{digest}/{filename}", "sha256": hashes[filename],
                             "availability": "withheld" if filename == "ranking.json" else "available"} for filename in documents}}
    return {"manifest.json": manifest, **documents}


def export_public_data(output_dir, **kwargs):
    documents = build_public_data(**kwargs)  # Validate everything before touching the destination.
    destination = Path(output_dir)
    snapshot = destination / "snapshots" / documents["manifest.json"]["dataset_id"]
    snapshot.mkdir(parents=True, exist_ok=True)
    for filename, payload in documents.items():
        if filename == "manifest.json":
            continue
        for parent in (snapshot, destination):
            target = parent / filename
            temporary = parent / (filename + ".tmp")
            temporary.write_bytes(encode(payload))
            temporary.replace(target)
    temporary = destination / "manifest.json.tmp"
    temporary.write_bytes(encode(documents["manifest.json"]))
    temporary.replace(destination / "manifest.json")
    return tuple(documents)


def verify_public_data(directory):
    """Verifica manifesto e bytes de todos os datasets, sem confiar nos nomes recebidos."""
    folder = Path(directory)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    files = manifest.get("files")
    hashes = manifest.get("sha256")
    if manifest.get("schema_version") != SCHEMA_VERSION or not isinstance(files, list) or not isinstance(hashes, dict):
        raise ValueError("Manifesto público inválido")
    if any(not isinstance(name, str) for name in files):
        raise ValueError("Nome de dataset inválido")
    if len(files) != len(set(files)) or set(files) != set(hashes):
        raise ValueError("Arquivos e hashes inconsistentes")
    for name in files:
        if not isinstance(name, str) or not name.endswith(".json") or Path(name).name != name or name == "manifest.json":
            raise ValueError("Nome de dataset inválido")
        expected = hashes[name]
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            raise ValueError("Hash inválido")
        actual = sha256((folder / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("Integridade de dataset comprometida: " + name)
    if set(files) != set(PUBLIC_FILES):
        raise ValueError("Contrato público incompleto")
    ranking = json.loads((folder / "ranking.json").read_text(encoding="utf-8"))
    if ranking.get("ranking") != [] or ranking.get("approved_results") != 0:
        raise ValueError("Ranking não homologado não pode ser publicado")
    datasets = manifest.get("datasets", {})
    digest = manifest.get("dataset_id", "")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest) or set(datasets) != set(PUBLIC_FILES):
        raise ValueError("Snapshot inválido")
    for name in files:
        entry = datasets[name]
        if entry.get("path") != f"snapshots/{digest}/{name}" or entry.get("sha256") != hashes[name]:
            raise ValueError("Referência de snapshot inválida")
        snapshot = (folder / entry["path"]).resolve()
        if not snapshot.is_relative_to(folder.resolve()) or sha256(snapshot.read_bytes()).hexdigest() != hashes[name]:
            raise ValueError("Integridade do snapshot comprometida")
    if ranking.get("publication_authorized") is not False:
        raise ValueError("Ranking não autorizado")
    return True

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(ROOT / "web/public/data"))
    parser.add_argument("--commit-sha")
    args = parser.parse_args(argv)
    files = export_public_data(args.output, commit_sha=args.commit_sha)
    print(json.dumps({"exported": list(files), "approved_results": 0}, ensure_ascii=False))

if __name__ == "__main__":
    main()
