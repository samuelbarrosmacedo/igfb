"""Relatório legível de tarefas históricas, sem afirmar homologação."""
import argparse
import csv
import io
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

def render_csv(candidates=None):
    """CSV para revisão em planilhas, sem aprovar qualquer resultado."""
    report = research_backlog(candidates)
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(("year", "edition_id", "priority", "stage", "candidate_count",
                     "source_ids", "checked_source_count", "archived_source_count", "approved"))
    for task in report["tasks"]:
        writer.writerow((
            task["year"], task["edition_id"], task["priority"], task["stage"],
            task["candidate_count"], ";".join(task["source_ids"]),
            task["checked_source_count"], task["archived_source_count"], "false"
        ))
    return output.getvalue()

def main(argv=None):
    parser = argparse.ArgumentParser(description="Relatório Markdown da pesquisa histórica")
    parser.add_argument("--output", help="Arquivo de saída; sem argumento escreve no terminal")
    parser.add_argument("--format", choices=("markdown", "csv"), default="markdown")
    args = parser.parse_args(argv)
    report = render_csv() if args.format == "csv" else render_markdown()
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        print(report, end="")

if __name__ == "__main__":
    main()
