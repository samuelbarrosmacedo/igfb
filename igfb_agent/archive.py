"""Conferência offline dos bytes arquivados de evidências históricas."""
from hashlib import sha256
from pathlib import Path
from .registry import validate_catalog

def verify_archive(evidence, archive_root, *, strict=True):
    """Compara bytes reais de arquivos locais ao SHA-256 do catálogo.

    Cada arquivo é nomeado <evidence_id>.bin; rejeita IDs com caminhos.
    Não faz download, não infere resultados e não homologa documentos.
    """
    evidence = tuple(evidence)
    validate_catalog([], evidence)
    root = Path(archive_root).resolve()
    report = {}
    for item in evidence:
        eid = item.evidence_id
        if eid in {".", ".."} or "/" in eid or "\\" in eid:
            raise ValueError("ID de evidência não pode conter caminhos")
        path = (root / f"{eid}.bin").resolve()
        if not path.is_relative_to(root):
            raise ValueError("Caminho fora do arquivo")
        if not path.is_file():
            report[eid] = "missing"
            continue
        digest = sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        report[eid] = "verified" if digest.hexdigest() == item.sha256 else "mismatch"
    if strict and any(status != "verified" for status in report.values()):
        raise ValueError("Evidências ausentes ou com hash divergente")
    return report
