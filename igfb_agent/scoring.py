"""Pontuação e estatística determinísticas; não homologa evidências."""
from collections import defaultdict
from dataclasses import dataclass
from math import exp, fsum, isfinite

BASELINE_YEAR, THROUGH_YEAR = 1971, 2025
WEIGHTS = {
 "world_classic":{"champion":900},"world_fifa_annual":{"champion":950},
 "world_expanded":{"champion":1100},
 "libertadores":{"champion":700,"runner_up":250,"semifinal":90},
 "brasileirao":{"champion":450,"runner_up":160,"third":75,"fourth":45},
 "copa_do_brasil":{"champion":300,"runner_up":110,"semifinal":40},
 "sul_americana":{"champion":200,"runner_up":70},
 "conmebol_mercosul":{"champion":170,"runner_up":60},
 "recopa":{"champion":100,"runner_up":30},
 "supercopa":{"champion":75,"runner_up":20},
 "estadual":{"champion":25,"runner_up":8},
 "serie_a_participation":{"participated":8},
 "relegation_a_b":{"relegated":-400},
 "relegation_b_c":{"relegated":-600},
 "relegation_c_d":{"relegated":-800},
}

@dataclass(frozen=True)
class Result:
    club: str
    year: int
    competition: str
    outcome: str
    evidence_id: str
    approved: bool = False
    edition_id: str = ""

def validate_result(r):
    if not r.club.strip() or not r.evidence_id.strip():
        raise ValueError("Clube e evidência obrigatórios")
    if type(r.year) is not int or not BASELINE_YEAR <= r.year <= THROUGH_YEAR:
        raise ValueError("Ano fora do recorte")
    if r.competition not in WEIGHTS or r.outcome not in WEIGHTS[r.competition]:
        raise ValueError("Resultado desconhecido")
    if type(r.approved) is not bool:
        raise ValueError("Aprovação inválida")
    if not isinstance(r.edition_id, str) or (r.edition_id and not r.edition_id.strip()):
        raise ValueError("Identificador de edição inválido")

def score_results(results, *, require_approved=True):
    seen, totals = set(), defaultdict(list)
    for r in results:
        validate_result(r)
        if require_approved and not r.approved:
            raise ValueError("Evidência não aprovada")
        identity = (r.club.strip(), r.edition_id or f"{r.competition}:{r.year}", r.outcome)
        if identity in seen:
            continue
        seen.add(identity)
        totals[identity[0]].append(WEIGHTS[r.competition][r.outcome])
    return {club:fsum(values) for club,values in sorted(totals.items())}

def temporal_consistency(annual_nonnegative_scores):
    values = tuple(float(x) for x in annual_nonnegative_scores)
    if not values or any(not isfinite(x) or x < 0 for x in values):
        raise ValueError("Série inválida")
    denom = len(values)*fsum(x*x for x in values)
    return fsum(values)**2/denom if denom else 0.0

def standardize_season(scores):
    if not scores:
        raise ValueError("Temporada vazia")
    vals = tuple(float(x) for x in scores.values())
    if any(not isfinite(x) for x in vals):
        raise ValueError("Pontuação não finita")
    mean = fsum(vals)/len(vals)
    variance = fsum((x-mean)**2 for x in vals)/len(vals)
    if variance == 0:
        return {club:0.0 for club in scores}
    std = variance**0.5
    return {club:(float(value)-mean)/std for club,value in scores.items()}

def logistic_index(z):
    z = float(z)
    if not isfinite(z):
        raise ValueError("Entrada não finita")
    if z >= 0:
        return 100/(1+exp(-z))
    ez = exp(z)
    return 100*ez/(1+ez)
