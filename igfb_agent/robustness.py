"""Estabilidade de posições e sensibilidade determinística com cenários explícitos."""
from collections import defaultdict
from math import fsum, isfinite
from .audit import weighted_totals

def rank_scores(scores):
    """Ranking por competição, com empate exato e valores numéricos finitos."""
    normalized = {}
    for club, value in scores.items():
        if not isinstance(club, str) or not club.strip():
            raise ValueError("Identificador de clube inválido")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Pontuação deve ser numérica")
        try:
            numeric = float(value)
        except (ValueError, OverflowError) as exc:
            raise ValueError("Pontuação inválida") from exc
        if not isfinite(numeric):
            raise ValueError("Pontuação inválida")
        normalized[club] = numeric
    ordered = sorted(normalized.items(), key=lambda x: (-x[1], x[0]))
    ranks = {}
    for i, (club, score) in enumerate(ordered, 1):
        ranks[club] = i if i == 1 or score != ordered[i-2][1] else ranks[ordered[i-2][0]]
    return ranks

def scenario_stability(results, scenarios, *, clubs=None):
    """Estatísticas por cenários, não probabilidades nem intervalos de confiança."""
    cases = tuple(scenarios)
    if not cases:
        raise ValueError("Ao menos um cenário é obrigatório")
    records = tuple(results)
    outputs = [weighted_totals(records, weights) for weights in cases]
    universe = set(clubs or ())
    for scores in outputs:
        universe.update(scores)
    universe = sorted(universe)
    if not universe:
        return {}
    samples = defaultdict(list)
    positions = defaultdict(list)
    for scores in outputs:
        complete = {club: scores.get(club, 0.0) for club in universe}
        ranking = rank_scores(complete)
        for club in universe:
            samples[club].append(complete[club])
            positions[club].append(ranking[club])
    return {
        club: {
            "score_min": min(samples[club]),
            "score_max": max(samples[club]),
            "score_mean": fsum(samples[club])/len(cases),
            "rank_best": min(positions[club]),
            "rank_worst": max(positions[club]),
            "rank_mean": fsum(positions[club])/len(cases),
            "first_place_fraction": sum(r == 1 for r in positions[club])/len(cases),
            "scenarios": len(cases),
        }
        for club in universe
    }
