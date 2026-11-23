import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Link } from "react-router-dom";
import { ExternalLink } from "lucide-react";
import { PageHeading, StatusBadge } from "../components/Shared";
import { DataTable } from "../components/ui/DataTable";
import type { PublicData } from "../lib/contracts";
export default function Methodology({ data }: { data: PublicData }) {
  const method = data["methodology.json"];
  const weights = Object.entries(method.weights).flatMap(
    ([competition, outcomes]) =>
      Object.entries(outcomes).map(([outcome, weight]) => ({
        competition: method.competition_labels[competition] || competition,
        outcome: method.outcome_labels[outcome] || outcome,
        weight,
      })),
  );
  return (
    <>
      <PageHeading
        eyebrow="METODOLOGIA E TRANSPARÊNCIA"
        title="O método precisa jogar aberto."
        description="Critérios explícitos, documentos verificáveis e espaço para revisão. Entenda o que o IGFB considera — e o que ainda precisa resolver."
      />
      <div className="method-intro">
        <div>
          <StatusBadge kind="green">Recorte atual</StatusBadge>
          <h2>
            {method.scope.first_year}
            <span>—</span>
            {method.scope.last_year}
          </h2>
          <p>
            O Campeonato Brasileiro Série A começa em 1971 neste modelo. A
            última temporada incluída é 2025.
          </p>
        </div>
        <div>
          <h3>Exclusões integrais</h3>
          <ul>
            {method.exclusions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <p>
            Fora de pontuações, rankings, participações e demais métricas do
            IGFB.
          </p>
          <h3>A convenção de 1987</h3>
          <p>
            Flamengo campeão por {method.flamengo_1987}. Não representa consenso
            institucional ou jurídico.
          </p>
        </div>
      </div>
      <section className="section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">MATRIZ DO MODELO</span>
            <h2>Quanto vale cada resultado?</h2>
          </div>
          <StatusBadge kind="gold">Pesos experimentais</StatusBadge>
        </div>
        <p>
          Valores exportados diretamente do núcleo Python. Ainda sujeitos à
          calibração; não constituem um índice matemático definitivo.
        </p>
        <DataTable
          data={weights}
          caption="Pesos experimentais do IGFB — valores do código Python"
          columns={[
            { accessorKey: "competition", header: "Critério" },
            { accessorKey: "outcome", header: "Resultado" },
            {
              accessorKey: "weight",
              header: "Peso",
              cell: ({ getValue }) => (
                <code
                  className={Number(getValue()) < 0 ? "negative" : "positive"}
                >
                  {Number(getValue()) > 0 ? "+" : ""}
                  {String(getValue())}
                </code>
              ),
            },
          ]}
        />
        <Link className="text-link" to="/laboratorio">
          Investigar os pesos no laboratório
        </Link>
      </section>
      <section className="section">
        <h2>Do documento ao número</h2>
        <p>
          Os protocolos abaixo são os textos reais do repositório, incluídos
          nesta publicação. Abra cada documento para aprofundar a leitura.
        </p>
        {method.documents.map((document) => (
          <details className="method-document" key={document.path}>
            <summary>
              {document.path.includes("DECISOES")
                ? "Homologação, integridade e revogação"
                : "Estados de evidência, regras e robustez"}
            </summary>
            <div className="document-meta">
              <a href={document.url} target="_blank" rel="noreferrer">
                Ver no commit de origem <ExternalLink size={14} />
              </a>
              <p>SHA-256 do documento</p>
              <code>{document.sha256}</code>
            </div>
            <div className="prose">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {document.markdown}
              </ReactMarkdown>
            </div>
          </details>
        ))}
      </section>
      <div className="section-banner">
        <div>
          <h3>O modelo continua em construção.</h3>
          <p>
            População de comparação, escalas e coeficientes precisam de
            definição e validação antes de qualquer índice definitivo.
          </p>
        </div>
        <Link className="button secondary" to="/pesquisa">
          Ver pendências
        </Link>
      </div>
    </>
  );
}
