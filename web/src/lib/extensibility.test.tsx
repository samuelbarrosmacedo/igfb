import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { fireEvent, render, screen, cleanup } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import {
  catalogInputSchema,
  observatorySchema,
  validateObservatory,
} from "./observatory-contract";
import { datasetSchemas, manifestSchema, type PublicData } from "./contracts";
import {
  Competitions,
  CompetitionProfile,
  Season,
} from "../features/Competitions";
import { Timeline } from "../features/Timeline";
import { Clubs } from "../features/Clubs";
import { ClubMark } from "../components/Shared";
function fixture(): PublicData {
  const read = (n: string) =>
    JSON.parse(readFileSync(`public/data/${n}`, "utf8"));
  return {
    manifest: manifestSchema.parse(read("manifest.json")),
    ...Object.fromEntries(
      Object.entries(datasetSchemas).map(([n, s]) => [n, s.parse(read(n))]),
    ),
  } as PublicData;
}
const mount = (el: React.ReactNode, path = "/") => {
  cleanup();
  return render(<MemoryRouter initialEntries={[path]}>{el}</MemoryRouter>);
};
describe("Extensibilidade do catálogo sem componentes específicos", () => {
  it("valida o arquivo canônico e rejeita contrato incompatível", () => {
    const c = JSON.parse(readFileSync("../config/observatory.json", "utf8"));
    expect(catalogInputSchema.parse(c)).toBeTruthy();
    expect(() =>
      catalogInputSchema.parse({ ...c, schema_version: 2 }),
    ).toThrow();
  });
  it("preserva a convenção vigente de 1987 apenas no Brasileirão", () => {
    const d = fixture();
    mount(<Timeline data={d} />, "/linha-do-tempo?competicao=brasileirao&ano=1987");
    expect(screen.getByRole("heading", { name: "Vencedores provisórios · aguardando revisão" })).toBeTruthy();
    expect(screen.getAllByText(d["methodology.json"].flamengo_1987).length).toBeGreaterThan(0);
    expect(d["methodology.json"].flamengo_1987).toContain("Flamengo* e Sport*");
    d["observatory.json"].editions.push({ ...d["observatory.json"].editions[0], id: "carioca:1987", competition_id: "carioca", year: 1987, label: "1987" });
    mount(<Timeline data={d} />, "/linha-do-tempo?competicao=carioca&ano=1987");
    expect(screen.queryByText(d["methodology.json"].flamengo_1987)).toBeNull();
    expect(d["ranking.json"].ranking).toEqual([]);
  });
  it("novo clube aparece sem pistas de campeões", () => {
    const d = fixture();
    d["clubs.json"].clubs.push({
      ...d["clubs.json"].clubs[0],
      id: "fixture",
      name: "Clube Sintético Novo",
      crest: null,
      lead_count: 0,
      source_ids: [],
      years_with_leads: [],
    });
    mount(<Clubs data={d} />);
    expect(
      screen.getByRole("heading", { name: "Clube Sintético Novo" }),
    ).toBeTruthy();
  });
  it("nova competição e edição geram páginas reutilizáveis", () => {
    const d = fixture();
    const o = d["observatory.json"];
    o.competitions.push({
      ...o.competitions[0],
      id: "fixture",
      name: "Competição Sintética",
    });
    o.editions.push({
      ...o.editions[0],
      id: "fixture:2027",
      competition_id: "fixture",
      year: 2027,
      label: "2027",
    });
    o.seasons.push(2027);
    validateObservatory(o, Object.keys(d["methodology.json"].weights));
    mount(<Competitions data={d} />);
    expect(
      screen.getByRole("heading", { name: "Competição Sintética" }),
    ).toBeTruthy();
    mount(
      <Routes>
        <Route
          path="/competicoes/:id"
          element={<CompetitionProfile data={d} />}
        />
      </Routes>,
      "/competicoes/fixture",
    );
    expect(screen.getByRole("link", { name: /2027/ })).toBeTruthy();
  });
  it("virada 2026 para 2027 mantém histórico separado", () => {
    const d = fixture();
    d["observatory.json"].current_season = 2027;
    d["observatory.json"].seasons.push(2027);
    mount(<Season data={d} />);
    expect(
      screen.getByRole("heading", { name: "O futebol em 2027." }),
    ).toBeTruthy();
    expect(
      screen.getByText("Fora do recorte histórico de cálculo"),
    ).toBeTruthy();
    expect(d["methodology.json"].scope.last_year).toBe(2025);
  });
  it("escudo ausente, indisponível e atualização não quebram identidade", () => {
    const asset = fixture()["clubs.json"].clubs.find((c) => c.crest)!.crest!;
    cleanup();
    const { rerender } = render(<ClubMark name="Clube" crest={asset} />);
    const img = document.querySelector("img")!;
    fireEvent.error(img);
    expect(screen.getByText("CLU")).toBeTruthy();
    rerender(
      <ClubMark
        name="Clube"
        crest={{ ...asset, path: "assets/identities/novo.svg" }}
      />,
    );
    expect(document.querySelector("img")?.getAttribute("src")).toContain(
      "novo.svg",
    );
    rerender(<ClubMark name="Clube" />);
    expect(screen.getByText("CLU")).toBeTruthy();
  });
  it("dados incompletos preservam null e não aceitam homologação editorial", () => {
    const d = fixture()["observatory.json"];
    expect(
      observatorySchema.parse(d).clubs.some((c) => c.official_name === null),
    ).toBe(true);
    const edition = d.editions[0];
    d.records.push({
      id: "fixture",
      edition_id: edition.id,
      kind: "result",
      status: "homologated" as never,
      club_ids: [d.clubs[0].id],
      source_ids: edition.source_ids,
      label: "Fixture",
      phase: null,
      position: null,
      value: null,
      unit: null,
      home_score: null,
      away_score: null,
      played_at: null,
      updated_at: "2026-11-25T00:00:00Z",
      revision: 1,
      revision_note: "Teste",
    });
    expect(() => observatorySchema.parse(d)).toThrow();
  });
});
