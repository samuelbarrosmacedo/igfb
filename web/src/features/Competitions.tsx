import { useState } from "react";
import { ArrowUpRight } from "lucide-react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import {
  PageHeading,
  ClubMark,
  StatusBadge,
  SourcesList,
} from "../components/Shared";
import { Select } from "../components/ui/Select";
import { DataTable } from "../components/ui/DataTable";
import { dateLabel } from "../lib/data";
import type { PublicData } from "../lib/contracts";
import type {
  SportingRecord,
  SportingEdition,
} from "../lib/observatory-contract";
export const sportStates = {
  collected: "Coletado",
  in_review: "Em revisão",
  disputed: "Contestado",
  provisional: "Provisório",
  official_final: "Resultado oficial · não homologado IGFB",
};
export const editionStates = {
  research: "Em pesquisa",
  scheduled: "Programada",
  ongoing: "Em andamento",
  finished: "Encerrada",
  cancelled: "Cancelada",
};
export function allEditions(data: PublicData): SportingEdition[] {
  const extra = data["observatory.json"].editions;
  return [
    ...data["editions.json"].editions
      .filter((e) => !extra.some((x) => x.id === e.id))
      .map((e) => ({
        id: e.id,
        competition_id: e.competition,
        year: e.year,
        label: String(e.year),
        status: "research" as const,
        format: "unknown" as const,
        participant_ids: [],
        source_ids: [],
        updated_at: null,
      })),
    ...extra,
  ].sort((a, b) => b.year - a.year || a.id.localeCompare(b.id));
}
export function CatalogSources({
  data,
  ids,
}: {
  data: PublicData;
  ids: string[];
}) {
  return (
    <div className="catalog-sources">
      {data["observatory.json"].sources
        .filter((s) => ids.includes(s.id))
        .map((s) => (
          <p key={s.id}>
            <a href={s.url} target="_blank" rel="noreferrer">
              {s.publisher} <ArrowUpRight aria-hidden="true" size={14} style={{ display: "inline-block", verticalAlign: "middle" }} />
            </a>{" "}
            · {s.note}
            {s.checked_on && <small> Consulta: {s.checked_on}</small>}
          </p>
        ))}
    </div>
  );
}
export function RecordList({
  data,
  records,
}: {
  data: PublicData;
  records: SportingRecord[];
}) {
  const [kind, setKind] = useState("all");
  if (!records.length)
    return (
      <p className="empty-note">
        Resultados, partidas, classificações e estatísticas ainda não foram
        cadastrados neste recorte. Ausência de dados não significa resultado
        zero.
      </p>
    );
  const labels = {
    result: "Resultados e campanhas",
    match: "Partidas",
    standing: "Classificações",
    statistic: "Estatísticas",
  };
  return (
    <>
      <p className="section-note">
        Informações esportivas em pesquisa. Nenhum destes registros alimenta o
        ranking homologado.
      </p>
      <Select
        label="Tipo de informação"
        value={kind}
        onChange={setKind}
        options={[
          { value: "all", label: "Todas as informações" },
          ...Object.entries(labels)
            .filter(([k]) => records.some((r) => r.kind === k))
            .map(([value, label]) => ({ value, label })),
        ]}
      />
      <DataTable
        caption="Registros esportivos e sua procedência — separados da pontuação IGFB"
        data={records.filter((r) => kind === "all" || r.kind === kind)}
        columns={[
          {
            accessorKey: "label",
            header: "Registro",
            cell: ({ row }) => (
              <>
                <strong>{row.original.label}</strong>
                <small>{row.original.phase}</small>
              </>
            ),
          },
          {
            id: "clubs",
            header: "Clubes",
            cell: ({ row }) => (
              <div className="record-clubs">
                {row.original.club_ids.map((id) => {
                  const c = data["clubs.json"].clubs.find((c) => c.id === id)!;
                  return (
                    <Link key={id} to={`/clubes/${id}`}>
                      <ClubMark name={c.name} crest={c.crest} />
                      {c.name}
                    </Link>
                  );
                })}
              </div>
            ),
          },
          {
            id: "value",
            header: "Dado registrado",
            cell: ({ row: { original: r } }) => (
              <>
                {r.position !== null && <span>{r.position}º · </span>}
                {r.kind === "match"
                  ? r.home_score === null || r.away_score === null
                    ? "Placar não disponível"
                    : `${r.home_score} × ${r.away_score}`
                  : r.value === null
                    ? r.kind === "result"
                      ? "Resultado registrado sem pontuação homologada"
                      : "Sem valor numérico"
                    : `${r.value} ${r.unit ?? ""}`}
                {r.played_at && <small>{dateLabel(r.played_at)}</small>}
              </>
            ),
          },
          {
            accessorKey: "status",
            header: "Estado e fonte",
            cell: ({ row: { original: r } }) => (
              <>
                <StatusBadge kind="gold">{sportStates[r.status]}</StatusBadge>
                <CatalogSources data={data} ids={r.source_ids} />
                <small>
                  Atualizado: {dateLabel(r.updated_at)} · revisão {r.revision}:{" "}
                  {r.revision_note}
                </small>
              </>
            ),
          },
        ]}
      />
    </>
  );
}
export function CandidateClaims({
  data,
  editionId,
  clubId,
}: {
  data: PublicData;
  editionId?: string;
  clubId?: string;
}) {
  const items = data["review-queue.json"].items
    .filter((i) => !editionId || i.edition_id === editionId)
    .flatMap((i) =>
      i.claims
        .filter((c) => !clubId || c.club_id === clubId)
        .map((c) => ({ ...c, year: i.year, edition_id: i.edition_id })),
    );
  if (!items.length) return null;
  return (
    <section className="section">
      <h2>Afirmações candidatas nas fontes</h2>
      <p>
        O cadastro abaixo registra pistas de título. Não constitui uma lista de
        títulos homologados. Afirmações conflitantes permanecem visíveis para
        revisão.
      </p>
      <div className="claim-list">
        {items.map((item) => {
          const c = data["clubs.json"].clubs.find(
            (c) => c.id === item.club_id,
          )!;
          return (
            <article
              className="source-row"
              key={`${item.edition_id}:${item.club_id}`}
            >
              <div>
                <span className="eyebrow">{item.year} · Em revisão</span>
                <h3>
                  <Link to={`/clubes/${c.id}`}>{c.name}</Link>
                </h3>
                <p>
                  Afirmação candidata: campeão. {item.source_count}{" "}
                  referência(s), sem homologação.
                </p>
                {item.year === 1987 && (
                  <p className="convention">
                    {data["methodology.json"].flamengo_1987}
                  </p>
                )}
                <SourcesList data={data} ids={item.source_ids} />
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
export function EditionLinks({
  data,
  editions,
}: {
  data: PublicData;
  editions: SportingEdition[];
}) {
  if (!editions.length)
    return (
      <p className="empty-note" role="status">
        Nenhuma edição cadastrada neste recorte. O calendário ainda não foi
        incorporado; não é possível inferir resultados.
      </p>
    );
  return (
    <div className="edition-list">
      {editions.map((e) => (
        <Link
          key={e.id}
          to={`/competicoes/${e.competition_id}/edicoes/${encodeURIComponent(e.id)}`}
        >
          <div>
            <span className="eyebrow">
              {e.year} · {editionStates[e.status]}
            </span>
            <h3>
              {
                data["observatory.json"].competitions.find(
                  (c) => c.id === e.competition_id,
                )?.name
              }
            </h3>
            <span>{e.label}</span>
          </div>
          <ArrowUpRight aria-hidden="true" size={18} />
        </Link>
      ))}
    </div>
  );
}
export function Competitions({ data }: { data: PublicData }) {
  const [search, setSearch] = useState("");
  const [jurisdiction, setJurisdiction] = useState("all");
  const catalog = data["observatory.json"];
  const editions = allEditions(data);
  return (
    <>
      <PageHeading
        eyebrow="CATÁLOGO DE COMPETIÇÕES"
        title="Cada disputa tem seu lugar."
        description="Competições têm identidades próprias. As edições preservam formatos, estados de pesquisa e fontes, sem confundir torneios com categorias de pontuação."
      />
      <div className="toolbar">
        <label className="search">
          <input
            aria-label="Buscar competição"
            placeholder="Encontre uma competição"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </label>
        <Select
          label="Abrangência"
          value={jurisdiction}
          onChange={setJurisdiction}
          options={[
            { value: "all", label: "Todas" },
            ...Array.from(
              new Set(catalog.competitions.map((c) => c.jurisdiction)),
            ).map((value) => ({
              value,
              label: {
                national: "Nacional",
                state: "Estadual",
                continental: "Continental",
                world: "Mundial",
              }[value],
            })),
          ]}
        />
      </div>
      <div className="edition-list">
        {catalog.competitions
          .filter(
            (c) =>
              (jurisdiction === "all" || jurisdiction === c.jurisdiction) &&
              c.name
                .toLocaleLowerCase("pt-BR")
                .includes(search.toLocaleLowerCase("pt-BR")),
          )
          .map((c) => (
            <Link key={c.id} to={`/competicoes/${c.id}`}>
              <ClubMark name={c.name} crest={c.crest} />
              <div>
                <h2>{c.name}</h2>
                <p>
                  {c.state ?? ""}{" "}
                  {editions.filter((e) => e.competition_id === c.id).length}{" "}
                  {editions.filter((e) => e.competition_id === c.id).length === 1 ? "edição cadastrada" : "edições cadastradas"}
                </p>
              </div>
              <ArrowUpRight aria-hidden="true" size={18} />
            </Link>
          ))}
      </div>
    </>
  );
}
export function CompetitionProfile({ data }: { data: PublicData }) {
  const { id, editionId } = useParams();
  const catalog = data["observatory.json"];
  const c = catalog.competitions.find((c) => c.id === id);
  const editions = allEditions(data).filter((e) => e.competition_id === id);
  const e = editions.find((e) => e.id === editionId);
  if (!c || (editionId && !e))
    return (
      <>
        <PageHeading
          eyebrow="ARQUIVO"
          title="Registro não encontrado."
          description="A identidade ou edição solicitada não está neste snapshot."
        />
        <Link to="/competicoes">Explorar competições</Link>
      </>
    );
  const historical =
    e && data["editions.json"].editions.find((x) => x.id === e.id);
  return (
    <>
      <Link
        className="breadcrumb"
        to={e ? `/competicoes/${c.id}` : "/competicoes"}
      >
        Competições / {c.name}
      </Link>
      <div className="club-profile-heading">
        <ClubMark name={c.name} crest={c.crest} large />
        <PageHeading
          eyebrow={
            e
              ? `${e.year} · ${editionStates[e.status]}`
              : "DOSSIÊ DA COMPETIÇÃO"
          }
          title={e ? `${c.name} · ${e.label}` : c.name}
          description={c.eligibility_note}
        />
      </div>
      <div className="profile-meta">
        <code>{e?.id ?? c.id}</code>
        {c.organizer && <span>{c.organizer}</span>}
        {c.state && <span>{c.state}</span>}
        {e?.updated_at && <span>Atualização: {dateLabel(e.updated_at)}</span>}
      </div>
      <CatalogSources data={data} ids={c.identity_source_ids} />
      {e ? (
        <>
          <section className="section">
            <h2>Participantes cadastrados</h2>
            {e.participant_ids.length ? (
              <div className="year-tags">
                {e.participant_ids.map((id) => (
                  <Link key={id} to={`/clubes/${id}`}>
                    {data["clubs.json"].clubs.find((c) => c.id === id)?.name}
                  </Link>
                ))}
              </div>
            ) : (
              <p className="empty-note">
                Lista de participantes ainda não disponível.
              </p>
            )}
          </section>
          <section className="section">
            <h2>O que está documentado</h2>
            <RecordList
              data={data}
              records={catalog.records.filter((r) => r.edition_id === e.id)}
            />
            <CatalogSources data={data} ids={e.source_ids} />
          </section>
          {historical && <CandidateClaims data={data} editionId={e.id} />}
        </>
      ) : (
        <section className="section">
          <h2>Edições do arquivo</h2>
          <EditionLinks data={data} editions={editions} />
        </section>
      )}
    </>
  );
}
export function Season({ data }: { data: PublicData }) {
  const [params, setParams] = useSearchParams();
  const catalog = data["observatory.json"];
  const year = Number(params.get("ano") || catalog.current_season);
  const editions = allEditions(data);
  const years = Array.from(
    new Set([catalog.current_season, ...editions.map((e) => e.year)]),
  ).sort((a, b) => b - a);
  return (
    <>
      <PageHeading
        eyebrow="TEMPORADA ATUAL E ARQUIVO"
        title={`O futebol em ${year}.`}
        description="Acompanhe as edições e os registros disponíveis. Resultados esportivos e homologação IGFB são etapas distintas."
      />
      <div className="toolbar">
        <Select
          label="Temporada"
          value={String(year)}
          onChange={(v) => setParams({ ano: v })}
          options={years.map((y) => ({ value: String(y), label: String(y) }))}
        />
        <StatusBadge kind="gold">
          {year > catalog.historical_scope.last_year
            ? "Fora do recorte histórico de cálculo"
            : "Recorte histórico · homologação pendente"}
        </StatusBadge>
      </div>
      <p className="section-note">
        Atualização por registros do repositório. Não há coleta automática de
        placares em tempo real.
      </p>
      <EditionLinks
        data={data}
        editions={editions.filter((e) => e.year === year)}
      />
      <div className="section-banner">
        <p>
          A virada do calendário não homologa resultados nem encerra
          competições. O estado de cada edição depende das fontes.
        </p>
        <Link to="/pesquisa" className="text-link">
          Acompanhar a pesquisa
        </Link>
      </div>
    </>
  );
}
