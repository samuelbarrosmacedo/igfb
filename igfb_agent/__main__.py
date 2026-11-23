"""Coleta experimental rastreável do IGFB (sem aprovação automática de fatos)."""
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from .document_review import examine_document
from .source_queue import build_source_queue

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "config" / "seed_sources.json"
EVENTS = ROOT / "state" / "events.jsonl"
STATUS = ROOT / "state" / "status.json"
RETRY_DELAY = timedelta(hours=24)
MAX_BYTES = 2_000_000


def main():
    seed_sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    rules = json.loads((ROOT / "config" / "project_rules.json").read_text(encoding="utf-8"))
    sources = build_source_queue(seed_sources, rules)
    events = [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    latest = {event["url"]: event for event in events if "url" in event}
    now = datetime.now(timezone.utc)
    limit = max(0, min(int(os.getenv("IGFB_FETCH_LIMIT", "2")), 5))
    processed = 0
    collected = 0
    for source in sources:
        if processed >= limit:
            break
        url = source["url"]
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            print("Fonte ignorada: URL inválida")
            continue
        last = latest.get(url)
        if last and last.get("status") == "collected":
            continue
        if last and last.get("status") == "retry":
            try:
                attempted = datetime.fromisoformat(last["at"])
                if now - attempted < RETRY_DELAY:
                    continue
            except (ValueError, KeyError):
                pass
        processed += 1
        try:
            with httpx.Client(timeout=20, follow_redirects=True, headers={"User-Agent": "IGFBResearch/0.3 (historical research)"}) as client:
                response = client.get(url)
                response.raise_for_status()
                if len(response.content) > MAX_BYTES:
                    raise ValueError("Response exceeds size limit")
                content_type = response.headers.get("content-type", "")
                if "html" not in content_type:
                    raise ValueError("Unsupported content type")
            page_text = BeautifulSoup(response.text, "html.parser").get_text(" ", strip=True)
            if not page_text:
                raise ValueError("Empty document")
            event = {"url": url, "status": "collected",
                     "sha256": hashlib.sha256(page_text.encode()).hexdigest(),
                     "characters": len(page_text), "trust": source.get("trust", "unrated"),
                     "topic": source.get("topic", "unknown"),
                     "edition": source.get("edition"),
                     "at": now.isoformat(), "approved": False}
            review = examine_document(page_text, url, source.get("topic", "unknown"))
            if review is not None:
                event["document_review"] = review
            collected += 1
        except (httpx.HTTPError, ValueError) as exc:
            event = {"url": url, "status": "retry",
                     "error": type(exc).__name__, "at": now.isoformat(),
                     "approved": False}
        EVENTS.parent.mkdir(parents=True, exist_ok=True)
        with EVENTS.open("a", encoding="utf-8") as output:
            output.write(json.dumps(event, ensure_ascii=False) + "\n")
    if processed:
        state = json.loads(STATUS.read_text(encoding="utf-8"))
        state["last_run_utc"] = now.isoformat()
        state["last_batch_collected"] = collected
        state["last_batch_attempted"] = processed
        STATUS.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Tentadas {processed} fontes; coletadas {collected}. Nenhum fato aprovado automaticamente.")


if __name__ == "__main__":
    main()
