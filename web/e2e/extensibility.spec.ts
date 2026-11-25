import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import type { PublicData } from "../src/lib/contracts";
import type { SportingRecord } from "../src/lib/observatory-contract";
import AxeBuilder from "@axe-core/playwright";
function snapshot() {
  const manifest = JSON.parse(
    readFileSync("public/data/manifest.json", "utf8"),
  );
  const docs = Object.fromEntries(
    manifest.files.map((name: string) => [
      name,
      JSON.parse(readFileSync(`public/data/${name}`, "utf8")),
    ]),
  );
  return { manifest, ...docs } as PublicData;
}
function packageData(d: PublicData) {
  const hash = (s: string) => createHash("sha256").update(s).digest("hex");
  const docs = Object.fromEntries(
    d.manifest.files.map((name) => [name, JSON.stringify(d[name])]),
  );
  const dataset = hash(JSON.stringify(docs));
  const manifest = structuredClone({ ...d.manifest, dataset_id: dataset });
  for (const name of manifest.files) {
    manifest.sha256[name] = hash(docs[name]);
    manifest.datasets[name] = {
      ...manifest.datasets[name],
      path: `snapshots/${dataset}/${name}`,
      sha256: manifest.sha256[name],
    };
  }
  return { manifest, docs };
}
function extended() {
  const d = snapshot();
  const o = d["observatory.json"];
  o.current_season = 2027;
  o.seasons.push(2027);
  const club = {
    ...o.clubs[0],
    id: "fixture-club",
    name: "Clube de Teste Isolado",
    crest: null,
  };
  o.clubs.push(club);
  d["clubs.json"].clubs.push({
    ...club,
    identity_status: "catalogued",
    lead_count: 0,
    source_ids: [],
    years_with_leads: [],
    titles: null,
    score: null,
    participations: null,
    relegations: null,
  });
  const competition = {
    ...o.competitions.find((c) => c.id === "carioca")!,
    id: "fixture-state",
    name: "Estadual Sintético",
    state: "RJ",
  };
  o.competitions.push(competition);
  o.editions.push({
    ...o.editions[0],
    id: "fixture:2027",
    competition_id: competition.id,
    year: 2027,
    label: "2027",
    status: "ongoing",
    participant_ids: [club.id],
  });
  const record: SportingRecord = {
    id: "fixture-result",
    edition_id: "fixture:2027",
    kind: "statistic",
    status: "provisional",
    club_ids: [club.id],
    source_ids: o.editions[0].source_ids,
    label: "Dado sintético isolado",
    phase: null,
    position: null,
    value: null,
    unit: null,
    home_score: null,
    away_score: null,
    played_at: null,
    updated_at: "2027-01-01T00:00:00Z",
    revision: 1,
    revision_note: "Fixture de teste, nunca publicada",
  };
  o.records.push(record);
  return d;
}
test("novo clube, estadual, edição, 2027 e registros provisórios aparecem sem código específico", async ({
  page,
}) => {
  const d = extended();
  let pack = packageData(d);
  await page.route("**/data/**", (route) => {
    const name = new URL(route.request().url()).pathname.split("/").at(-1)!;
    return route.fulfill({
      contentType: "application/json",
      body:
        name === "manifest.json"
          ? JSON.stringify(pack.manifest)
          : pack.docs[name],
    });
  });
  await page.goto("./#/temporada");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "O futebol em 2027.",
  );
  await page.getByRole("link", { name: /Estadual Sintético/ }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Estadual Sintético · 2027",
  );
  await expect(page.getByText("Provisório", { exact: true })).toBeVisible();
  await expect(page.getByText("Sem valor numérico")).toBeVisible();
  await expect(
    page
      .getByRole("link", { name: "Clube de Teste Isolado", exact: true })
      .first(),
  ).toBeVisible();
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  d["observatory.json"].editions.find((e) => e.id === "fixture:2027")!.status =
    "finished";
  Object.assign(d["observatory.json"].records.find((r) => r.id === "fixture-result")!, {
    status: "official_final",
    revision: 2,
    revision_note: "Correção sintética",
    value: 7,
  });
  pack = packageData(d);
  await page.reload();
  await expect(
    page.getByText("Resultado oficial · não homologado IGFB", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/revisão 2: Correção sintética/)).toBeVisible();
  await page.goto("./#/ranking");
  await expect(page.getByText("Publicação bloqueada")).toBeVisible();
});
test("falha de dataset não exibe snapshot parcial e recuperação funciona", async ({
  page,
}) => {
  await page.route("**/data/snapshots/**/observatory.json", (route) =>
    route.fulfill({ status: 503, body: "Unavailable" }),
  );
  await page.goto("./#/temporada");
  await expect(page.getByRole("alert")).toContainText(
    "O arquivo não carregou",
    { timeout: 15000 },
  );
  await page.unroute("**/data/snapshots/**/observatory.json");
  await page.getByRole("button", { name: "Tentar novamente" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "O futebol em",
  );
});
test("escudos reais carregam e imagem indisponível mantém o nome", async ({
  page,
}) => {
  await page.goto("./#/clubes/flamengo");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Flamengo");
  const image = page.locator(".club-profile-heading img");
  await expect(image).toBeVisible();
  await expect
    .poll(() =>
      image.evaluate(
        (img: HTMLImageElement) => img.complete && img.naturalWidth > 0,
      ),
    )
    .toBe(true);
  await page.route("**/assets/identities/**", (route) => route.abort());
  await page.reload();
  await expect(page.locator(".club-profile-heading .club-mark")).toHaveText(
    "FLA",
  );
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Flamengo");
});
test("nova publicação oferece atualização atômica", async ({ page }) => {
  const initial = snapshot();
  initial["observatory.json"].current_season = 2026;
  initial["observatory.json"].seasons = [
    ...new Set([...initial["observatory.json"].seasons, 2026]),
  ];
  const first = packageData(initial);
  const second = packageData(extended());
  let latest = false;
  await page.route("**/data/**", (route) => {
    const name = new URL(route.request().url()).pathname.split("/").at(-1)!;
    const p = latest ? second : first;
    return route.fulfill({
      contentType: "application/json",
      body:
        name === "manifest.json" ? JSON.stringify(p.manifest) : p.docs[name],
    });
  });
  await page.clock.install();
  await page.goto("./#/temporada");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("2026");
  latest = true;
  await page.clock.fastForward(301000);
  await expect(
    page.getByText("Há uma nova publicação de dados disponível."),
  ).toBeVisible();
  await page.getByRole("button", { name: "Atualizar dados" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toContainText("2027");
});
