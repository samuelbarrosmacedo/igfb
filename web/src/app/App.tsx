import { Component, Suspense, lazy, useEffect, type ReactNode } from "react";
import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import * as Dialog from "@radix-ui/react-dialog";
import { Menu, X, ExternalLink, RefreshCw } from "lucide-react";
import { usePublicData, useLatestManifest, dateLabel } from "../lib/data";
import { Home } from "../features/Home";

const Clubs = lazy(() =>
  import("../features/Clubs").then((m) => ({ default: m.Clubs })),
);
const ClubProfile = lazy(() =>
  import("../features/Clubs").then((m) => ({ default: m.ClubProfile })),
);
const Ranking = lazy(() =>
  import("../features/Ranking").then((m) => ({ default: m.Ranking })),
);
const Research = lazy(() =>
  import("../features/Research").then((m) => ({ default: m.Research })),
);
const Timeline = lazy(() =>
  import("../features/Timeline").then((m) => ({ default: m.Timeline })),
);
const Compare = lazy(() =>
  import("../features/Compare").then((m) => ({ default: m.Compare })),
);
const Methodology = lazy(() => import("../features/Methodology"));
const Laboratory = lazy(() => import("../features/Laboratory"));
declare const __BUILD_TIME__: string;
const links = [
  ["/ranking", "Ranking"],
  ["/clubes", "Clubes"],
  ["/comparador", "Comparador"],
  ["/laboratorio", "Laboratório"],
  ["/linha-do-tempo", "Linha do tempo"],
  ["/metodologia", "Metodologia"],
  ["/pesquisa", "Pesquisa"],
];
function Navigation({ mobile = false }: { mobile?: boolean }) {
  return (
    <nav aria-label={mobile ? "Navegação móvel" : "Navegação principal"}>
      {links.map(([url, label]) =>
        mobile ? (
          <Dialog.Close asChild key={url}>
            <NavLink to={url}>{label}</NavLink>
          </Dialog.Close>
        ) : (
          <NavLink to={url} key={url}>
            {label}
          </NavLink>
        ),
      )}
    </nav>
  );
}
function RouteFocus() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "instant" });
    const id = window.setTimeout(() => {
      const title = document.querySelector("h1");
      title?.focus({ preventScroll: true });
      if (title)
        document.title = `${title.innerText.replace(/\s+/g, " ")} · IGFB`;
    }, 120);
    return () => clearTimeout(id);
  }, [pathname]);
  return null;
}
class PageBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <div className="load-state" role="alert">
        <h2>Não foi possível abrir esta página.</h2>
        <p>Recarregue para buscar a versão atual do site.</p>
        <button
          className="button primary"
          onClick={() => window.location.reload()}
        >
          Recarregar
        </button>
      </div>
    ) : (
      this.props.children
    );
  }
}
export default function App() {
  const data = usePublicData();
  const latest = useLatestManifest();
  const client = useQueryClient();
  const location = useLocation();
  const hasUpdate =
    data.data &&
    latest.data &&
    data.data.manifest.dataset_id !== latest.data.dataset_id;
  return (
    <>
      <a
        className="skip-link"
        href="#conteudo"
        onClick={(event) => {
          event.preventDefault();
          document.getElementById("conteudo")?.focus();
        }}
      >
        Pular para o conteúdo
      </a>
      <div className="topline">
        <div className="container">
          <span>HISTÓRIA. MÉTODO. FUTEBOL.</span>
          <span className="topline-status">
            <span /> PESQUISA EM ANDAMENTO
          </span>
        </div>
      </div>
      <header className="site-header">
        <div className="container header-inner">
          <Link to="/" className="brand" aria-label="IGFB — início">
            <span className="brand-symbol">
              <i />
              <i />
              <i />
            </span>
            IGFB
            <span className="brand-description">
              ÍNDICE DE GRANDEZA
              <br />
              DO FUTEBOL BRASILEIRO
            </span>
          </Link>
          <div className="desktop-nav">
            <Navigation />
          </div>
          <Dialog.Root>
            <Dialog.Trigger
              className="icon-button mobile-menu"
              aria-label="Abrir menu"
            >
              <Menu />
            </Dialog.Trigger>
            <Dialog.Portal>
              <Dialog.Overlay className="dialog-overlay" />
              <Dialog.Content className="mobile-nav">
                <Dialog.Title>Explore o IGFB</Dialog.Title>
                <Dialog.Description>
                  História, pesquisa e transparência.
                </Dialog.Description>
                <Navigation mobile />
                <Dialog.Close
                  className="icon-button dialog-close"
                  aria-label="Fechar menu"
                >
                  <X />
                </Dialog.Close>
              </Dialog.Content>
            </Dialog.Portal>
          </Dialog.Root>
        </div>
      </header>
      {hasUpdate && (
        <div className="update-banner" role="status">
          <span>Há uma nova publicação de dados disponível.</span>
          <button
            onClick={() =>
              client.invalidateQueries({ queryKey: ["public-data"] })
            }
          >
            <RefreshCw size={16} />
            Atualizar dados
          </button>
        </div>
      )}
      <main id="conteudo" className="container" tabIndex={-1}>
        <RouteFocus />
        {data.isPending ? (
          <div className="load-state" role="status">
            <span className="loading-line" />
            <h1 tabIndex={-1}>Abrindo o arquivo.</h1>
            <p>Conferindo o manifesto e a integridade dos dados.</p>
          </div>
        ) : data.isError ? (
          <div className="load-state" role="alert">
            <h1 tabIndex={-1}>O arquivo não carregou.</h1>
            <p>
              Verifique sua conexão e tente novamente. Dados incompletos ou
              inválidos não serão exibidos.
            </p>
            <button className="button primary" onClick={() => data.refetch()}>
              Tentar novamente
            </button>
          </div>
        ) : (
          <PageBoundary key={location.pathname}>
            <Suspense
              fallback={
                <div className="load-state" role="status">
                  Abrindo seção…
                </div>
              }
            >
              <Routes>
                <Route path="/" element={<Home data={data.data} />} />
                <Route path="/ranking" element={<Ranking data={data.data} />} />
                <Route path="/clubes" element={<Clubs data={data.data} />} />
                <Route
                  path="/clubes/:id"
                  element={<ClubProfile data={data.data} />}
                />
                <Route
                  path="/comparador"
                  element={<Compare data={data.data} />}
                />
                <Route
                  path="/laboratorio"
                  element={<Laboratory data={data.data} />}
                />
                <Route
                  path="/linha-do-tempo"
                  element={<Timeline data={data.data} />}
                />
                <Route
                  path="/metodologia"
                  element={<Methodology data={data.data} />}
                />
                <Route
                  path="/pesquisa"
                  element={<Research data={data.data} />}
                />
                <Route
                  path="*"
                  element={
                    <div className="load-state">
                      <h1 tabIndex={-1}>Página fora de campo.</h1>
                      <Link className="button primary" to="/">
                        Voltar ao início
                      </Link>
                    </div>
                  }
                />
              </Routes>
            </Suspense>
          </PageBoundary>
        )}
      </main>
      <footer className="site-footer">
        <div className="container">
          <div className="footer-top">
            <Link to="/" className="brand">
              IGFB
              <span className="brand-description">
                A GRANDEZA SE DEBATE.
                <br />
                OS NÚMEROS SE VERIFICAM.
              </span>
            </Link>
            <a
              href="https://github.com/samuelbarrosmacedo/igfb"
              target="_blank"
              rel="noreferrer"
            >
              Projeto no GitHub <ExternalLink size={15} />
            </a>
          </div>
          <div className="footer-bottom">
            <p>
              Um observatório em construção. Nenhum ranking definitivo
              publicado.
            </p>
            {data.data && (
              <p>
                Dados gerados: {dateLabel(data.data.manifest.generated_at)}{" "}
                (Brasília)
                <br />
                <a
                  href={`https://github.com/samuelbarrosmacedo/igfb/tree/${data.data.manifest.source_commit}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Origem:{" "}
                  <code>{data.data.manifest.source_commit.slice(0, 7)}</code>
                </a>{" "}
                · Build: {dateLabel(__BUILD_TIME__)}
              </p>
            )}
          </div>
        </div>
      </footer>
    </>
  );
}
