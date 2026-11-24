"""Plano de pesquisa por lacunas; tarefas não representam resultados esportivos."""
import json
from .calendar import brasileirao_editions
from .evidence_reconciliation import reconcile_evidence

def research_backlog(candidates=None):
    records = tuple(reconcile_evidence()["candidates"] if candidates is None else candidates)
    years = {edition.year for edition in brasileirao_editions()}
    by_year = {year: [] for year in years}
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("Candidato inválido")
        year = item.get("year")
        if type(year) is not int or year not in years:
            raise ValueError("Ano fora do recorte")
        if item.get("edition_id") != f"brasileirao:{year}" or item.get("competition") != "brasileirao":
            raise ValueError("Identidade da edição inválida")
        if item.get("approved") is not False or item.get("status") != "candidate_requires_review":
            raise ValueError("Pistas não homologadas obrigatórias")
        if not isinstance(item.get("source_id"), str) or not item["source_id"].strip():
            raise ValueError("Fonte inválida")
        by_year[year].append(item)
    tasks = []
    for year in sorted(years):
        items = by_year[year]
        sources = sorted({row["source_id"] for row in items})
        checked = sorted({row["source_id"] for row in items if row.get("source_page_checked") is True})
        archived = sorted({row["source_id"] for row in items if row.get("source_archived") is True})
        if not items:
            stage, priority = "discover_official_source", 1
        elif len(archived) < len(sources):
            stage, priority = "archive_and_verify_source", 2
        else:
            stage, priority = "manual_historical_review", 3
        tasks.append({
            "year": year, "edition_id": f"brasileirao:{year}",
            "priority": priority, "stage": stage,
            "candidate_count": len(items), "source_ids": sources,
            "checked_source_count": len(checked), "archived_source_count": len(archived),
            "approved": False,
        })
    tasks.sort(key=lambda item: (item["priority"], item["year"]))
    return {
        "schema_version": 1,
        "scope": {"first_year": 1971, "last_year": 2025},
        "total_seasons": len(years),
        "seasons_without_leads": sum(not by_year[y] for y in years),
        "seasons_with_leads": sum(bool(by_year[y]) for y in years),
        "lead_coverage_percent": round(100 * sum(bool(by_year[y]) for y in years) / len(years), 2),
        "ranking_approved": False,
        "tasks": tasks,
        "warning": "Fila de pesquisa, não evidência de campeões ou progresso global.",
    }

def main():
    print(json.dumps(research_backlog(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
