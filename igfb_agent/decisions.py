"""Trilha de homologação explícita, verificável e revogável.

Não homologa resultados por conta própria: exige decisão humana e evidência
arquivada com SHA-256, além de identificadores consistentes.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from .registry import validate_dataset, validate_catalog
from .scoring import Result, validate_result

@dataclass(frozen=True)
class Decision:
    decision_id: str
    edition_id: str
    club: str
    outcome: str
    evidence_id: str
    reviewer: str
    decided_at: str
    rationale: str
    status: str = "approved"
    supersedes: str = ""

def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Data de decisão inválida")
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Data de decisão inválida") from exc
    if date.tzinfo is None or date.utcoffset() is None:
        raise ValueError("Data exige fuso horário")
    return date.astimezone(timezone.utc)

def validate_decisions(decisions, editions, evidence):
    catalog, documents = validate_catalog(editions, evidence)
    seen = {}
    for d in decisions:
        if not isinstance(d, Decision):
            raise ValueError("Decisão inválida")
        if not isinstance(d.decision_id, str) or not d.decision_id.strip() or d.decision_id in seen:
            raise ValueError("ID de decisão duplicado ou inválido")
        if d.status not in {"approved", "revoked"}:
            raise ValueError("Estado de decisão inválido")
        for value in (d.club, d.evidence_id, d.reviewer, d.rationale):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Decisão exige clube, evidência, revisor e justificativa")
        if d.edition_id not in catalog or d.evidence_id not in documents:
            raise ValueError("Referência de decisão inexistente")
        edition = catalog[d.edition_id]
        validate_result(Result(d.club, edition.year, edition.competition, d.outcome, d.evidence_id, True, d.edition_id))
        timestamp = _timestamp(d.decided_at)
        if d.status == "approved" and d.supersedes:
            raise ValueError("Aprovação não pode revogar outra decisão")
        if d.status == "revoked":
            if not d.supersedes or d.supersedes not in seen:
                raise ValueError("Revogação exige decisão anterior")
            previous = seen[d.supersedes]
            if previous.status != "approved" or previous.edition_id != d.edition_id or previous.club != d.club or previous.outcome != d.outcome or previous.evidence_id != d.evidence_id:
                raise ValueError("Revogação não corresponde à aprovação original")
            if timestamp <= _timestamp(previous.decided_at):
                raise ValueError("Revogação deve ser posterior à aprovação")
            if any(x.status == "revoked" and x.supersedes == d.supersedes for x in seen.values()):
                raise ValueError("Aprovação já revogada")
        seen[d.decision_id] = d
    return seen

def materialize_approved(decisions, editions, evidence, *, archive_root=None):
    """Produz resultados aprovados apenas a partir de decisões válidas e ativas."""
    editions = tuple(editions)
    evidence = tuple(evidence)
    decisions = tuple(decisions)
    validate_decisions(decisions, editions, evidence)
    revoked = {d.supersedes for d in decisions if d.status == "revoked"}
    catalog, documents = validate_catalog(editions, evidence)
    # A existência de um hash cadastrado não comprova os bytes do documento.
    active_evidence_ids = {d.evidence_id for d in decisions
                           if d.status == "approved" and d.decision_id not in revoked}
    if active_evidence_ids:
        if archive_root is None:
            raise ValueError("Arquivo de evidências obrigatório para homologação")
        from .archive import verify_archive
        verify_archive((documents[eid] for eid in sorted(active_evidence_ids)),
                       archive_root, strict=True)
    results = []
    for d in decisions:
        if d.status != "approved" or d.decision_id in revoked:
            continue
        edition = catalog[d.edition_id]
        results.append(Result(d.club, edition.year, edition.competition, d.outcome, d.evidence_id, True, d.edition_id))
    return validate_dataset(results, editions, evidence)
