"""Catálogo de edições e validação de evidências, sem homologação automática."""
from dataclasses import dataclass
from urllib.parse import urlparse
from .scoring import Result, WEIGHTS, validate_result

@dataclass(frozen=True)
class Edition:
    edition_id: str
    competition: str
    year: int
    organizer: str
    jurisdiction: str = ""
    single_champion: bool = True

@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    url: str
    sha256: str
    source_type: str

def validate_catalog(editions, evidence):
    editions_by_id = {}
    evidence_by_id = {}
    for e in editions:
        if not isinstance(e.edition_id, str) or not e.edition_id.strip() or e.edition_id != e.edition_id.strip():
            raise ValueError("ID de edição inválido")
        if e.competition not in WEIGHTS:
            raise ValueError("Competição desconhecida")
        if type(e.year) is not int or not 1971 <= e.year <= 2025:
            raise ValueError("Edição fora do recorte")
        if not isinstance(e.organizer, str) or not e.organizer.strip():
            raise ValueError("Organizador obrigatório")
        if e.competition == "estadual" and (not isinstance(e.jurisdiction, str) or not e.jurisdiction.strip()):
            raise ValueError("Estadual exige federação ou jurisdição")
        if e.single_champion is not True:
            raise ValueError("Edições com campeões compartilhados exigem regra específica")
        if e.edition_id in editions_by_id:
            raise ValueError("Edição duplicada")
        editions_by_id[e.edition_id] = e
    for e in evidence:
        if not isinstance(e.evidence_id, str) or not e.evidence_id.strip() or e.evidence_id in evidence_by_id:
            raise ValueError("Evidência duplicada ou sem ID")
        if not isinstance(e.url, str):
            raise ValueError("URL de evidência inválida")
        p = urlparse(e.url)
        if p.scheme != "https" or not p.hostname:
            raise ValueError("Fonte exige HTTPS")
        if not isinstance(e.sha256, str) or len(e.sha256) != 64 or any(c not in "0123456789abcdef" for c in e.sha256):
            raise ValueError("Hash SHA-256 inválido")
        if e.source_type not in {"official", "historical_archive", "secondary", "exploratory"}:
            raise ValueError("Tipo de fonte desconhecido")
        evidence_by_id[e.evidence_id] = e
    return editions_by_id, evidence_by_id

def validate_dataset(results, editions, evidence, *, require_approved=True):
    """Valida integridade referencial e conflitos antes de calcular pontuações."""
    from .audit import detect_conflicts
    editions_by_id, evidence_by_id = validate_catalog(editions, evidence)
    records = tuple(results)
    for r in records:
        validate_result(r)
        if require_approved and not r.approved:
            raise ValueError("Registro não homologado")
        if not r.edition_id or r.edition_id not in editions_by_id:
            raise ValueError("Edição não cadastrada")
        edition = editions_by_id[r.edition_id]
        if (r.competition, r.year) != (edition.competition, edition.year):
            raise ValueError("Resultado diverge da edição")
        if r.evidence_id not in evidence_by_id:
            raise ValueError("Evidência não cadastrada")
    conflicts = detect_conflicts(records)
    if conflicts:
        raise ValueError(f"Conflitos históricos: {len(conflicts)}")
    champions = {}
    for r in records:
        if not r.approved or r.outcome != "champion":
            continue
        edition = editions_by_id[r.edition_id]
        if edition.single_champion:
            champions.setdefault(r.edition_id, set()).add(r.club.strip())
    if any(len(clubs) > 1 for clubs in champions.values()):
        raise ValueError("Múltiplos campeões na mesma edição")
    return records

def score_verified(results, editions, evidence, *, weights=None):
    """Entrada pública recomendada: valida catálogo e evidências antes de pontuar."""
    from .audit import weighted_totals
    records = validate_dataset(results, editions, evidence, require_approved=True)
    return weighted_totals(records, weights)
