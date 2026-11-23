import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  PageHeading,
  ClubMark,
  EmptyMetrics,
  StatusBadge,
} from "../components/Shared";
import { DataTable } from "../components/ui/DataTable";
import type { PublicData } from "../lib/contracts";
export function Compare({ data }: { data: PublicData }) {
  const [params] = useSearchParams();
  const clubs = data["clubs.json"].clubs;
  const initial = clubs.some((c) => c.id === params.get("club"))
    ? [
        params.get("club")!,
        ...clubs
          .filter((c) => c.id !== params.get("club"))
          .slice(0, 1)
          .map((c) => c.id),
      ]
    : clubs.slice(0, 2).map((c) => c.id);
  const [selected, setSelected] = useState(initial);
  const chosen = clubs.filter((c) => selected.includes(c.id));
  return (
    <>
      <PageHeading
        eyebrow="COMPARADOR DE CLUBES"
        title="Compare o que sabemos."
        description="Neste estágio, a comparação mostra a cobertura documental. Mais pistas não significam mais títulos ou maior grandeza."
      />
      <StatusBadge kind="gold">Modo: pesquisa documental</StatusBadge>
      <fieldset className="club-picker">
        <legend>Selecione de 2 a 4 clubes</legend>
        {clubs.map((club) => (
          <label
            key={club.id}
            className={selected.includes(club.id) ? "selected" : ""}
          >
            <input
              type="checkbox"
              checked={selected.includes(club.id)}
              disabled={!selected.includes(club.id) && selected.length === 4}
              onChange={() =>
                setSelected((current) =>
                  current.includes(club.id)
                    ? current.filter((id) => id !== club.id)
                    : [...current, club.id],
                )
              }
            />
            {club.name}
          </label>
        ))}
      </fieldset>
      {chosen.length < 2 ? (
        <div className="empty-note" role="status">
          Selecione ao menos dois clubes para comparar.
        </div>
      ) : (
        <>
          <div
            className="versus-grid"
            style={{ "--club-count": chosen.length } as React.CSSProperties}
          >
            {chosen.map((club) => (
              <div key={club.id}>
                <ClubMark name={club.name} large />
                <h2>{club.name}</h2>
                <Link to={`/clubes/${club.id}`} className="text-link">
                  Abrir dossiê
                </Link>
              </div>
            ))}
          </div>
          <DataTable
            caption="Comparação de cobertura documental — não é uma classificação esportiva"
            data={[
              { metric: "Pistas cadastradas", key: "lead_count" },
              { metric: "Fontes distintas", key: "source_ids" },
              { metric: "Temporadas com pistas", key: "years_with_leads" },
              {
                metric: "Títulos, pontuação e participações",
                key: "unavailable",
              },
            ]}
            columns={[
              {
                accessorKey: "metric",
                header: "Indicador",
                enableSorting: false,
              },
              ...chosen.map((club) => ({
                id: club.id,
                header: club.name,
                enableSorting: false,
                cell: ({ row }: any) => {
                  const key = row.original.key;
                  return key === "unavailable"
                    ? "Não homologados"
                    : key === "lead_count"
                      ? club.lead_count
                      : key === "source_ids"
                        ? club.source_ids.length
                        : club.years_with_leads.length;
                },
              })),
            ]}
          />
          <EmptyMetrics />
          <div className="section-banner">
            <div>
              <h3>Da comparação à simulação</h3>
              <p>
                Teste o efeito dos pesos em equipes fictícias no laboratório.
              </p>
            </div>
            <Link className="button secondary" to="/laboratorio">
              Experimentar pesos
            </Link>
          </div>
        </>
      )}
    </>
  );
}
