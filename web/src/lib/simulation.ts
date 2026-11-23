export type Weights = Record<string, Record<string, number>>;
// Exemplos inventados e isolados. Nenhum ID de clube real ou fato histórico.
export const syntheticTeams = [
  {
    id: "sintetico-aurora",
    name: "Equipe Aurora",
    counts: {
      libertadores: { champion: 2 },
      brasileirao: { champion: 1, runner_up: 1 },
      serie_a_participation: { participated: 8 },
      relegation_a_b: { relegated: 1 },
    },
  },
  {
    id: "sintetico-horizonte",
    name: "Equipe Horizonte",
    counts: {
      libertadores: { champion: 0 },
      brasileirao: { champion: 3, runner_up: 2 },
      serie_a_participation: { participated: 12 },
      relegation_a_b: { relegated: 0 },
    },
  },
  {
    id: "sintetico-vertice",
    name: "Equipe Vértice",
    counts: {
      libertadores: { champion: 1 },
      brasileirao: { champion: 1, runner_up: 0 },
      serie_a_participation: { participated: 6 },
      relegation_a_b: { relegated: 0 },
    },
  },
] as const;
export function simulate(weights: Weights) {
  const rows = syntheticTeams
    .map((team) => {
      const contributions = Object.entries(team.counts).map(
        ([criterion, outcomes]) => ({
          criterion,
          value: Object.entries(outcomes).reduce((sum, [outcome, count]) => {
            const weight = weights[criterion]?.[outcome];
            if (!Number.isFinite(weight))
              throw Error("Peso ausente ou inválido");
            return sum + Number(count) * weight;
          }, 0),
        }),
      );
      return {
        id: team.id,
        name: team.name,
        score: contributions.reduce((sum, item) => sum + item.value, 0),
        contributions,
        position: 0,
      };
    })
    .sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
  rows.forEach(
    (row, i) =>
      (row.position =
        i > 0 && row.score === rows[i - 1].score
          ? rows[i - 1].position
          : i + 1),
  );
  return rows;
}
export function consistency(values: number[]) {
  if (!values.length || values.some((v) => !Number.isFinite(v) || v < 0))
    throw Error("Série inválida");
  const sum = values.reduce((a, b) => a + b, 0);
  const denominator = values.length * values.reduce((a, b) => a + b * b, 0);
  return denominator ? (sum * sum) / denominator : 0;
}
export function logistic(z: number) {
  if (!Number.isFinite(z)) throw Error("Entrada inválida");
  return z >= 0
    ? 100 / (1 + Math.exp(-z))
    : (100 * Math.exp(z)) / (1 + Math.exp(z));
}
export function standardize(values: number[]) {
  if (!values.length || values.some((v) => !Number.isFinite(v)))
    throw Error("Série inválida");
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance =
    values.reduce((a, b) => a + (b - mean) ** 2, 0) / values.length;
  return values.map((v) => (variance ? (v - mean) / Math.sqrt(variance) : 0));
}
