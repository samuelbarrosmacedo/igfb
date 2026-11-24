import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Search } from "lucide-react";
import {
  PageHeading,
  ClubMark,
  StatusBadge,
  EmptyMetrics,
  SourcesList,
} from "../components/Shared";
import type { PublicData } from "../lib/contracts";
export function Clubs({ data }: { data: PublicData }) {
  const [search, setSearch] = useState("");
  const normalize = (text: string) =>
    text
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  const clubs = data["clubs.json"].clubs.filter((c) =>
    normalize(c.name).includes(normalize(search)),
  );
  return (
    <>
      <PageHeading
        eyebrow="EXPLORADOR DE CLUBES"
        title="Cada camisa, uma história."
        description="Explore as identidades já presentes na pesquisa e os documentos associados a cada trajetória."
      />
      <div className="toolbar">
        <label className="search">
          <Search size={20} />
          <input
            aria-label="Buscar clube"
            placeholder="Encontre um clube"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <span className="muted" aria-live="polite">
          {clubs.length} identidades encontradas
        </span>
      </div>
      <div className="club-grid">
        {clubs.map((club) => (
          <Link className="club-tile" to={`/clubes/${club.id}`} key={club.id}>
            <div className="club-tile-top">
              <ClubMark name={club.name} />
              <StatusBadge>Em pesquisa</StatusBadge>
            </div>
            <h2>{club.name}</h2>
            <p>
              {club.lead_count} {club.lead_count === 1 ? "pista" : "pistas"} ·{" "}
              {club.source_ids.length}{" "}
              {club.source_ids.length === 1 ? "fonte" : "fontes"}
            </p>
            <div className="club-tile-bottom">
              Explorar o dossiê <span>+</span>
            </div>
          </Link>
        ))}
      </div>
      {clubs.length === 0 && (
        <p className="empty-note">
          Nenhuma identidade encontrada para esta busca.
        </p>
      )}
      <p className="section-note">
        {data["clubs.json"].scope_note} Os nomes são identificações
        tipográficas; escudos só serão incluídos com procedência e autorização
        adequadas.
      </p>
    </>
  );
}
export function ClubProfile({ data }: { data: PublicData }) {
  const { id } = useParams();
  const club = data["clubs.json"].clubs.find((c) => c.id === id);
  if (!club)
    return (
      <>
        <PageHeading
          eyebrow="EXPLORADOR"
          title="Identidade não encontrada."
          description="Este clube ainda não consta nas identidades disponíveis."
        />
        <Link to="/clubes" className="button secondary">
          Voltar aos clubes
        </Link>
      </>
    );
  return (
    <>
      <Link to="/clubes" className="breadcrumb">
        Clubes / Dossiê
      </Link>
      <div className="club-profile-heading">
        <ClubMark name={club.name} large />
        <PageHeading
          eyebrow="DOSSIÊ DOCUMENTAL"
          title={club.name}
          description="Uma trajetória em pesquisa. As pistas abaixo ainda precisam de homologação."
        />
      </div>
      <div className="profile-meta">
        <code>{club.id}</code>
        <StatusBadge kind="gold">Identidade presente nas pistas</StatusBadge>
        <Link className="text-link" to={`/comparador?club=${club.id}`}>
          Comparar cobertura documental
        </Link>
      </div>
      <EmptyMetrics />
      <section className="section">
        <div className="section-heading">
          <h2>Temporadas com pistas</h2>
          <span>{club.years_with_leads.length} no cadastro atual</span>
        </div>
        <div className="year-tags">
          {club.years_with_leads.map((year) => (
            <Link key={year} to={`/linha-do-tempo?ano=${year}`}>
              {year}
            </Link>
          ))}
        </div>
        <p className="section-note">
          As datas indicam afirmações encontradas em fontes, não uma lista de
          conquistas homologadas.
        </p>
      </section>
      <section className="section">
        <h2>O caminho até as fontes</h2>
        <SourcesList data={data} ids={club.source_ids} />
      </section>
    </>
  );
}
