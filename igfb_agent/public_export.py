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
            "files": ["project-status.json", "coverage.json", "methodology.json", "review-queue.json", "ranking.json"],
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
    destination.mkdir(parents=True, exist_ok=True)
    for filename, payload in documents.items():
        target = destination / filename
        temporary = destination / (filename + ".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(target)
    return tuple(documents)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Exportar dados públicos do IGFB sem homologação automática")
    parser.add_argument("--output", default=str(ROOT / "web" / "public" / "data"))
    args = parser.parse_args(argv)
    files = export_public_data(args.output)
    print(json.dumps({"exported": list(files), "approved_results": 0}, ensure_ascii=False))

if __name__ == "__main__":
    main()
