import { Link } from "react-router-dom";
import { PageHeading, SourceCard, StatusBadge } from "../components/Shared";
import { DataTable } from "../components/ui/DataTable";
import type { PublicData } from "../lib/contracts";
import { dateLabel } from "../lib/data";
export function Research({ data }: { data: PublicData }) {
  const coverage = data["coverage.json"];
  const status = data["project-status.json"];
  return (
    <>
      <PageHeading
        eyebrow="CENTRAL DE PESQUISA"
        title="Transparência em campo."
        description="O que já foi encontrado, o que falta conferir e o que pode ser afirmado. Cada indicador tem um significado e um limite."
      />
      <div className="research-stats">
        {[
          {
            value: coverage.seasons_with_leads,
            label: "temporadas com pistas",
            note: "Ao menos uma afirmação cadastrada",
          },
          {
            value: coverage.seasons_without_leads.length,
            label: "temporadas sem pistas",
            note: "Lacunas do cadastro atual",
          },
          {
            value: coverage.checked_source_pages,
            label: "página conferida",
            note: "Conferência registrada na base",
          },
          {
            value: coverage.approved_results,
            label: "resultados homologados",
            note: "Disponíveis para cálculo histórico",
          },
        ].map((item) => (
          <div key={item.label}>
            <strong>{item.value}</strong>
            <h2>{item.label}</h2>
            <p>{item.note}</p>
          </div>
        ))}
      </div>
      <section className="coverage-panel">
        <div className="section-heading">
          <div>
            <span className="eyebrow">MAPA DOCUMENTAL DA SÉRIE A</span>
            <h2>
              {coverage.seasons_with_leads} de {data.manifest.scope.seasons}{" "}
              temporadas com pistas
            </h2>
          </div>
          <Link className="text-link" to="/linha-do-tempo">
            Explorar calendário
          </Link>
        </div>
        <div className="coverage-grid">
          {data["editions.json"].editions.map((edition) => (
            <Link
              key={edition.id}
              to={`/linha-do-tempo?ano=${edition.year}`}
              className={edition.evidence_state}
              aria-label={`${edition.year}: ${edition.evidence_state !== "no_lead" ? "com pistas" : "sem pistas"}`}
            >
              {edition.year}
            </Link>
          ))}
        </div>
        <p>{coverage.denominator}</p>
        <div className="timeline-legend">
          <span>
            <i />
            Com pistas
          </span>
          <span>
            <i />
            Sem pistas
          </span>
        </div>
      </section>
      <div className="research-details">
        <section>
          <h2>Da referência à evidência</h2>
          <dl className="research-dl">
            <dt>URLs distintas</dt>
            <dd>{coverage.distinct_source_urls}</dd>
            <dt>Referências cadastradas</dt>
            <dd>{coverage.catalogued_sources}</dd>
            <dt>Candidatos a resultado</dt>
            <dd>{coverage.source_leads}</dd>
            <dt>Edições na fila de revisão</dt>
            <dd>{coverage.review_editions}</dd>
            <dt>Referências sem bytes arquivados</dt>
            <dd>{coverage.source_ids_without_archived_bytes}</dd>
            <dt>Documentos no catálogo de evidências</dt>
            <dd>{coverage.archived_evidence_documents}</dd>
            <dt>Edições com afirmações concorrentes</dt>
            <dd>{coverage.competing_claim_editions.length}</dd>
          </dl>
          <p className="section-note">
            A ausência de afirmações concorrentes no cadastro não demonstra
            ausência de controvérsias históricas.
          </p>
        </section>
        <aside className="audit-note">
          <StatusBadge kind="gold">Leitura correta do progresso</StatusBadge>
          <h2>
            {status.progress.percent}%
            <span>Estimativa anterior — não auditada.</span>
          </h2>
          <p>
            Este número foi preservado como registro histórico. Não mede a
            execução atual, a cobertura ou a qualidade da pesquisa.
          </p>
          <hr />
          <p>
            Auditoria de estado: contagens e invariantes conferidos. Resultados
            históricos ainda não homologados.
          </p>
          <small>
            Dados gerados em {dateLabel(data.manifest.generated_at)} (Brasília).{" "}
            {status.last_collection_at &&
              `Última coleta registrada: ${dateLabel(status.last_collection_at)}.`}
          </small>
        </aside>
      </div>
      <section className="section">
        <h2>Próximos passos por temporada</h2>
        <p>
          A fila vem da pesquisa Python. Prioridade documental não representa
          importância esportiva.
        </p>
        <details className="method-document">
          <summary>Ver as 55 tarefas da fila de pesquisa</summary>
          <DataTable
            caption="Fila de pesquisa — tarefas sem homologação automática"
            data={data["research-backlog.json"].tasks}
            columns={[
              { accessorKey: "year", header: "Ano" },
              { accessorKey: "priority", header: "Prioridade" },
              {
                accessorKey: "stage",
                header: "Próxima etapa",
                cell: ({ getValue }) =>
                  ({
                    discover_official_source: "Localizar fonte oficial",
                    archive_and_verify_source: "Arquivar e verificar",
                    manual_historical_review: "Revisão histórica humana",
                  })[String(getValue())] || String(getValue()),
              },
              { accessorKey: "candidate_count", header: "Pistas" },
            ]}
          />
        </details>
      </section>
      <section className="section">
        <div className="section-heading">
          <h2>Referências abertas à revisão</h2>
          <span>{coverage.catalogued_sources} referências</span>
        </div>
        {data["sources.json"].sources.map((source) => (
          <SourceCard key={source.id} source={source} />
        ))}
      </section>
    </>
  );
}
