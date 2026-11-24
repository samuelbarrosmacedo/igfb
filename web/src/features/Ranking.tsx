import { Link } from "react-router-dom";
import { FileSearch, LibraryBig, ShieldCheck, Flag } from "lucide-react";
import { PageHeading, StatusBadge } from "../components/Shared";
import type { PublicData } from "../lib/contracts";
export function Ranking({ data }: { data: PublicData }) {
  const coverage = data["coverage.json"];
  return (
    <>
      <PageHeading
        eyebrow="RANKING HISTÓRICO"
        title="A posição vem depois da prova."
        description={data["ranking.json"].reason}
      />
      <section className="ranking-gate">
        <div className="gate-watermark" aria-hidden="true">
          IGFB
        </div>
        <div>
          <StatusBadge kind="gold">Publicação bloqueada</StatusBadge>
          <h2>
            O próximo grande debate
            <br />
            merece uma base sólida.
          </h2>
          <p>
            O modelo já tem regras experimentais. Para ordenar clubes, cada
            resultado precisa de evidência arquivada, revisão e decisão formal.
            A publicação ainda exige aprovação expressa.
          </p>
          <Link className="button primary" to="/pesquisa">
            Ver o estado da pesquisa
          </Link>
        </div>
        <div className="gate-stat">
          <strong>{coverage.approved_results}</strong>
          <span>resultados homologados</span>
          <small>Sem pontuação histórica publicável.</small>
        </div>
      </section>
      <ol className="process-list">
        {[
          {
            icon: FileSearch,
            title: "Encontrar",
            text: `${coverage.source_leads} pistas em ${coverage.catalogued_sources} referências documentais.`,
            state: "Em pesquisa",
          },
          {
            icon: LibraryBig,
            title: "Arquivar e confrontar",
            text: "Preservar os bytes, calcular SHA-256 e examinar as afirmações.",
            state: "Catálogo de evidências pendente",
          },
          {
            icon: ShieldCheck,
            title: "Homologar",
            text: "Registrar decisão, revisor, justificativa e possibilidade de revogação.",
            state: "Nenhum resultado aprovado",
          },
          {
            icon: Flag,
            title: "Publicar",
            text: "Auditar cobertura, calibrar o modelo e autorizar a classificação.",
            state: "Aguardando aprovação",
          },
        ].map((item) => (
          <li key={item.title}>
            <item.icon />
            <h3>{item.title}</h3>
            <p>{item.text}</p>
            <span>{item.state}</span>
          </li>
        ))}
      </ol>
      <div className="section-banner">
        <div>
          <h3>Quer experimentar a lógica?</h3>
          <p>
            O laboratório usa equipes fictícias e dados sintéticos, sem atribuir
            pontos a clubes reais.
          </p>
        </div>
        <Link className="button secondary" to="/laboratorio">
          Abrir laboratório
        </Link>
      </div>
    </>
  );
}
