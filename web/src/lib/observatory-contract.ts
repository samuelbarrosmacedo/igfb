import { z } from "zod";
const id = z.string().regex(/^[a-z0-9][a-z0-9_:-]*$/);
const text = z.string().min(1);
const year = z.number().int().min(1971).max(9999);
const https = z.url().regex(/^https:\/\//);
export const assetSchema = z
  .object({
    path: z.string().regex(/^assets\/identities\/[a-z0-9_-]+\.(svg|png|webp)$/),
    sha256: z.string().regex(/^[a-f0-9]{64}$/),
    source_url: https,
    license: text,
    attribution: text,
    usage_note: text,
  })
  .strict();
const identity = {
  id,
  name: text,
  crest: assetSchema.nullable(),
  colors: z.array(z.string().regex(/^#[0-9a-fA-F]{6}$/)),
  identity_source_ids: z.array(id),
};
export const identitySchema = z
  .object({
    ...identity,
    official_name: text.nullable(),
    abbreviation: text.nullable(),
    state: text.nullable(),
    city: text.nullable(),
  })
  .strict();
export const competitionSchema = z
  .object({
    ...identity,
    scoring_category: text.nullable(),
    jurisdiction: z.enum(["national", "state", "continental", "world"]),
    state: text.nullable(),
    organizer: text.nullable(),
    format: z.enum(["league", "cup", "mixed", "unknown"]),
    periodicity: z.enum([
      "annual",
      "irregular",
      "discontinued",
      "not_documented",
    ]),
    status: z.enum(["catalogued", "active", "discontinued"]),
    eligibility_note: text,
  })
  .strict();
export const sportingEditionSchema = z
  .object({
    id,
    competition_id: id,
    year,
    label: text,
    status: z.enum([
      "research",
      "scheduled",
      "ongoing",
      "finished",
      "cancelled",
    ]),
    format: z.enum(["league", "cup", "mixed", "unknown"]),
    participant_ids: z.array(id),
    source_ids: z.array(id),
    updated_at: z.iso.datetime({ offset: true }).nullable(),
  })
  .strict();
export const sportingRecordSchema = z
  .object({
    id,
    edition_id: id,
    kind: z.enum(["result", "match", "standing", "statistic"]),
    status: z.enum([
      "collected",
      "in_review",
      "disputed",
      "provisional",
      "official_final",
    ]),
    club_ids: z.array(id).min(1),
    source_ids: z.array(id).min(1),
    label: text,
    phase: text.nullable(),
    position: z.number().int().positive().nullable(),
    value: z.number().finite().nullable(),
    unit: text.nullable(),
    home_score: z.number().int().nonnegative().nullable(),
    away_score: z.number().int().nonnegative().nullable(),
    played_at: z.iso.datetime({ offset: true }).nullable(),
    updated_at: z.iso.datetime({ offset: true }),
    revision: z.number().int().positive(),
    revision_note: text,
  })
  .strict();
export const catalogSourceSchema = z
  .object({
    id,
    url: https,
    publisher: text,
    note: text,
    checked_on: z.iso.date().nullable(),
  })
  .strict();
export const catalogShape = {
  clubs: z.array(identitySchema),
  competitions: z.array(competitionSchema),
  editions: z.array(sportingEditionSchema),
  sources: z.array(catalogSourceSchema),
  records: z.array(sportingRecordSchema),
};
export const catalogInputSchema = z
  .object({ schema_version: z.literal(1), ...catalogShape })
  .strict();
export const observatorySchema = z
  .object({
    schema_version: z.literal(3),
    ...catalogShape,
    current_season: year,
    historical_scope: z.object({ first_year: year, last_year: year }),
    seasons: z.array(year),
    collection_mode: z.literal("repository_records_only"),
  })
  .strict();
export type Observatory = z.infer<typeof observatorySchema>;
export type SportingEdition = z.infer<typeof sportingEditionSchema>;
export type SportingRecord = z.infer<typeof sportingRecordSchema>;
export type IdentityAsset = z.infer<typeof assetSchema>;
export function validateObservatory(d: Observatory, categories: string[]) {
  const unique = (rows: { id: string }[]) => {
    const ids = new Set(rows.map((r) => r.id));
    if (ids.size !== rows.length) throw Error("ID duplicado no observatório");
    return ids;
  };
  const clubs = unique(d.clubs),
    comps = unique(d.competitions),
    editions = unique(d.editions),
    sources = unique(d.sources);
  unique(d.records);
  const refs = (ids: string[], set: Set<string>) => {
    if (ids.some((i) => !set.has(i)))
      throw Error("Referência ausente no observatório");
  };
  for (const i of [...d.clubs, ...d.competitions])
    refs(i.identity_source_ids, sources);
  for (const c of d.competitions) {
    if (
      ["taca_brasil", "robertao", "1937"].includes(c.id) ||
      (c.scoring_category !== null && !categories.includes(c.scoring_category))
    )
      throw Error("Competição inelegível");
    if (c.jurisdiction === "state" && (!c.state || !c.organizer))
      throw Error("Estadual sem jurisdição");
  }
  for (const e of d.editions) {
    refs([e.competition_id], comps);
    refs(e.participant_ids, clubs);
    refs(e.source_ids, sources);
    if (e.status !== "research" && !e.source_ids.length)
      throw Error("Estado esportivo sem fonte");
  }
  for (const r of d.records) {
    refs([r.edition_id], editions);
    refs(r.club_ids, clubs);
    refs(r.source_ids, sources);
    if (
      r.status === "official_final" &&
      d.editions.find((e) => e.id === r.edition_id)?.status !== "finished"
    )
      throw Error("Final sem encerramento");
  }
  if (
    !d.seasons.includes(d.current_season) ||
    d.editions.some((e) => !d.seasons.includes(e.year))
  )
    throw Error("Temporada ausente");
}
