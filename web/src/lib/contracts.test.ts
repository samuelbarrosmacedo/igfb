import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import {
  datasetSchemas,
  manifestSchema,
  rankingSchema,
  validateRelations,
  type PublicData,
} from "./contracts";
function fixture() {
  const read = (name: string) =>
    JSON.parse(readFileSync(`public/data/${name}`, "utf8"));
  return {
    manifest: manifestSchema.parse(read("manifest.json")),
    ...Object.fromEntries(
      Object.entries(datasetSchemas).map(([name, schema]) => [
        name,
        schema.parse(read(name)),
      ]),
    ),
  } as PublicData;
}
describe("Contrato público", () => {
  it("valida o snapshot exportado pelo Python", () =>
    expect(validateRelations(fixture())).toBeTruthy());
  it("bloqueia um ranking disfarçado em dados de pesquisa", () => {
    const data = fixture()["ranking.json"];
    expect(() =>
      rankingSchema.parse({
        ...data,
        ranking: [{ club: "flamengo", score: 999 }],
      }),
    ).toThrow();
    expect(() =>
      rankingSchema.parse({ ...data, publication_authorized: true }),
    ).toThrow();
  });
  it("rejeita métricas ausentes convertidas em zero", () => {
    const data = fixture()["clubs.json"];
    data.clubs[0].titles = 0 as never;
    expect(() => datasetSchemas["clubs.json"].parse(data)).toThrow();
  });
  it("rejeita fonte não cadastrada", () => {
    const data = fixture();
    data["clubs.json"].clubs[0].source_ids.push("inventada");
    expect(() => validateRelations(data)).toThrow();
  });
  it("rejeita mistura de snapshots", () => {
    const data = fixture();
    data.manifest.datasets["clubs.json"].path =
      "snapshots/" + "0".repeat(64) + "/clubs.json";
    expect(() => validateRelations(data)).toThrow();
  });
  it("rejeita ano fora do recorte", () => {
    const data = fixture()["editions.json"];
    data.editions[0].year = 1970;
    expect(() => datasetSchemas["editions.json"].parse(data)).toThrow();
  });
  it("rejeita anos sem pistas incorretos mesmo com a contagem certa", () => {
    const data = fixture();
    data["coverage.json"].seasons_without_leads[0] = data[
      "editions.json"
    ].editions.find((e) => e.evidence_state !== "no_lead")!.year;
    expect(() => validateRelations(data)).toThrow();
  });
  it("rejeita avanço de pesquisa sem evidências correspondentes", () => {
    const data = fixture();
    data["coverage.json"].verified_archives += 1;
    expect(() => validateRelations(data)).toThrow();
  });
  it("rejeita contagens inconsistentes", () => {
    const data = fixture();
    data["coverage.json"].source_leads += 1;
    expect(() => validateRelations(data)).toThrow();
  });
});
