import { z } from "zod";
import {
  identitySchema,
  observatorySchema,
  validateObservatory,
} from "./observatory-contract";
const version = z.literal(3);
const nonnegative = z.number().int().nonnegative();
const year = z.number().int().min(1971).max(2025);
const hash = z.string().regex(/^[a-f0-9]{64}$/);
const https = z
  .string()
  .url()
  .regex(/^https:\/\//);
export const scopeSchema = z.object({
  first_year: z.literal(1971),
  last_year: z.literal(2025),
  seasons: z.literal(55),
  excluded_pre_1971: z.literal(true),
});
const fileNames = [
  "project-status.json",
  "coverage.json",
  "methodology.json",
  "review-queue.json",
  "ranking.json",
  "clubs.json",
  "editions.json",
  "sources.json",
  "research-backlog.json",
  "observatory.json",
] as const;
export const manifestSchema = z.object({
  schema_version: version,
  dataset_status: z.literal("research_in_progress"),
  approved_results: z.literal(0),
  source_commit: z.string().regex(/^[a-f0-9]{40}$/),
  generated_at: z.iso.datetime({ offset: true }),
  data_published_at: z.null(),
  dataset_id: hash,
  scope: scopeSchema,
  audit_status: z.literal("research_state_checked_results_not_homologated"),
  files: z.array(z.enum(fileNames)).length(fileNames.length),
  sha256: z.record(z.enum(fileNames), hash),
  datasets: z.record(
    z.enum(fileNames),
    z.object({
      path: z.string().regex(/^snapshots\/[a-f0-9]{64}\/[a-z-]+\.json$/),
      sha256: hash,
      availability: z.enum(["available", "withheld"]),
    }),
  ),
});
const statusSchema = z.object({
  schema_version: version,
  stage: z.literal("research_in_progress"),
  progress: z.object({
    percent: nonnegative.max(100),
    audited: z.literal(false),
    usable_as_completion_metric: z.literal(false),
  }),
  measured_progress: z.object({
    metric: z.literal("seasons_with_documentary_leads"),
    numerator: nonnegative,
    denominator: z.literal(55),
    percent: z.number().min(0).max(100),
    audited_completion: z.literal(false),
    warning: z.string(),
  }),
  approved_results: z.literal(0),
  scope: scopeSchema,
  audit_status: z.string(),
  last_collection_at: z.string().nullable(),
  ranking_publication: z.literal("blocked"),
  publication_reason: z.string(),
});
const coverageSchema = z.object({
  schema_version: version,
  source_leads: nonnegative,
  seasons_with_leads: nonnegative.max(55),
  seasons_without_leads: z.array(year),
  checked_source_pages: nonnegative,
  source_ids_without_archived_bytes: nonnegative,
  approved_results: z.literal(0),
  catalogued_sources: nonnegative,
  archived_evidence_documents: nonnegative,
  verified_archives: nonnegative,
  archived_candidate_count: nonnegative,
  distinct_source_urls: nonnegative,
  lead_coverage_percent: z.number().min(0).max(100),
  coverage_metric: z.string(),
  archive_status: z.literal("inventory_verified"),
  review_editions: nonnegative,
  competing_claim_editions: z.array(year),
  denominator: z.string(),
});
export const methodologySchema = z.object({
  schema_version: version,
  weights_status: z.literal("experimental"),
  weights: z.record(z.string(), z.record(z.string(), z.number().finite())),
  scope: scopeSchema,
  exclusions: z.array(z.string()),
  flamengo_1987: z.string(),
  competition_labels: z.record(z.string(), z.string()),
  outcome_labels: z.record(z.string(), z.string()),
  documents: z.array(
    z.object({
      path: z.string(),
      url: https,
      sha256: hash,
      markdown: z.string(),
    }),
  ),
});
const claimSchema = z.object({
  club_id: z.string(),
  source_ids: z.array(z.string()),
  source_count: nonnegative,
});
const queueSchema = z.object({
  schema_version: version,
  status: z.literal("manual_review_required"),
  items: z.array(
    z.object({
      year,
      edition_id: z.string(),
      claims: z.array(claimSchema),
      has_competing_claims: z.boolean(),
      status: z.literal("manual_review_required"),
      approved: z.literal(false),
    }),
  ),
});
export const rankingSchema = z.object({
  schema_version: version,
  status: z.literal("unavailable_pending_homologation"),
  approved_results: z.literal(0),
  publication_authorized: z.literal(false),
  ranking: z.array(z.never()).length(0),
  reason: z.string(),
});
export const clubSchema = identitySchema.extend({
  identity_status: z.literal("catalogued"),
  lead_count: nonnegative,
  source_ids: z.array(z.string()),
  years_with_leads: z.array(year),
  titles: z.null(),
  score: z.null(),
  participations: z.null(),
  relegations: z.null(),
});
const clubsSchema = z.object({
  schema_version: version,
  status: z.literal("canonical_catalog"),
  scope_note: z.string(),
  clubs: z.array(clubSchema),
});
export const editionSchema = z.object({
  id: z.string(),
  year,
  competition: z.literal("brasileirao"),
  evidence_state: z.enum(["lead_found", "no_lead", "archived_pending_review"]),
  source_ids: z.array(z.string()),
  has_competing_claims: z.boolean(),
  approved_results: z.literal(0),
  champion: z.null(),
});
const editionsSchema = z.object({
  schema_version: version,
  status: z.literal("calendar_with_research_states"),
  competition: z.literal("brasileirao"),
  editions: z.array(editionSchema).length(55),
});
export const sourceSchema = z.object({
  id: z.string(),
  url: https,
  publisher: z.string(),
  note: z.string(),
  checked_on: z.string().nullable(),
  state: z.enum([
    "page_checked_not_archived",
    "unverified_lead",
    "partially_archived",
    "archived_pending_review",
  ]),
  archives: z.array(
    z.object({
      evidence_id: z.string(),
      year,
      sha256: hash,
      retrieved_at: z.iso.datetime({ offset: true }),
    }),
  ),
  archived_sha256: z.null(),
  approved: z.literal(false),
  club_ids: z.array(z.string()),
  years: z.array(year),
});
const sourcesSchema = z.object({
  schema_version: version,
  status: z.literal("source_leads_not_homologated"),
  sources: z.array(sourceSchema),
});
const backlogSchema = z.object({
  schema_version: version,
  scope: z.object({ first_year: z.literal(1971), last_year: z.literal(2025) }),
  total_seasons: z.literal(55),
  seasons_without_leads: nonnegative,
  seasons_with_leads: nonnegative,
  lead_coverage_percent: z.number().min(0).max(100),
  ranking_approved: z.literal(false),
  warning: z.string(),
  tasks: z
    .array(
      z.object({
        year,
        edition_id: z.string(),
        priority: z.number().int().min(1).max(3),
        stage: z.enum([
          "discover_official_source",
          "archive_and_verify_source",
          "manual_historical_review",
        ]),
        candidate_count: nonnegative,
        source_ids: z.array(z.string()),
        checked_source_count: nonnegative,
        archived_source_count: nonnegative,
        approved: z.literal(false),
      }),
    )
    .length(55),
});
export const datasetSchemas = {
  "observatory.json": observatorySchema,
  "project-status.json": statusSchema,
  "coverage.json": coverageSchema,
  "methodology.json": methodologySchema,
  "review-queue.json": queueSchema,
  "ranking.json": rankingSchema,
  "clubs.json": clubsSchema,
  "editions.json": editionsSchema,
  "sources.json": sourcesSchema,
  "research-backlog.json": backlogSchema,
};
export type FileName = keyof typeof datasetSchemas;
export type Manifest = z.infer<typeof manifestSchema>;
export type Club = z.infer<typeof clubSchema>;
export type Source = z.infer<typeof sourceSchema>;
export type Methodology = z.infer<typeof methodologySchema>;
export type PublicData = { manifest: Manifest } & {
  [K in FileName]: z.infer<(typeof datasetSchemas)[K]>;
};
export function validateRelations(data: PublicData) {
  const { manifest } = data;
  validateObservatory(
    data["observatory.json"],
    Object.keys(data["methodology.json"].weights),
  );
  if (
    JSON.stringify(data["observatory.json"].clubs.map((c) => c.id).sort()) !==
    JSON.stringify(data["clubs.json"].clubs.map((c) => c.id).sort())
  )
    throw Error("Catálogos de clubes divergentes");
  if (new Set(manifest.files).size !== fileNames.length)
    throw new Error("Manifesto contém duplicidades");
  for (const file of manifest.files) {
    const entry = manifest.datasets[file];
    if (
      entry.path !== `snapshots/${manifest.dataset_id}/${file}` ||
      entry.sha256 !== manifest.sha256[file]
    )
      throw new Error("Snapshot inconsistente");
  }
  const editions = data["editions.json"].editions;
  if (new Set(editions.map((e) => e.year)).size !== 55)
    throw new Error("Calendário incompleto");
  const sources = new Set(data["sources.json"].sources.map((s) => s.id));
  if (sources.size !== data["sources.json"].sources.length)
    throw new Error("Fonte duplicada");
  const clubs = data["clubs.json"].clubs;
  const clubIds = new Set(clubs.map((c) => c.id));
  if (clubIds.size !== clubs.length) throw new Error("Clube duplicado");
  for (const row of [...clubs, ...editions])
    if (row.source_ids.some((id) => !sources.has(id)))
      throw new Error("Fonte não cadastrada");
  for (const source of data["sources.json"].sources)
    if (source.club_ids.some((id) => !clubIds.has(id)))
      throw new Error("Clube não cadastrado");
  const coverage = data["coverage.json"];
  const withLeads = editions.filter((e) => e.evidence_state !== "no_lead");
  if (
    withLeads.length !== coverage.seasons_with_leads ||
    new Set(coverage.seasons_without_leads).size + withLeads.length !== 55
  )
    throw new Error("Cobertura inconsistente");
  if (
    coverage.source_leads !== clubs.reduce((s, c) => s + c.lead_count, 0) ||
    coverage.catalogued_sources !== sources.size
  )
    throw new Error("Contagens inconsistentes");
  if (
    editions.some(
      (e) =>
        e.id !== `brasileirao:${e.year}` ||
        e.source_ids.length > 0 !== (e.evidence_state !== "no_lead"),
    )
  )
    throw new Error("Edição inconsistente");
  const missing = editions
    .filter((e) => e.evidence_state === "no_lead")
    .map((e) => e.year)
    .sort();
  if (
    JSON.stringify([...coverage.seasons_without_leads].sort()) !==
    JSON.stringify(missing)
  )
    throw Error("Anos sem pistas inconsistentes");
  const measured = data["project-status.json"].measured_progress;
  const expected = Math.round((withLeads.length / 55) * 10000) / 100;
  if (
    coverage.lead_coverage_percent !== expected ||
    measured.percent !== expected ||
    measured.numerator !== withLeads.length
  )
    throw Error("Indicador medido inconsistente");
  const backlog = data["research-backlog.json"];
  if (
    new Set(backlog.tasks.map((t) => t.year)).size !== 55 ||
    backlog.seasons_with_leads !== withLeads.length ||
    backlog.lead_coverage_percent !== expected
  )
    throw Error("Fila de pesquisa inconsistente");
  for (const task of backlog.tasks) {
    if (
      task.edition_id !== `brasileirao:${task.year}` ||
      task.source_ids.some((id) => !sources.has(id))
    )
      throw Error("Referência de tarefa inválida");
  }
  for (const item of data["review-queue.json"].items) {
    if (item.edition_id !== `brasileirao:${item.year}`)
      throw Error("Revisão inconsistente");
    for (const claim of item.claims) {
      if (
        !clubIds.has(claim.club_id) ||
        claim.source_ids.some((id) => !sources.has(id)) ||
        claim.source_count !== new Set(claim.source_ids).size
      )
        throw Error("Afirmação sem referência");
    }
  }
  if (
    coverage.distinct_source_urls !==
      new Set(data["sources.json"].sources.map((s) => s.url)).size ||
    coverage.verified_archives !==
      data["sources.json"].sources.reduce((n, s) => n + s.archives.length, 0)
  )
    throw Error("Inventário inconsistente");
  return data;
}
