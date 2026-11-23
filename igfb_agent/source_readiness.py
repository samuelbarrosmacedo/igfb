"""Relatório de prontidão documental; pistas não equivalem a provas arquivadas."""
from collections import Counter, defaultdict
from .candidates import build_candidates
from .calendar import brasileirao_editions

def source_readiness(candidates=None):
    records = tuple(build_candidates() if candidates is None else candidates)
    years = {e.year for e in brasileirao_editions()}
    by_year = defaultdict(set)
    by_club = Counter()
    checked_source_ids = set()
    unarchived_source_ids = set()
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("Candidato inválido")
        if item.get("approved") is not False or item.get("status") != "candidate_requires_review":
            raise ValueError("Somente candidatos pendentes são permitidos")
        year = item.get("year")
        if type(year) is not int or year not in years:
            raise ValueError("Ano fora do recorte")
        if item.get("edition_id") != f"brasileirao:{year}" or item.get("competition") != "brasileirao":
            raise ValueError("Edição inconsistente")
        if not isinstance(item.get("source_id"), str) or not item["source_id"].strip():
            raise ValueError("Fonte inválida")
        if not isinstance(item.get("club_id"), str) or not item["club_id"].strip():
            raise ValueError("Clube inválido")
        if item.get("source_page_checked") is True:
            checked_source_ids.add(item["source_id"])
        if item.get("source_archived") is not True:
            unarchived_source_ids.add(item["source_id"])
        by_year[year].add(item["source_id"])
        by_club[item["club_id"]] += 1
    return {
        "total_candidates": len(records),
        "distinct_years_with_leads": len(by_year),
        "total_seasons": len(years),
        "years_without_leads": sorted(years-set(by_year)),
        "sources_per_year": {str(y):len(ids) for y,ids in sorted(by_year.items())},
        "candidate_counts_by_club": dict(sorted(by_club.items())),
        "checked_source_pages": len(checked_source_ids),
        "source_ids_without_archived_bytes": len(unarchived_source_ids),
        "approved_results": 0,
        "warning": "Contagem de pistas não mede cobertura histórica homologada.",
    }

def main():
    import json
    print(json.dumps(source_readiness(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
