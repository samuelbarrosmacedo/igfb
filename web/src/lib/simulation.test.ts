import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { simulate, consistency, standardize, logistic } from "./simulation";
const weights = JSON.parse(
  readFileSync("public/data/methodology.json", "utf8"),
).weights;
describe("Laboratório sintético", () => {
  it("calcula exemplo explícito sem IDs reais", () => {
    const rows = simulate(weights);
    expect(rows.find((r) => r.id === "sintetico-aurora")?.score).toBe(1674);
    expect(rows.every((r) => r.id.startsWith("sintetico-"))).toBe(true);
  });
  it("restaurar usa pesos exportados sem mutação", () => {
    const original = JSON.stringify(weights);
    const custom = structuredClone(weights);
    custom.libertadores.champion = 0;
    expect(simulate(custom)).not.toEqual(simulate(weights));
    expect(JSON.stringify(weights)).toBe(original);
  });
  it("preserva empate exato por competição", () => {
    const zero = Object.fromEntries(
      Object.entries(weights).map(([key, value]) => [
        key,
        Object.fromEntries(
          Object.keys(value as object).map((outcome) => [outcome, 0]),
        ),
      ]),
    );
    expect(simulate(zero).map((r) => r.position)).toEqual([1, 1, 1]);
  });
  it("trata valores extremos e séries inválidas", () => {
    expect(consistency([10, 10, 10, 10, 10])).toBe(1);
    expect(consistency([0, 0])).toBe(0);
    expect(consistency([10, 0, 0, 0, 0])).toBe(0.2);
    expect(() => consistency([-1])).toThrow();
    expect(standardize([1, 1])).toEqual([0, 0]);
    expect(logistic(1000)).toBe(100);
    expect(logistic(-1000)).toBe(0);
    expect(() => logistic(Infinity)).toThrow();
  });
});
