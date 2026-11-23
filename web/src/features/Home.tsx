import { Link } from "react-router-dom";
import { BookOpen, ScanLine, FlaskConical } from "lucide-react";
import type { PublicData } from "../lib/contracts";
export function Home({ data }: { data: PublicData }) {
  const coverage = data["coverage.json"];
  const scope = data.manifest.scope;
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">
            <span /> OBSERVATÓRIO DO FUTEBOL BRASILEIRO
          </div>
          <h1 tabIndex={-1}>
            A GRANDEZA
            <br />
            TEM HISTÓRIA.
            <br />
            <em>
              AGORA TERÁ
              <br className="mobile-break" /> MÉTODO.
            </em>
          </h1>
          <p>
            O futebol vive de paixão. A história precisa de evidências. Um novo
            olhar sobre o que faz um clube ser grande.
          </p>
          <div className="hero-actions">
            <Link className="button primary" to="/metodologia">
              Conheça o método
            </Link>
            <Link className="button secondary" to="/clubes">
              Explore os clubes
            </Link>
          </div>
          <div className="hero-footnote">
            <span className="live-dot" />
            Pesquisa aberta · resultados em homologação
          </div>
        </div>
        <div className="hero-art">
          <img src={`${import.meta.env.BASE_URL}assets/pitch.svg`} alt="" />
          <div className="art-caption">
            <span>O CAMPO É O MESMO.</span>
            <strong>As histórias, não.</strong>
          </div>
          <div className="art-years">
            <span>{scope.first_year}</span>
            <i />
            <span>{scope.last_year}</span>
          </div>
        </div>
      </section>
      <section className="research-strip" aria-label="Estado atual da pesquisa">
        <div className="strip-title">
          <ScanLine size={22} />
          <div>
            <span className="eyebrow">DOSSIÊ ABERTO</span>
            <strong>O rigor começa aqui.</strong>
          </div>
        </div>
        <div className="strip-metric">
          <strong>{scope.seasons}</strong>
          <span>temporadas no recorte</span>
        </div>
        <div className="strip-metric">
          <strong>{coverage.seasons_with_leads}</strong>
          <span>temporadas com pistas</span>
        </div>
        <div className="strip-metric">
          <strong>{coverage.approved_results}</strong>
          <span>resultados homologados</span>
        </div>
        <Link className="text-link" to="/pesquisa">
          Acompanhe a pesquisa
        </Link>
      </section>
      <section className="home-editorial">
        <div>
          <div className="eyebrow">PARA ALÉM DA TAÇA</div>
          <h2>
            Uma discussão antiga.
            <br />
            <em>Uma base nova.</em>
          </h2>
          <p>
            Títulos contam. Trajetórias também. O IGFB investiga conquistas,
            campanhas e permanência na elite com critérios explícitos e fontes
            rastreáveis.
          </p>
          <p className="muted">
            Sem atalhos entre encontrar uma notícia e homologar um resultado.
          </p>
        </div>
        <div className="editorial-links">
          <Link to="/linha-do-tempo">
            <span className="editorial-icon">
              <BookOpen />
            </span>
            <div>
              <span className="eyebrow">O ARQUIVO</span>
              <h3>
                55 temporadas.
                <br />
                Histórias para investigar.
              </h3>
              <p>
                Percorra as décadas e veja onde já existem pistas documentais.
              </p>
            </div>
          </Link>
          <Link to="/laboratorio">
            <span className="editorial-icon gold">
              <FlaskConical />
            </span>
            <div>
              <span className="eyebrow">O LABORATÓRIO</span>
              <h3>
                E se os pesos
                <br />
                fossem diferentes?
              </h3>
              <p>
                Explore o modelo experimental em simulações claramente
                identificadas.
              </p>
            </div>
          </Link>
        </div>
      </section>
      <section className="ranking-teaser">
        <span className="eyebrow">RANKING HISTÓRICO</span>
        <h2>
          Antes da posição,
          <br />
          <em>a comprovação.</em>
        </h2>
        <div>
          <p>{data["ranking.json"].reason}</p>
          <Link className="button secondary" to="/ranking">
            Entenda a preparação
          </Link>
        </div>
      </section>
    </>
  );
}
