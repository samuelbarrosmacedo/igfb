"""Fila determinística de fontes, sem inferir resultados esportivos."""
from urllib.parse import urlparse


def build_source_queue(seed_sources, rules):
    start = int(rules["baseline_year"])
    end = int(rules["through_year"])
    if start != 1971 or end < start or end > 2025:
        raise ValueError("Recorte histórico inesperado: 1971 a 2025")
    sources = [dict(source) for source in seed_sources]
    for year in range(start, end + 1):
        sources.append({
            "url": f"https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_{year}",
            "trust": "exploratory",
            "topic": "brasileirao",
            "edition": year,
        })
    unique = {}
    for source in sources:
        url = source.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            continue
        if url not in unique:
            unique[url] = dict(source)
        else:
            # Preserva o ano explícito mesmo quando a fonte foi cadastrada antes.
            for field in ("edition", "topic", "trust"):
                if unique[url].get(field) is None and source.get(field) is not None:
                    unique[url][field] = source[field]
    return list(unique.values())
