import { mkdirSync, writeFileSync } from "node:fs";
import { z } from "zod";
import { datasetSchemas, manifestSchema } from "../src/lib/contracts.ts";
mkdirSync("public/schemas", { recursive: true });
for (const [name, schema] of Object.entries({
  "manifest.json": manifestSchema,
  ...datasetSchemas,
}))
  writeFileSync(
    `public/schemas/${name}`,
    JSON.stringify(z.toJSONSchema(schema), null, 2) + "\n",
  );
console.log("10 JSON Schemas gerados da fonte Zod.");
