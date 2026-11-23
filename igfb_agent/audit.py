"""Auditoria de conflitos e sensibilidade de pesos, sem dados históricos presumidos."""
from collections import defaultdict
from dataclasses import dataclass
from math import fsum, isfinite
from .scoring import WEIGHTS, validate_result

EXCLUSIVE = {"champion", "runner_up", "third", "fourth", "semifinal"}
COMPETITION_GROUPS = {
    "brasileirao": "brasileirao",
    "libertadores": "libertadores",
    "copa_do_brasil": "copa_do_brasil",
    "sul_americana": "sul_americana",
    "conmebol_mercosul": "conmebol_mercosul",
    "recopa": "recopa",
    "supercopa": "supercopa",
}

@dataclass(frozen=True)
class Conflict:
    kind: str
    competition: str
    year: int
    clubs: tuple[str, ...]
    outcomes: tuple[str, ...]

def detect_conflicts(results):
    """Detecta incompatibilidades; não decide controvérsias históricas."""
    records = tuple(results)
    for r in records:
        validate_result(r)
    by_club = defaultdict(set)
    by_champion = defaultdict(set)
    for r in records:
        if not r.approved:
            continue
        edition = r.edition_id or f"{r.competition}:{r.year}"
        key = (r.club.strip(), r.year, r.competition, edition)
        if r.outcome in EXCLUSIVE:
            by_club[key].add(r.outcome)
        if r.outcome == "champion" and r.competition in COMPETITION_GROUPS:
            by_champion[(r.year, r.competition, edition)].add(r.club.strip())
    conflicts = []
    for (club, year, competition, edition), outcomes in sorted(by_club.items()):
        if len(outcomes) > 1:
            conflicts.append(Conflict("incompatible_outcomes", competition, year, (club,), tuple(sorted(outcomes))))
    for (year, competition, edition), clubs in sorted(by_champion.items()):
        if len(clubs) > 1:
            conflicts.append(Conflict("multiple_champions", competition, year, tuple(sorted(clubs)), ("champion",)))
    return conflicts

def weighted_totals(results, weights=None):
    """Recusa entradas conflitantes; pesos podem variar em cenários auditáveis."""
    records = tuple(results)
    conflicts = detect_conflicts(records)
    if conflicts:
        raise ValueError(f"{len(conflicts)} conflito(s) histórico(s) não resolvido(s)")
    weights = WEIGHTS if weights is None else weights
    totals = defaultdict(list)
    seen = set()
    for r in records:
        if not r.approved:
            raise ValueError("Evidência não aprovada")
        key = (r.club.strip(), r.competition, r.year, r.edition_id or f"{r.competition}:{r.year}", r.outcome)
        if key in seen:
            continue
        seen.add(key)
        try:
            weight = float(weights[r.competition][r.outcome])
        except (KeyError, TypeError) as exc:
            raise ValueError("Peso ausente") from exc
        if not isfinite(weight):
            raise ValueError("Peso não finito")
        totals[r.club.strip()].append(weight)
    return {club: fsum(values) for club, values in sorted(totals.items())}

def sensitivity_envelope(results, scenarios):
    """Intervalo de pontuações por cenário; não é intervalo de confiança."""
    cases = tuple(scenarios)
    if not cases:
        raise ValueError("Ao menos um cenário é necessário")
    records = tuple(results)
    scores = [weighted_totals(records, weights) for weights in cases]
    clubs = set().union(*(set(case) for case in scores))
    return {club: {"min": min(case.get(club, 0) for case in scores),
                   "max": max(case.get(club, 0) for case in scores)}
            for club in sorted(clubs)}
