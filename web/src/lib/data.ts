import { useQuery } from "@tanstack/react-query";
import {
  datasetSchemas,
  manifestSchema,
  validateRelations,
  type Manifest,
  type PublicData,
} from "./contracts";
const base = import.meta.env.BASE_URL + "data/";
async function getText(path: string, signal?: AbortSignal) {
  const response = await fetch(base + path, { signal, cache: "no-cache" });
  if (!response.ok)
    throw new Error(`Não foi possível carregar os dados (${response.status}).`);
  return response.text();
}
export async function fetchManifest(signal?: AbortSignal) {
  return manifestSchema.parse(
    JSON.parse(await getText("manifest.json", signal)),
  );
}
export async function fetchData(
  manifest: Manifest,
  signal?: AbortSignal,
): Promise<PublicData> {
  const entries = await Promise.all(
    manifest.files.map(async (name) => {
      const entry = manifest.datasets[name];
      if (entry.path !== `snapshots/${manifest.dataset_id}/${name}`)
        throw Error("Referência de snapshot inválida.");
      const text = await getText(entry.path, signal);
      const bytes = await crypto.subtle.digest(
        "SHA-256",
        new TextEncoder().encode(text),
      );
      const hash = Array.from(new Uint8Array(bytes), (b) =>
        b.toString(16).padStart(2, "0"),
      ).join("");
      if (hash !== entry.sha256)
        throw Error("A integridade dos dados não pôde ser confirmada.");
      return [name, datasetSchemas[name].parse(JSON.parse(text))];
    }),
  );
  return validateRelations({
    manifest,
    ...Object.fromEntries(entries),
  } as PublicData);
}
export function usePublicData() {
  return useQuery({
    queryKey: ["public-data"],
    queryFn: async ({ signal }) =>
      fetchData(await fetchManifest(signal), signal),
    staleTime: Infinity,
    retry: 1,
  });
}
export function useLatestManifest() {
  return useQuery({
    queryKey: ["latest-manifest"],
    queryFn: ({ signal }) => fetchManifest(signal),
    refetchInterval: 300_000,
    staleTime: 60_000,
    retry: 1,
  });
}
export const dateLabel = (value: string) =>
  new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
    timeZone: "America/Sao_Paulo",
  }).format(new Date(value));
