"""Relatório legível de tarefas históricas, sem afirmar homologação."""
import argparse
from .research_backlog import research_backlog

def render_markdown(candidates=None):
    report = research_backlog(candidates)
    lines = [
        "# Fila de pesquisa — Brasileirão 1971–2025",
        "",
        "Cobertura documental: {}/{} ({:.2f}%). Não é conclusão global.".format(
            report["seasons_with_leads"], report["total_seasons"], report["lead_coverage_percent"]
        ),
        "",
        "| Ano | Próxima ação | Pistas | Fontes conferidas | Arquivadas |",
        "|---:|---|---:|---:|---:|",
    ]
    for task in report["tasks"]:
        lines.append("| {} | {} | {} | {} | {} |".format(
            task["year"], task["stage"], task["candidate_count"],
            task["checked_source_count"], task["archived_source_count"]
        ))
    return "\n".join(lines) + "\n"

def main(argv=None):
    parser = argparse.ArgumentParser(description="Relatório Markdown da pesquisa histórica")
    parser.add_argument("--output", help="Arquivo de saída; sem argumento escreve no terminal")
    args = parser.parse_args(argv)
    report = render_markdown()
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        print(report, end="")

if __name__ == "__main__":
    main()
