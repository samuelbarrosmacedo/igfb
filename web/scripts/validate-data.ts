import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import {
  datasetSchemas,
  manifestSchema,
  validateRelations,
  type PublicData,
} from "../src/lib/contracts.ts";
const manifest = manifestSchema.parse(
  JSON.parse(readFileSync("public/data/manifest.json", "utf8")),
);
const data: Record<string, unknown> = { manifest };
for (const name of manifest.files) {
  const entry = manifest.datasets[name];
  const raw = readFileSync(`public/data/${entry.path}`);
  if (createHash("sha256").update(raw).digest("hex") !== entry.sha256)
    throw Error(`Hash divergente: ${name}`);
  data[name] = datasetSchemas[name].parse(JSON.parse(raw.toString()));
}
validateRelations(data as PublicData);
console.log(
  `Contrato v${manifest.schema_version}: 8 datasets válidos, integridade e relações conferidas.`,
);
