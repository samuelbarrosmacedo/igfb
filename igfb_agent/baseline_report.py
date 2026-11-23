"""Relatório reproduzível do calendário e estado atual, sem classificação de clubes."""
import json
from dataclasses import asdict
from pathlib import Path
from .calendar import brasileirao_editions
from .coverage import measure_coverage

def build_baseline_report():
    editions = brasileirao_editions()
    coverage = measure_coverage([], editions, [])
    return {
        "project": "IGFB",
        "scope": {"competition": "brasileirao", "start": 1971, "end": 2025},
        "catalog_status": "calendar_only_unverified_metadata",
        "approved_results": 0,
        "coverage": asdict(coverage),
        "note": "Calendário não é comprovação de resultados, participações ou títulos.",
    }

def main():
    print(json.dumps(build_baseline_report(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
