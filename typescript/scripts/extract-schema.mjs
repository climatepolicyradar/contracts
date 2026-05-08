// Pull `components.schemas` out of the OpenAPI doc and emit a JSON Schema
// bundle that quicktype can read. Top-level is `Document`; every other
// schema becomes a `$defs` entry. Refs are rewritten from
// `#/components/schemas/X` → `#/$defs/X`.
//
// Usage: piped into quicktype via the npm `generate` script.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import yaml from "js-yaml";

const here = dirname(fileURLToPath(import.meta.url));
const openapiPath = resolve(here, "../../schemas/openapi.yaml");
const openapi = yaml.load(readFileSync(openapiPath, "utf8"));
const schemas = openapi.components.schemas;

const rewriteRefs = (obj) => {
  if (Array.isArray(obj)) return obj.map(rewriteRefs);
  if (obj && typeof obj === "object") {
    return Object.fromEntries(
      Object.entries(obj).map(([k, v]) =>
        k === "$ref" && typeof v === "string"
          ? [k, v.replace("#/components/schemas/", "#/$defs/")]
          : [k, rewriteRefs(v)],
      ),
    );
  }
  return obj;
};

const bundle = rewriteRefs({
  $schema: "https://json-schema.org/draft/2020-12/schema",
  ...schemas.Document,
  $defs: schemas,
});

process.stdout.write(JSON.stringify(bundle, null, 2));
