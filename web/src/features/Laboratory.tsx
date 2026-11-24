import { lazy, Suspense, useMemo, useState } from "react";
import * as Slider from "@radix-ui/react-slider";
import { RotateCcw, FlaskConical } from "lucide-react";
import { PageHeading } from "../components/Shared";
import { DataTable } from "../components/ui/DataTable";
import {
  simulate,
  syntheticTeams,
  consistency,
  standardize,
  logistic,
  type Weights,
} from "../lib/simulation";
import type { PublicData } from "../lib/contracts";
const ContributionChart = lazy(() => import("../components/ContributionChart"));
export default function Laboratory({ data }: { data: PublicData }) {
  const method = data["methodology.json"];
  const [weights, setWeights] = useState<Weights>(() =>
    structuredClone(method.weights),
  );
  const [series, setSeries] = useState([10, 10, 10, 10, 10]);
  const [scenario, setScenario] = useState<ReturnType<typeof simulate> | null>(
    null,
  );
  const results = useMemo(() => simulate(weights), [weights]);
  const baseline = useMemo(() => simulate(method.weights), [method.weights]);
  const [demo, setDemo] = useState(false);
  const zscores = standardize(series);
  const activeKeys = new Set(
    syntheticTeams.flatMap((t) =>
      Object.entries(t.counts).flatMap(([competition, outcomes]) =>
        Object.keys(outcomes).map((outcome) => `${competition}:${outcome}`),
      ),
    ),
  );
  return (
    <>
      <PageHeading
        eyebrow="LABORATÓRIO DA GRANDEZA"
        title="Mude o peso. Questione o resultado."
        description="Entenda o modelo experimental e explore o efeito de suas escolhas. Ajustes locais não alteram a metodologia do projeto."
      />
      <div className="simulation-notice">
        <FlaskConical />
        <div>
          <strong>Simulação com dados sintéticos</strong>
          <p>
            Equipes Aurora, Horizonte e Vértice são fictícias. Seus resultados
            foram inventados apenas para demonstrar o cálculo. Nenhum clube real
            recebe pontuação aqui.
          </p>
        </div>
        <button
          className="button primary"
          onClick={() => setDemo((value) => !value)}
        >
          {demo ? "Fechar simulação" : "Iniciar simulação"}
        </button>
      </div>
      {!demo ? (
        <div className="lab-intro">
          <h2>
            Pesos reais do código.
            <br />
            <em>Exemplos inteiramente fictícios.</em>
          </h2>
          <p>
            Ative o modo de simulação para ajustar os critérios, comparar um
            cenário e ver contribuições. A classificação do exemplo nunca é um
            ranking histórico do IGFB.
          </p>
        </div>
      ) : (
        <>
          <div className="lab-toolbar">
            <span className="eyebrow">
              MODO SINTÉTICO ATIVO · SOMA EXPERIMENTAL
            </span>
            <button
              className="button secondary small"
              onClick={() => {
                setWeights(structuredClone(method.weights));
                setScenario(null);
              }}
            >
              <RotateCcw size={16} />
              Restaurar pesos do modelo
            </button>
          </div>
          <div className="lab-layout">
            <section className="weight-panel">
              <h2>Controle os critérios</h2>
              <p>Os critérios usados no exemplo aparecem primeiro.</p>
              {[true, false].map((active) => (
                <div key={String(active)}>
                  {!active && <h3>Demais critérios do modelo</h3>}
                  {Object.entries(weights).flatMap(([competition, outcomes]) =>
                    Object.entries(outcomes)
                      .filter(
                        ([outcome]) =>
                          activeKeys.has(`${competition}:${outcome}`) ===
                          active,
                      )
                      .map(([outcome, weight]) => (
                        <WeightControl
                          key={`${competition}:${outcome}`}
                          label={`${method.competition_labels[competition]} · ${method.outcome_labels[outcome]}`}
                          value={weight}
                          original={method.weights[competition][outcome]}
                          onChange={(value) =>
                            setWeights((current) => ({
                              ...current,
                              [competition]: {
                                ...current[competition],
                                [outcome]: value,
                              },
                            }))
                          }
                        />
                      )),
                  )}
                </div>
              ))}
            </section>
            <section className="lab-results">
              <span className="eyebrow">CLASSIFICAÇÃO DO EXEMPLO FICTÍCIO</span>
              <h2>
                Três trajetórias inventadas.
                <br />
                Um cenário em teste.
              </h2>
              <DataTable
                caption="Ranking sintético — equipes fictícias, soma experimental"
                data={results}
                columns={[
                  { accessorKey: "position", header: "Pos." },
                  { accessorKey: "name", header: "Equipe fictícia" },
                  {
                    accessorKey: "score",
                    header: "Pontos",
                    cell: ({ getValue }) => (
                      <code>{Number(getValue()).toLocaleString("pt-BR")}</code>
                    ),
                  },
                  {
                    id: "variation",
                    header: "Δ modelo",
                    cell: ({ row }) => (
                      <code>
                        {row.original.score -
                          (baseline.find((item) => item.id === row.original.id)
                            ?.score || 0)}
                      </code>
                    ),
                  },
                ]}
              />
              <p className="section-note">
                Empates exatos compartilham a posição, pulando a posição
                seguinte. Δ indica a diferença de pontos em relação aos pesos
                exportados.
              </p>
              <Suspense fallback={<p>Carregando gráfico…</p>}>
                <ContributionChart
                  rows={results}
                  labels={method.competition_labels}
                />
              </Suspense>
              <DataTable
                caption="Contribuição dos critérios — alternativa acessível ao gráfico sintético"
                data={results.flatMap((row) =>
                  row.contributions.map((item) => ({
                    team: row.name,
                    criterion: method.competition_labels[item.criterion],
                    points: item.value,
                  })),
                )}
                columns={[
                  { accessorKey: "team", header: "Equipe" },
                  { accessorKey: "criterion", header: "Critério" },
                  { accessorKey: "points", header: "Pontos" },
                ]}
              />
              <button
                className="button secondary"
                onClick={() => setScenario(structuredClone(results))}
              >
                Guardar cenário nesta sessão
              </button>
              {scenario && (
                <div
                  className="saved-scenario"
                  role="status"
                  aria-label="Cenário guardado"
                >
                  <h3>Cenário guardado × cenário atual</h3>
                  <DataTable
                    caption="Comparação local de cenários sintéticos"
                    data={results.map((row) => ({
                      team: row.name,
                      before: scenario.find((item) => item.id === row.id)!
                        .score,
                      now: row.score,
                      rankBefore: scenario.find((item) => item.id === row.id)!
                        .position,
                      rankNow: row.position,
                    }))}
                    columns={[
                      { accessorKey: "team", header: "Equipe" },
                      { accessorKey: "before", header: "Antes" },
                      { accessorKey: "now", header: "Agora" },
                      { accessorKey: "rankBefore", header: "Pos. antes" },
                      { accessorKey: "rankNow", header: "Pos. agora" },
                    ]}
                  />
                </div>
              )}
              <details className="method-document">
                <summary>Ver os dados sintéticos utilizados</summary>
                <DataTable
                  caption="Contagens inventadas por equipe; nenhuma corresponde a clubes reais"
                  data={syntheticTeams.flatMap((team) =>
                    Object.entries(team.counts).flatMap(
                      ([competition, outcomes]) =>
                        Object.entries(outcomes).map(([outcome, count]) => ({
                          team: team.name,
                          criterion: method.competition_labels[competition],
                          outcome: method.outcome_labels[outcome],
                          count,
                        })),
                    ),
                  )}
                  columns={[
                    { accessorKey: "team", header: "Equipe" },
                    { accessorKey: "criterion", header: "Critério" },
                    { accessorKey: "outcome", header: "Resultado" },
                    { accessorKey: "count", header: "Quantidade" },
                  ]}
                />
              </details>
            </section>
          </div>
        </>
      )}
      <section className="math-section">
        <span className="eyebrow">COMO A MATEMÁTICA ENTRA EM CAMPO</span>
        <h2>Regularidade também tem forma.</h2>
        <p>
          Experimente uma série de cinco temporadas fictícias. Estes componentes
          são independentes e ainda não compõem o índice definitivo.
        </p>
        <div className="series-inputs">
          {series.map((value, index) => (
            <label key={index}>
              Ano {index + 1}
              <input
                type="number"
                inputMode="numeric"
                min={0}
                max={10000}
                value={value}
                onChange={(event) =>
                  setSeries((current) =>
                    current.map((v, i) =>
                      i === index
                        ? Math.max(
                            0,
                            Math.min(10000, Number(event.target.value) || 0),
                          )
                        : v,
                    ),
                  )
                }
              />
            </label>
          ))}
        </div>
        <div className="math-grid">
          <article>
            <span className="eyebrow">CONSISTÊNCIA TEMPORAL</span>
            <strong>{consistency(series).toFixed(3)}</strong>
            <code>J = (Σp)² / (T × Σp²)</code>
            <p>
              Índice de Jain: usa valores não negativos, incluindo anos com
              zero. Penalidades negativas não entram diretamente.
            </p>
          </article>
          <article>
            <span className="eyebrow">PADRONIZAÇÃO</span>
            <strong>{zscores[0].toFixed(3)}</strong>
            <code>z = (p − μ) / σ</code>
            <p>
              Exemplo didático do primeiro valor contra os cinco valores acima.
              Na aplicação sazonal, a população de referência deverá ser
              definida por temporada.
            </p>
          </article>
          <article>
            <span className="eyebrow">TRANSFORMAÇÃO LOGÍSTICA</span>
            <strong>{logistic(zscores[0]).toFixed(2)}</strong>
            <code>I(z) = 100 / (1 + e⁻ᶻ)</code>
            <p>
              Transformação do z mostrado. Não é probabilidade, chance de título
              ou pontuação histórica homologada.
            </p>
          </article>
        </div>
        <p className="section-note">
          Um envelope entre cenários não é intervalo de confiança. A fração de
          cenários em primeiro lugar não é uma probabilidade estatística.
        </p>
      </section>
    </>
  );
}
function WeightControl({
  label,
  value,
  original,
  onChange,
}: {
  label: string;
  value: number;
  original: number;
  onChange: (value: number) => void;
}) {
  const negative = original < 0;
  const min = negative ? original * 2 : 0;
  const max = negative ? 0 : Math.max(original * 2, 20);
  return (
    <div className="weight-control">
      <div>
        <span>{label}</span>
        <output>{value}</output>
      </div>
      <Slider.Root
        className="slider-root"
        min={min}
        max={max}
        step={1}
        value={[value]}
        onValueChange={(values) => onChange(values[0])}
      >
        <Slider.Track className="slider-track">
          <Slider.Range className="slider-range" />
        </Slider.Track>
        <Slider.Thumb className="slider-thumb" aria-label={label} />
      </Slider.Root>
      <small>Modelo experimental: {original}</small>
    </div>
  );
}
