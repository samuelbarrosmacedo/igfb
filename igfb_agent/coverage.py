"""Auditoria de cobertura e lacunas sem estimativas subjetivas de progresso."""
from collections import Counter
from dataclasses import dataclass
from .registry import validate_catalog
from .scoring import validate_result

@dataclass(frozen=True)
class Coverage:
    registered_editions: int
    editions_with_results: int
    editions_without_results: int
    approved_results: int
    pending_results: int
    distinct_clubs: int
    editions_with_approved_results: int
    missing_edition_ids: tuple[str, ...]
    approved_coverage_ratio: float | None

def measure_coverage(results, editions, evidence):
    """Denominador: edições cadastradas, não o universo histórico total."""
    catalog, documents = validate_catalog(editions, evidence)
    records = tuple(results)
    with_results = set()
    with_approved = set()
    clubs = set()
    approved = pending = 0
    for record in records:
        validate_result(record)
        if not record.edition_id or record.edition_id not in catalog:
            raise ValueError("Edição ausente do catálogo")
        edition = catalog[record.edition_id]
        if (record.competition, record.year) != (edition.competition, edition.year):
            raise ValueError("Inconsistência entre resultado e edição")
        if record.evidence_id not in documents:
            raise ValueError("Evidência não cadastrada")
        with_results.add(record.edition_id)
        clubs.add(record.club.strip())
        if record.approved:
            approved += 1
            with_approved.add(record.edition_id)
        else:
            pending += 1
    missing = tuple(sorted(set(catalog) - with_results))
    denominator = len(catalog)
    return Coverage(
        registered_editions=denominator,
        editions_with_results=len(with_results),
        editions_without_results=len(missing),
        approved_results=approved,
        pending_results=pending,
        distinct_clubs=len(clubs),
        editions_with_approved_results=len(with_approved),
        missing_edition_ids=missing,
        approved_coverage_ratio=len(with_approved)/denominator if denominator else None,
    )
