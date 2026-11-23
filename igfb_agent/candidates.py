"""Converte pistas documentais em candidatos NÃO homologados, sem inferir fatos novos."""
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LEADS = ROOT / "config" / "historical_source_leads.json"
EXCLUDED = {1937}
FIRST, LAST = 1971, 2025

def validate_leads(payload):
    if payload.get("schema_version") != 1 or payload.get("status") != "source_leads_not_homologated":
        raise ValueError("Versão ou status de pistas inválido")
    seen = set()
    candidates = []
    for source in payload.get("sources", []):
        sid = source.get("source_id")
        url = source.get("url", "")
        if not isinstance(url, str):
            raise ValueError('URL inválida')
        parsed = urlparse(url)
        if not isinstance(sid, str) or not sid.strip() or sid in seen:
            raise ValueError("Identificador de fonte inválido ou duplicado")
        if parsed.scheme != "https" or parsed.hostname not in {"cbf.com.br", "www.cbf.com.br"} or parsed.username or parsed.password:
            raise ValueError("Fonte deve usar HTTPS")
        if source.get("publisher") != "CBF" or source.get("source_type") != "official":
            raise ValueError("Tipo de fonte inesperado")
        club = source.get("claim_club")
        if not isinstance(club, str) or not club.strip():
            raise ValueError("Clube canônico ausente")
        years = source.get("claim_years")
        if not isinstance(years, list) or not years:
            raise ValueError("Anos de referência ausentes")
        if len(years) != len(set(years)):
            raise ValueError('Ano duplicado')
        seen.add(sid)
        for year in years:
            if type(year) is not int or year in EXCLUDED or not FIRST <= year <= LAST:
                raise ValueError("Ano fora do recorte")
            candidates.append({
                "club_id": club,
                "competition": "brasileirao",
                "year": year,
                "edition_id": f"brasileirao:{year}",
                "outcome_claim": "champion",
                "source_id": sid,
                "source_url": url,
                "status": "candidate_requires_review",
                "approved": False,
            })
    return candidates

def build_candidates(path=LEADS):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_leads(payload)

def main():
    print(json.dumps({"schema_version": 1, "candidates": build_candidates(),
                      "note": "Pistas documentais; nenhum resultado homologado."},
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
