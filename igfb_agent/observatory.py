"""Catálogo editorial extensível. Nunca promove conteúdo esportivo a homologação."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
from .scoring import BASELINE_YEAR, THROUGH_YEAR, WEIGHTS

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"taca_brasil", "robertao", "1937"}
SPORT_STATES = {"collected", "in_review", "disputed", "provisional", "official_final"}
EDITION_STATES = {"research", "scheduled", "ongoing", "finished", "cancelled"}


def unique(rows, label):
    result = {}
    for row in rows:
        key = row.get("id")
        if not isinstance(key, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_:-]*", key) or key in result:
            raise ValueError(f"ID inválido ou duplicado: {label}")
        result[key] = row
    return result


def validate_catalog(catalog, *, root=ROOT):
    if catalog.get("schema_version") != 1:
        raise ValueError("Versão do catálogo não suportada; exige migração explícita")
    clubs = unique(catalog["clubs"], "clube")
    competitions = unique(catalog["competitions"], "competição")
    editions = unique(catalog["editions"], "edição")
    sources = unique(catalog["sources"], "fonte")
    records = unique(catalog["records"], "registro")
    for source in sources.values():
        if urlparse(source["url"]).scheme != "https" or not urlparse(source["url"]).hostname:
            raise ValueError("Fonte exige HTTPS")
    for item in [*clubs.values(), *competitions.values()]:
        if not item.get("name", "").strip():
            raise ValueError("Identidade exige nome")
        if any(s not in sources for s in item["identity_source_ids"]):
            raise ValueError("Fonte da identidade ausente")
        asset = item.get("crest")
        if asset:
            path = asset["path"]
            if not re.fullmatch(r"assets/identities/[a-z0-9_-]+\.(svg|png|webp)", path):
                raise ValueError("Caminho de escudo inválido")
            target = Path(root) / "web/public" / path
            if not target.is_file() or sha256(target.read_bytes()).hexdigest() != asset["sha256"]:
                raise ValueError("Escudo ausente ou hash divergente")
            if not all(asset.get(k) for k in ("source_url", "license", "attribution", "usage_note")):
                raise ValueError("Escudo sem procedência ou condições de uso")
            if not asset["source_url"].startswith("https://"):
                raise ValueError("Fonte de escudo inválida")
            if path.endswith(".svg"):
                import xml.etree.ElementTree as ET
                svg = ET.fromstring(target.read_bytes())
                for element in svg.iter():
                    tag = element.tag.rsplit("}", 1)[-1]
                    if tag == "style" and re.search(r"url\s*\(|@import|expression", element.text or "", re.I):
                        raise ValueError("CSS externo em escudo")
                    if tag in {"script", "foreignObject", "image", "use"} or any(k.lower().startswith("on") or "href" in k.lower() for k in element.attrib):
                        raise ValueError("SVG ativo ou com referência externa")
    for competition in competitions.values():
        if competition["id"] in EXCLUDED or competition["scoring_category"] not in {*WEIGHTS, None}:
            raise ValueError("Competição inelegível ou categoria desconhecida")
        if competition["jurisdiction"] == "state" and (not competition["state"] or not competition["organizer"]):
            raise ValueError("Estadual exige estado e federação")
    for edition in editions.values():
        if edition["id"].startswith("brasileirao:") and (edition["competition_id"] != "brasileirao" or edition["id"] != f'brasileirao:{edition["year"]}'):
            raise ValueError("Identidade histórica de edição divergente")
        if edition["competition_id"] not in competitions:
            raise ValueError("Competição não cadastrada")
        if type(edition["year"]) is not int or not BASELINE_YEAR <= edition["year"] <= 9999:
            raise ValueError("Temporada fora do domínio")
        if edition["status"] not in EDITION_STATES:
            raise ValueError("Estado de edição inválido")
        if edition["status"] != "research" and not edition["source_ids"]:
            raise ValueError("Estado esportivo exige fonte")
        if any(c not in clubs for c in edition["participant_ids"]) or len(set(edition["participant_ids"])) != len(edition["participant_ids"]):
            raise ValueError("Participante inválido")
        if any(s not in sources for s in edition["source_ids"]):
            raise ValueError("Fonte de edição ausente")
    for record in records.values():
        if record["edition_id"] not in editions or record["status"] not in SPORT_STATES:
            raise ValueError("Registro sem edição ou homologação indevida")
        if not record["source_ids"] or any(s not in sources for s in record["source_ids"]):
            raise ValueError("Registro exige fontes cadastradas")
        if not record["club_ids"] or any(c not in clubs for c in record["club_ids"]):
            raise ValueError("Registro exige clubes cadastrados")
        if record["kind"] not in {"result", "match", "standing", "statistic"}:
            raise ValueError("Tipo de registro desconhecido")
        if record["status"] == "official_final" and editions[record["edition_id"]]["status"] != "finished":
            raise ValueError("Resultado final exige edição encerrada")
        if type(record["revision"]) is not int or record["revision"] < 1 or not record["revision_note"].strip():
            raise ValueError("Revisão exige número e justificativa")
        timestamp = datetime.fromisoformat(record["updated_at"].replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            raise ValueError("Atualização exige fuso")
    return catalog


def include_historical_results(catalog, *, root=ROOT):
    """Translate the researched 1971–2025 cross-check into *provisional* display records.

    Do not assign IGFB scores, approvals or official_final status. This is
    derived from a versioned research document, not silently promoted evidence.
    """
    path = Path(root) / "docs/evidence/brasileirao-reconciliation-2025.json"
    evidence = json.loads(path.read_text(encoding="utf-8"))
    years = evidence.get("years", [])
    if evidence.get("status") != "secondary_crosscheck_not_homologated" or len(years) != 55:
        raise ValueError("Reconciliação histórica incompleta ou homologação inesperada")
    if {row["year"] for row in years} != set(range(BASELINE_YEAR, THROUGH_YEAR + 1)):
        raise ValueError("Calendário do cruzamento histórico inválido")
    if [(row["year"], row["club"]) for row in years if row["conflict"]] != [(1987, "sport")]:
        raise ValueError("Controvérsia histórica alterada: exige revisão")
    club_ids = {c["id"] for c in catalog["clubs"]}
    source_ids = {s["id"] for s in catalog["sources"]}
    if not {"espn-brasileirao-lista-2025", "flamengo-titulos-1987"} <= source_ids:
        raise ValueError("Fontes do cruzamento ausentes do catálogo")
    leads = json.loads((Path(root) / "config/historical_source_leads.json").read_text(encoding="utf-8"))["sources"]
    by_source = {s["source_id"]: s for s in leads}
    for row in years:
        for claim in row["claims"]:
            lead = by_source.get(claim["source"])
            if lead is None or row["year"] not in lead["claim_years"] or claim["club"] != lead["claim_club"]:
                raise ValueError("Pista histórica divergente do cruzamento versionado")
            if lead["source_id"] not in source_ids:
                catalog["sources"].append({
                    "id": lead["source_id"], "url": lead["url"],
                    "publisher": lead["publisher"],
                    "note": "Pista candidata, sem homologação. " + lead["note"],
                    "checked_on": None,
                })
                source_ids.add(lead["source_id"])
    existing_editions = {e["id"] for e in catalog["editions"]}
    existing_records = {r["id"] for r in catalog["records"]}
    for row in sorted(years, key=lambda r: r["year"]):
        year = row["year"]
        disputed = year == 1987
        clubs = ["sport", "flamengo"] if disputed else [row["club"]]
        if not set(clubs) <= club_ids:
            raise ValueError(f"Clube histórico ausente do catálogo: {year}")
        sources = ["espn-brasileirao-lista-2025", "flamengo-titulos-1987"] if disputed else ["espn-brasileirao-lista-2025"]
        sources = sorted(set(sources) | {claim["source"] for claim in row["claims"]})
        edition_id = f"brasileirao:{year}"
        if edition_id not in existing_editions:
            catalog["editions"].append({
                "id": edition_id, "competition_id": "brasileirao", "year": year,
                "label": str(year), "status": "finished", "format": "unknown",
                "participant_ids": [], "source_ids": sources,
                "updated_at": "2026-11-25T23:00:00Z",
            })
        record_id = f"{edition_id}:champion-crosscheck"
        if record_id not in existing_records:
            catalog["records"].append({
                "id": record_id, "edition_id": edition_id, "kind": "result",
                "status": "disputed" if disputed else "provisional",
                "club_ids": clubs, "source_ids": sources,
                "label": ("Flamengo* e Sport* — aguardando revisão" if disputed
                          else "Campeão indicado no cruzamento histórico"),
                "phase": "Copa União (Módulo Verde) / atribuição oficial ao Sport" if disputed else None,
                "position": 1 if not disputed else None,
                "value": None, "unit": None,
                "home_score": None, "away_score": None, "played_at": None,
                "updated_at": "2026-11-25T23:00:00Z", "revision": 1,
                "revision_note": "Cruzamento secundário, ainda não homologado; sem pontuação no IGFB.",
            })
    return catalog


def build_observatory(*, catalog_path=None, current_year=None, root=ROOT):
    catalog = json.loads((Path(catalog_path) if catalog_path else ROOT / "config/observatory.json").read_text())
    validate_catalog(catalog, root=root)
    include_historical_results(catalog, root=root)
    validate_catalog(catalog, root=root)
    year = current_year if current_year is not None else datetime.now(ZoneInfo("America/Sao_Paulo")).year
    if type(year) is not int or not BASELINE_YEAR <= year <= 9999:
        raise ValueError("Temporada atual inválida")
    return {**deepcopy(catalog), "current_season": year,
            "historical_scope": {"first_year": BASELINE_YEAR, "last_year": THROUGH_YEAR},
            "seasons": sorted({year, *(e["year"] for e in catalog["editions"])}, reverse=True),
            "collection_mode": "repository_records_only"}
