import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { Ranking } from "./Ranking";
import type { PublicData } from "../lib/contracts";
it("mostra o bloqueio público sem criar uma tabela histórica", () => {
  const data = {
    "ranking.json": JSON.parse(
      readFileSync("public/data/ranking.json", "utf8"),
    ),
    "coverage.json": JSON.parse(
      readFileSync("public/data/coverage.json", "utf8"),
    ),
  } as PublicData;
  render(
    <MemoryRouter>
      <Ranking data={data} />
    </MemoryRouter>,
  );
  expect(screen.getByText("Publicação bloqueada")).toBeInTheDocument();
  expect(screen.queryByRole("table")).not.toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: "Abrir laboratório" }),
  ).toHaveAttribute("href", "/laboratorio");
});
