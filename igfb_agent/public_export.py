"""Exportação pública conservadora: pistas não se tornam resultados homologados."""
import argparse
import json
from pathlib import Path
from hashlib import sha256
from .project_audit import audit_project
from .source_readiness import source_readiness
from .review_queue import review_queue
from .candidates import build_candidates
from .scoring import WEIGHTS

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
PUBLIC_FILES = ("project-status.json", "coverage.json", "methodology.json", "review-queue.json", "ranking.json")

def build_public_data(*, candidates=None, status_path=None):
    records = tuple(build_candidates() if candidates is None else candidates)
    audit = audit_project(status_path=status_path, candidates=records)
    readiness = source_readiness(records)
    queue = review_queue(records)
    return {
        "manifest.json": {
            "schema_version": SCHEMA_VERSION,
            "dataset_status": "research_in_progress",
            "approved_results": 0,
            "files": list(PUBLIC_FILES),
            "warning": "Sem ranking homologado; não converter pistas em pontuação.",
        },
        "project-status.json": {
            "schema_version": SCHEMA_VERSION,
            "stage": "prototype",
            "progress": audit["legacy_progress"],
            "approved_results": 0,
            "scope": audit["scope"],
        },
        "coverage.json": {
            "schema_version": SCHEMA_VERSION,
            "source_leads": readiness["total_candidates"],
            "seasons_with_leads": readiness["distinct_years_with_leads"],
            "lead_coverage_percent": round(100 * readiness["distinct_years_with_leads"] / readiness["total_seasons"], 2),
            "coverage_metric": "temporadas com pelo menos uma pista / 55; não mede homologação",
            "seasons_without_leads": readiness["years_without_leads"],
            "checked_source_pages": readiness["checked_source_pages"],
            "source_ids_without_archived_bytes": readiness["source_ids_without_archived_bytes"],
            "approved_results": 0,
        },
        "methodology.json": {
            "schema_version": SCHEMA_VERSION,
            "weights_status": "experimental",
            "weights": WEIGHTS,
            "scope": audit["scope"],
            "flamengo_1987": "convenção metodológica, não consenso institucional",
        },
        "review-queue.json": {
            "schema_version": SCHEMA_VERSION,
            "status": "manual_review_required",
            "items": list(queue),
        },
        "ranking.json": {
            "schema_version": SCHEMA_VERSION,
            "status": "unavailable_pending_homologation",
            "approved_results": 0,
            "ranking": [],
        },
    }

def export_public_data(output_dir, *, candidates=None, status_path=None):
    destination = Path(output_dir)
    documents = build_public_data(candidates=candidates, status_path=status_path)
    # Serialize before writing, and publish the checksum manifest last.
    payloads = {name: (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
                for name, data in documents.items()}
    manifest = documents["manifest.json"]
    manifest["sha256"] = {name: sha256(blob).hexdigest()
                          for name, blob in payloads.items() if name != "manifest.json"}
    payloads["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    destination.mkdir(parents=True, exist_ok=True)
    for filename in (*manifest["files"], "manifest.json"):
        target = destination / filename
        temporary = destination / (filename + ".tmp")
        temporary.write_bytes(payloads[filename])
        temporary.replace(target)
    return tuple(documents)

def verify_public_data(directory):
    """Verifica manifesto e bytes de todos os datasets, sem confiar nos nomes recebidos."""
    folder = Path(directory)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    files = manifest.get("files")
    hashes = manifest.get("sha256")
    if manifest.get("schema_version") != SCHEMA_VERSION or not isinstance(files, list) or not isinstance(hashes, dict):
        raise ValueError("Manifesto público inválido")
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
    return True

def main(argv=None):
    parser = argparse.ArgumentParser(description="Exportar dados públicos do IGFB sem homologação automática")
    parser.add_argument("--output", default=str(ROOT / "web" / "public" / "data"))
    args = parser.parse_args(argv)
    files = export_public_data(args.output)
    print(json.dumps({"exported": list(files), "approved_results": 0}, ensure_ascii=False))

if __name__ == "__main__":
    main()
