"""Revisão de afirmações históricas: triagem determinística, nunca homologação automática."""
from collections import defaultdict
from .candidates import build_candidates
from .calendar import brasileirao_editions

def review_queue(candidates=None):
    """Agrupa afirmações por edição e identifica disputas entre clubes.
    
    Um grupo com várias fontes para o mesmo clube não equivale a validação
    independente; as fontes precisam ser examinadas e arquivadas.
    """
    records = tuple(build_candidates() if candidates is None else candidates)
    valid_years = {e.year for e in brasileirao_editions()}
    grouped = defaultdict(lambda: defaultdict(set))
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("Candidato inválido")
        year = row.get("year")
        club = row.get("club_id")
        sid = row.get("source_id")
        if type(year) is not int or year not in valid_years:
            raise ValueError("Ano fora do recorte")
        if row.get("edition_id") != f"brasileirao:{year}" or row.get("competition") != "brasileirao":
            raise ValueError("Identidade de edição inválida")
        if row.get("approved") is not False or row.get("status") != "candidate_requires_review":
            raise ValueError("Revisão exige candidato pendente")
        if any(not isinstance(v, str) or not v.strip() for v in (club, sid)):
            raise ValueError("Clube e fonte obrigatórios")
        if row.get("outcome_claim") != "champion":
            raise ValueError("Tipo de afirmação não suportado")
        grouped[year][club].add(sid)
    return tuple({
        "year": year,
        "edition_id": f"brasileirao:{year}",
        "claims": tuple({
            "club_id": club,
            "source_ids": tuple(sorted(ids)),
            "source_count": len(ids),
        } for club, ids in sorted(clubs.items())),
        "has_competing_claims": len(clubs) > 1,
        "status": "manual_review_required",
        "approved": False,
    } for year, clubs in sorted(grouped.items()))
