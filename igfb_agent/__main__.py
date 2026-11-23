import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "config" / "seed_sources.json"
EVENTS = ROOT / "state" / "events.jsonl"
STATUS = ROOT / "state" / "status.json"

def main():
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    events = [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    seen = {e["url"] for e in events if e.get("status") == "collected"}
    limit = max(0, min(int(os.getenv("IGFB_FETCH_LIMIT", "2")), 5))
    completed = 0
    for source in sources:
        if completed >= limit:
            break
        url = source["url"]
        if url in seen or urlparse(url).scheme != "https":
            continue
        try:
            with httpx.Client(timeout=15, follow_redirects=True, headers={"User-Agent":"IGFBResearch/0.2 (historical data research)"}) as client:
                response = client.get(url)
                response.raise_for_status()
            text = BeautifulSoup(response.text, "html.parser").get_text(" ", strip=True)
            if not text:
                raise ValueError("Empty document")
            event = {"url":url, "status":"collected", "sha256":hashlib.sha256(text.encode()).hexdigest(),
                     "characters":len(text), "trust":source["trust"], "topic":source["topic"],
                     "at":datetime.now(timezone.utc).isoformat(), "approved":False}
            completed += 1
        except Exception as exc:
            event = {"url":url, "status":"retry", "error":type(exc).__name__,
                     "at":datetime.now(timezone.utc).isoformat(), "approved":False}
        EVENTS.parent.mkdir(parents=True, exist_ok=True)
        with EVENTS.open("a", encoding="utf-8") as out:
            out.write(json.dumps(event, ensure_ascii=False)+"\n")
    state = json.loads(STATUS.read_text(encoding="utf-8"))
    state["last_run_utc"] = datetime.now(timezone.utc).isoformat()
    state["last_batch_collected"] = completed
    STATUS.write_text(json.dumps(state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Coletadas {completed} fontes. Nenhum dado aprovado automaticamente.")

if __name__ == "__main__":
    main()
