"""Calendário canônico de edições da Série A, sem inferir participantes ou campeões."""
from .registry import Edition

START_YEAR = 1971
END_YEAR = 2025

def brasileirao_editions(start=START_YEAR, end=END_YEAR):
    if type(start) is not int or type(end) is not int or not START_YEAR <= start <= end <= END_YEAR:
        raise ValueError("Recorte permitido: 1971–2025")
    return tuple(
        Edition(
            edition_id=f"brasileirao:{year}",
            competition="brasileirao",
            year=year,
            organizer="CBF (ou entidade organizadora predecessora; verificar por edição)",
        )
        for year in range(start, end + 1)
    )

def participation_editions(start=START_YEAR, end=END_YEAR):
    """Identidade separada para presença na elite; requer confirmação por clube."""
    if type(start) is not int or type(end) is not int or not START_YEAR <= start <= end <= END_YEAR:
        raise ValueError("Recorte permitido: 1971–2025")
    return tuple(
        Edition(
            edition_id=f"serie_a_participation:{year}",
            competition="serie_a_participation",
            year=year,
            organizer="Organizador da Série A; verificar por edição",
        )
        for year in range(start, end + 1)
    )
