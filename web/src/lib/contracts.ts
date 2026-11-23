import { z } from "zod";
const version = z.literal(2);
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
  files: z.array(z.enum(fileNames)).length(8),
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
  archived_evidence_documents: z.null(),
  archive_status: z.literal("no_evidence_catalog"),
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
export const clubSchema = z.object({
  id: z.string(),
  name: z.string(),
  identity_status: z.literal("source_lead_identity"),
  crest: z.null(),
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
  status: z.literal("identities_from_source_leads"),
  scope_note: z.string(),
  clubs: z.array(clubSchema),
});
export const editionSchema = z.object({
  id: z.string(),
  year,
  competition: z.literal("brasileirao"),
  evidence_state: z.enum(["lead_found", "no_lead"]),
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
  state: z.enum(["page_checked_not_archived", "unverified_lead"]),
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
export const datasetSchemas = {
  "project-status.json": statusSchema,
  "coverage.json": coverageSchema,
  "methodology.json": methodologySchema,
  "review-queue.json": queueSchema,
  "ranking.json": rankingSchema,
  "clubs.json": clubsSchema,
  "editions.json": editionsSchema,
  "sources.json": sourcesSchema,
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
  if (new Set(manifest.files).size !== 8)
    throw new Error("Manifesto contém duplicidades");
  for (const file of manifest.files) {
    const entry = manifest.datasets[file];
    if (entry.path !== `snapshots/${manifest.dataset_id}/${file}`)
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
  const withLeads = editions.filter((e) => e.evidence_state === "lead_found");
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
        e.source_ids.length > 0 !== (e.evidence_state === "lead_found"),
    )
  )
    throw new Error("Edição inconsistente");
  return data;
}
