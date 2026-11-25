import { useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { PageHeading, StatusBadge, SourcesList } from "../components/Shared";
import { Select } from "../components/ui/Select";
import {
  allEditions,
  CandidateClaims,
  CatalogSources,
  editionStates,
} from "./Competitions";
import type { PublicData } from "../lib/contracts";
export function Timeline({ data }: { data: PublicData }) {
  const [params, setParams] = useSearchParams();
  const [decade, setDecade] = useState("all");
  const [state, setState] = useState("all");
  const competition =
    params.get("competicao") ||
    data["observatory.json"].competitions[0]?.id ||
    "";
  const editions = allEditions(data).filter(
    (e) => e.competition_id === competition,
  );
  const selected =
    editions.find((e) => e.id === params.get("edicao")) ||
    editions.find((e) => e.year === Number(params.get("ano"))) ||
    editions.at(-1);
  const decades = Array.from(
    new Set(editions.map((e) => Math.floor(e.year / 10) * 10)),
  ).sort();
  const history = (id: string) =>
    data["editions.json"].editions.find((e) => e.id === id);
  const visible = editions
    .filter(
      (e) =>
        (decade === "all" || Math.floor(e.year / 10) * 10 === Number(decade)) &&
        (state === "all" ||
          (state === "lead_found"
            ? !!history(e.id)?.source_ids.length
            : !history(e.id)?.source_ids.length)),
    )
    .sort((a, b) => a.year - b.year);
  const choose = (id: string) => {
    const e = editions.find((e) => e.id === id)!;
    setParams({ competicao: competition, ano: String(e.year), edicao: e.id });
  };
  return (
    <>
      <PageHeading
        eyebrow="ALMANAQUE IGFB"
        title="O tempo também joga."
        description="Calendários e fontes do catálogo. Uma edição sem dados é uma lacuna da pesquisa, não da história."
      />
      <div className="toolbar timeline-toolbar">
        <Select
          label="Competição"
          value={competition}
          onChange={(v) => {
            setParams({ competicao: v });
            setDecade("all");
          }}
          options={data["observatory.json"].competitions.map((c) => ({
            value: c.id,
            label: c.name,
          }))}
        />
        {selected && (
          <Select
            label="Temporada"
            value={selected.id}
            onChange={choose}
            options={editions.map((e) => ({ value: e.id, label: e.label }))}
          />
        )}
        <Select
          label="Estado documental"
          value={state}
          onChange={setState}
          options={[
            { value: "all", label: "Todos os estados" },
            { value: "lead_found", label: "Com pistas históricas" },
            { value: "no_lead", label: "Sem pistas históricas" },
          ]}
        />
      </div>
      <div className="decades" aria-label="Filtrar por década">
        {["all", ...decades.map(String)].map((d) => (
          <button
            key={d}
            aria-pressed={d === decade}
            onClick={() => setDecade(d)}
          >
            {d === "all" ? "Todas" : `${d}s`}
          </button>
        ))}
      </div>
      {!selected ? (
        <p className="empty-note" role="status">
          O calendário desta competição ainda não foi incorporado. As edições
          aparecerão quando forem cadastradas.
        </p>
      ) : (
        <div className="timeline-layout">
          <div className="year-grid">
            {visible.map((e) => (
              <button
                key={e.id}
                className={`${history(e.id)?.source_ids.length ? "lead_found" : "no_lead"} ${selected.id === e.id ? "selected" : ""}`}
                onClick={() => choose(e.id)}
                aria-pressed={selected.id === e.id}
              >
                <strong>{e.year}</strong>
                <span>
                  {history(e.id)?.source_ids.length
                    ? "Com pistas"
                    : editionStates[e.status]}
                </span>
              </button>
            ))}
          </div>
          <section className="year-detail">
            <div className="year-display">{selected.year}</div>
            <StatusBadge>{editionStates[selected.status]}</StatusBadge>
            <h2>
              {
                data["observatory.json"].competitions.find(
                  (c) => c.id === competition,
                )?.name
              }
            </h2>
            <code>{selected.id}</code>
            <p>Resultados históricos ainda não homologados.</p>
            <Link
              className="text-link"
              to={`/competicoes/${competition}/edicoes/${encodeURIComponent(selected.id)}`}
            >
              Abrir edição e registros
            </Link>
            {selected.year === 1987 && (
              <p className="convention">
                {data["methodology.json"].flamengo_1987}
              </p>
            )}
            <CatalogSources data={data} ids={selected.source_ids} />
            {history(selected.id) && (
              <SourcesList data={data} ids={history(selected.id)!.source_ids} />
            )}
          </section>
        </div>
      )}
      {selected && <CandidateClaims data={data} editionId={selected.id} />}
    </>
  );
}
