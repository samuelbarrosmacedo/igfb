import { mkdirSync, writeFileSync } from "node:fs";
import { z } from "zod";
import { datasetSchemas, manifestSchema } from "../src/lib/contracts.ts";
import { catalogInputSchema } from "../src/lib/observatory-contract.ts";
mkdirSync("public/schemas", { recursive: true });
for (const [name, schema] of Object.entries({
  "catalog-input.json": catalogInputSchema,
  "manifest.json": manifestSchema,
  ...datasetSchemas,
}))
  writeFileSync(
    `public/schemas/${name}`,
    JSON.stringify(z.toJSONSchema(schema), null, 2) + "\n",
  );
console.log("JSON Schemas gerados da fonte Zod.");
