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


def build_observatory(*, catalog_path=None, current_year=None, root=ROOT):
    catalog = json.loads((Path(catalog_path) if catalog_path else ROOT / "config/observatory.json").read_text())
    validate_catalog(catalog, root=root)
    year = current_year if current_year is not None else datetime.now(ZoneInfo("America/Sao_Paulo")).year
    if type(year) is not int or not BASELINE_YEAR <= year <= 9999:
        raise ValueError("Temporada atual inválida")
    return {**deepcopy(catalog), "current_season": year,
            "historical_scope": {"first_year": BASELINE_YEAR, "last_year": THROUGH_YEAR},
            "seasons": sorted({year, *(e["year"] for e in catalog["editions"])}, reverse=True),
            "collection_mode": "repository_records_only"}
