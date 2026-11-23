"""Auditoria determinística do estado do IGFB; não estima percentual concluído."""
import json
from pathlib import Path
from .calendar import brasileirao_editions
from .candidates import build_candidates
from .source_readiness import source_readiness
from .review_queue import review_queue

ROOT = Path(__file__).resolve().parents[1]

def audit_project(*, status_path=None, candidates=None):
    path = Path(status_path) if status_path is not None else ROOT / "state" / "status.json"
    status = json.loads(path.read_text(encoding="utf-8"))
    records = tuple(build_candidates() if candidates is None else candidates)
    readiness = source_readiness(records)
    queue = review_queue(records)
    years = {e.year for e in brasileirao_editions()}
    if years != set(range(1971, 2026)):
        raise ValueError("Calendário não cobre exatamente 1971–2025")
    if status.get("progress_audited") is not False:
        raise ValueError("Progresso não pode ser marcado auditado sem metodologia")
    estimate = status.get("progress_percent_estimate")
    if type(estimate) is not int or not 0 <= estimate <= 100:
        raise ValueError("Estimativa de progresso inválida")
    if status.get("approved_records") != 0:
        raise ValueError("Contagem de aprovados exige reconciliação com ledger")
    if any(r.get("approved") is not False for r in records):
        raise ValueError("Pistas não podem ser homologadas")
    return {
        "scope": {"first_year": 1971, "last_year": 2025, "seasons": len(years),
                  "excluded_pre_1971": True},
        "legacy_progress": {"percent": estimate, "audited": False,
                            "usable_as_completion_metric": False},
        "source_leads": readiness["total_candidates"],
        "measured_progress": {
            "metric": "seasons_with_documentary_leads",
            "numerator": readiness["distinct_years_with_leads"],
            "denominator": len(years),
            "percent": round(100 * readiness["distinct_years_with_leads"] / len(years), 2),
            "audited_completion": False,
            "warning": "Cobertura de pistas não é percentual de conclusão do IGFB.",
        },
        "seasons_with_leads": readiness["distinct_years_with_leads"],
        "seasons_without_leads": readiness["years_without_leads"],
        "review_queue_editions": len(queue),
        "competing_claim_editions": [x["year"] for x in queue if x["has_competing_claims"]],
        "approved_records": 0,
        "warning": "Pistas não são documentos arquivados nem resultados homologados.",
    }

def main():
    print(json.dumps(audit_project(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
