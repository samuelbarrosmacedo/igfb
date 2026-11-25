import { useState } from "react";
import type { IdentityAsset } from "../lib/observatory-contract";
import * as Dialog from "@radix-ui/react-dialog";
import { ExternalLink, FileText, X, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import type { PublicData, Source } from "../lib/contracts";
export function PageHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <header className="page-heading">
      <div className="eyebrow">
        <span />
        {eyebrow}
      </div>
      <h1 tabIndex={-1}>{title}</h1>
      <p>{description}</p>
    </header>
  );
}
export function StatusBadge({
  children,
  kind = "neutral",
}: {
  children: React.ReactNode;
  kind?: "gold" | "green" | "neutral";
}) {
  return <span className={`badge ${kind}`}>{children}</span>;
}
export function EmptyMetrics() {
  return (
    <div className="metrics-unavailable">
      <ShieldCheck size={26} />
      <div>
        <h3>Dados ainda não homologados</h3>
        <p>
          Conquistas, participações, rebaixamentos e pontuação aguardam
          validação documental. Ausência de dados não significa ausência de
          história.
        </p>
      </div>
    </div>
  );
}
const sourceStates: Record<Source["state"], string> = {
  unverified_lead: "Pista ainda não conferida",
  page_checked_not_archived: "Conferência declarada; bytes não arquivados",
  partially_archived: "Parte das edições com arquivo verificado",
  archived_pending_review: "Bytes verificados; revisão histórica pendente",
};
export function SourceCard({ source }: { source: Source }) {
  return (
    <article className="source-row">
      <div>
        <span className="eyebrow">
          {source.publisher} · {sourceStates[source.state]}
        </span>
        <h3>{source.id}</h3>
        <p>{source.note}</p>
        <div className="source-years">{source.years.join(" · ")}</div>
      </div>
      <Dialog.Root>
        <Dialog.Trigger className="button secondary small">
          <FileText size={16} />
          Ver registro
        </Dialog.Trigger>
        <Dialog.Portal>
          <Dialog.Overlay className="dialog-overlay" />
          <Dialog.Content className="dialog-content">
            <Dialog.Title className="dialog-title">
              Registro documental
            </Dialog.Title>
            <Dialog.Description>
              Esta referência é uma pista. Não constitui um resultado
              homologado.
            </Dialog.Description>
            <code>{source.id}</code>
            <p>{source.note}</p>
            <dl>
              <dt>Estado da evidência</dt>
              <dd>{sourceStates[source.state]}</dd>
              <dt>Conferência registrada</dt>
              <dd>{source.checked_on || "Não registrada"}</dd>
              <dt>SHA-256 dos bytes</dt>
              <dd>
                {source.archives.length
                  ? source.archives.map((archive) => (
                      <div key={archive.evidence_id}>
                        <span>
                          {archive.year} · {archive.evidence_id}
                        </span>
                        <br />
                        <code>{archive.sha256}</code>
                      </div>
                    ))
                  : "Ainda não arquivado no catálogo de evidências"}
              </dd>
              <dt>Resultado homologado</dt>
              <dd>Não</dd>
            </dl>
            <a
              className="button primary"
              href={source.url}
              target="_blank"
              rel="noreferrer"
            >
              Abrir fonte original <ExternalLink size={16} />
            </a>
            <Dialog.Close
              className="icon-button dialog-close"
              aria-label="Fechar registro"
            >
              <X />
            </Dialog.Close>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </article>
  );
}
export function SourcesList({
  data,
  ids,
}: {
  data: PublicData;
  ids: string[];
}) {
  const sources = data["sources.json"].sources.filter((source) =>
    ids.includes(source.id),
  );
  return sources.length ? (
    <div>
      {sources.map((source) => (
        <SourceCard key={source.id} source={source} />
      ))}
    </div>
  ) : (
    <div className="empty-note">
      <FileText />
      <p>
        Nenhuma pista cadastrada para este recorte. Isso não indica que a
        competição deixou de acontecer.
      </p>
      <Link to="/pesquisa" className="text-link">
        Acompanhar a pesquisa
      </Link>
    </div>
  );
}
export function ClubMark({
  name,
  crest = null,
  large = false,
}: {
  name: string;
  crest?: IdentityAsset | null;
  large?: boolean;
}) {
  const [failed, setFailed] = useState<string | null>(null);
  return (
    <div
      aria-hidden="true"
      className={`club-mark ${large ? "large" : ""} ${crest && failed !== crest.path ? "with-crest" : ""}`}
    >
      {crest && failed !== crest.path ? (
        <img
          src={import.meta.env.BASE_URL + crest.path}
          alt=""
          width={large ? 112 : 64}
          height={large ? 112 : 64}
          loading="lazy"
          onError={() => setFailed(crest.path)}
        />
      ) : (
        name.slice(0, 3).toLocaleUpperCase("pt-BR")
      )}
    </div>
  );
}
