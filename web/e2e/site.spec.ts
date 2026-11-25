import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const exportedSeason = JSON.parse(
  readFileSync("public/data/observatory.json", "utf8"),
).current_season;
const convention = JSON.parse(
  readFileSync("public/data/methodology.json", "utf8"),
).flamengo_1987;
import AxeBuilder from "@axe-core/playwright";
test("home, rotas, integridade visual e acessibilidade", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("./");
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "GRANDEZA",
  );
  await page.screenshot({
    path: test.info().outputPath("home.png"),
    fullPage: true,
  });
  if (await page.getByRole("button", { name: "Abrir menu" }).isVisible()) {
    await page.getByRole("button", { name: "Abrir menu" }).click();
    const menu = page.getByRole("dialog", { name: "Explore o IGFB" });
    await expect(menu).toBeVisible();
    await menu.getByRole("link", { name: "Clubes", exact: true }).click();
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(
      "Cada camisa, uma história.",
    );
    await expect(menu).toHaveCount(0);
  }
  for (const [route, heading] of [
    ["/temporada", `O futebol em ${exportedSeason}.`],
    ["/competicoes", "Cada disputa tem seu lugar."],
    ["/ranking", "A posição vem depois da prova."],
    ["/clubes", "Cada camisa, uma história."],
    ["/comparador", "Compare o que sabemos."],
    ["/linha-do-tempo", "O tempo também joga."],
    ["/pesquisa", "Transparência em campo."],
    ["/metodologia", "O método precisa jogar aberto."],
    ["/laboratorio", "Mude o peso. Questione o resultado."],
  ]) {
    await page.goto(`./#${route}`);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(heading);
    await page.screenshot({
      path: test.info().outputPath(route.slice(1) + ".png"),
      fullPage: true,
    });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
    const axe = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    expect(axe.violations).toEqual([]);
  }
  expect(errors).toEqual([]);
});
test("clubes, comparação e filtros do almanaque", async ({ page }) => {
  await page.goto("./#/clubes");
  await page.getByRole("textbox", { name: "Buscar clube" }).fill("gremio");
  await page
    .getByRole("link")
    .filter({ has: page.getByRole("heading", { name: "Grêmio", exact: true }) })
    .click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Grêmio");
  await expect(
    page.getByText("Dados ainda não homologados", { exact: true }),
  ).toBeVisible();
  await page.goto("./#/comparador");
  await expect(page.getByRole("table")).toBeVisible();
  await expect(page.getByText("Modo: pesquisa documental")).toBeVisible();
  await page.goto("./#/linha-do-tempo?ano=1987");
  await expect(
    page.getByText(convention, { exact: true }).first(),
  ).toBeVisible();
  await page.getByRole("combobox", { name: "Competição" }).click();
  await page.getByRole("option", { name: "Libertadores", exact: true }).click();
  await expect(page.getByRole("status")).toContainText(
    "ainda não foi incorporado",
  );
});
test("simulação separada, restauração e teclado", async ({ page }) => {
  await page.goto("./#/laboratorio");
  await page.getByRole("button", { name: "Iniciar simulação" }).click();
  const slider = page.getByRole("slider", { name: "Libertadores · Título" });
  await slider.focus();
  await slider.press("Home");
  await expect(slider).toHaveAttribute("aria-valuenow", "0");
  await page
    .getByRole("button", { name: "Guardar cenário nesta sessão" })
    .click();
  await expect(
    page.getByRole("status", { name: "Cenário guardado" }),
  ).toContainText("Cenário guardado");
  await page.getByRole("button", { name: "Restaurar pesos do modelo" }).click();
  await expect(slider).toHaveAttribute("aria-valuenow", "700");
  await expect(page.getByText("Modo: pesquisa documental")).toHaveCount(0);
  await expect(
    page.getByRole("img", { name: /Contribuições por critério/ }),
  ).toBeVisible();
  await page.screenshot({
    path: test.info().outputPath("laboratorio-ativo.png"),
    fullPage: true,
  });
  const axe = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(axe.violations).toEqual([]);
});
test("erros de rede são visíveis e não fabricam dados", async ({ page }) => {
  await page.route("**/data/manifest.json", (route) =>
    route.fulfill({ status: 503, body: "Unavailable" }),
  );
  await page.goto("./");
  await expect(page.getByRole("alert")).toContainText(
    "O arquivo não carregou",
    { timeout: 15000 },
  );
  await expect(
    page.getByRole("button", { name: "Tentar novamente" }),
  ).toBeVisible();
});
