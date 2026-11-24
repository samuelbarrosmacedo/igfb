import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { PageHeading, SourcesList, StatusBadge } from "../components/Shared";
import { Select } from "../components/ui/Select";
import type { PublicData } from "../lib/contracts";
export function Timeline({ data }: { data: PublicData }) {
  const [params, setParams] = useSearchParams();
  const editions = data["editions.json"].editions;
  const selected =
    editions.find((e) => e.year === Number(params.get("ano"))) || editions[0];
  const [decade, setDecade] = useState(
    String(Math.floor(selected.year / 10) * 10),
  );
  const [state, setState] = useState("all");
  const [competition, setCompetition] = useState("brasileirao");
  const visible = editions.filter(
    (e) =>
      (decade === "all" || Math.floor(e.year / 10) * 10 === Number(decade)) &&
      (state === "all" ||
        (state === "lead_found"
          ? e.evidence_state !== "no_lead"
          : e.evidence_state === state)),
  );
  function selectYear(year: number) {
    setParams({ ano: String(year) });
    setDecade(String(Math.floor(year / 10) * 10));
  }
  return (
    <>
      <PageHeading
        eyebrow="ALMANAQUE IGFB · 1971–2025"
        title="O tempo também joga."
        description="Navegue pelo calendário e acompanhe a construção do arquivo. Um ano sem pistas é uma lacuna da pesquisa, não da história."
      />
      <div className="decades" aria-label="Filtrar por década">
        {["all", "1970", "1980", "1990", "2000", "2010", "2020"].map(
          (value) => (
            <button
              key={value}
              aria-pressed={decade === value}
              onClick={() => setDecade(value)}
            >
              {value === "all" ? "Todas" : `${value.slice(0, 3)}0s`}
            </button>
          ),
        )}
      </div>
      <div className="toolbar timeline-toolbar">
        <Select
          label="Competição"
          value={competition}
          onChange={setCompetition}
          options={Object.entries(data["methodology.json"].competition_labels)
            .filter(([id]) => !id.startsWith("relegation"))
            .map(([value, label]) => ({ value, label }))}
        />
        <Select
          label="Temporada"
          value={String(selected.year)}
          onChange={(value) => selectYear(Number(value))}
          options={editions.map((e) => ({
            value: String(e.year),
            label: String(e.year),
          }))}
        />
        <Select
          label="Estado documental"
          value={state}
          onChange={setState}
          options={[
            { value: "all", label: "Todos os estados" },
            { value: "lead_found", label: "Com pistas" },
            { value: "no_lead", label: "Sem pistas cadastradas" },
          ]}
        />
      </div>
      {competition !== "brasileirao" ? (
        <div className="empty-note" role="status">
          O calendário desta competição ainda não foi incorporado ao contrato
          público. Não é possível inferir suas edições ou resultados.
        </div>
      ) : (
        <div className="timeline-layout">
          <div>
            <div className="year-grid">
              {visible.map((edition) => (
                <button
                  key={edition.id}
                  className={`${edition.evidence_state} ${edition.year === selected.year ? "selected" : ""}`}
                  onClick={() => setParams({ ano: String(edition.year) })}
                  aria-pressed={edition.year === selected.year}
                  aria-label={`${edition.year}: ${edition.evidence_state !== "no_lead" ? "com pistas" : "sem pistas cadastradas"}`}
                >
                  <strong>{edition.year}</strong>
                  <span>
                    {edition.evidence_state !== "no_lead"
                      ? "Com pistas"
                      : "Sem pistas"}
                  </span>
                </button>
              ))}
            </div>
            {visible.length === 0 && (
              <p role="status">
                Nenhuma temporada corresponde a estes filtros.
              </p>
            )}
            <div className="timeline-legend">
              <span>
                <i />
                Com pistas
              </span>
              <span>
                <i />
                Sem pistas cadastradas
              </span>
            </div>
          </div>
          <section className="year-detail" aria-live="polite">
            <div className="year-display">{selected.year}</div>
            <StatusBadge
              kind={selected.evidence_state !== "no_lead" ? "green" : "neutral"}
            >
              {selected.evidence_state !== "no_lead"
                ? "Pistas aguardando revisão"
                : "Pesquisa pendente"}
            </StatusBadge>
            <h2>Campeonato Brasileiro</h2>
            <code>{selected.id}</code>
            <p>
              Campeão e demais resultados:{" "}
              <strong>dados ainda não homologados.</strong>
            </p>
            {selected.year === 1987 && (
              <p className="convention">
                1987: Flamengo campeão por convenção metodológica explícita do
                IGFB, sem alegação de consenso institucional ou jurídico. A
                convenção não substitui a homologação documental.
              </p>
            )}
            <SourcesList data={data} ids={selected.source_ids} />
          </section>
        </div>
      )}
    </>
  );
}
