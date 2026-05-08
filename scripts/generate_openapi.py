#!/usr/bin/env python3
"""Emit an OpenAPI 3.1 doc that wraps all registered contracts.

OpenAPI 3.1 components/schemas accept JSON Schema 2020-12 unchanged, so this
single artifact serves both downstream consumers:

  - quicktype (TypeScript type generation)
  - oasdiff (breaking-change detection in CI)

The contract is versioned by git tag, not by `info.version` — we set the
field to a static placeholder to satisfy the OpenAPI spec.
"""

import sys
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic.json_schema import JsonSchemaMode, models_json_schema

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from cpr_contracts.registry import CONTRACTS  # noqa: E402

OUT = ROOT / "schemas" / "openapi.yaml"


class _IndentDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow=flow, indentless=False)


def main() -> None:
    all_models: list[tuple[type[BaseModel], JsonSchemaMode]] = [
        (model, "validation")
        for contract in CONTRACTS
        for model in contract.schema_models
    ]
    _, defs = models_json_schema(all_models, ref_template="#/components/schemas/{model}")
    openapi = {
        "openapi": "3.1.0",
        "info": {
            "title": "cpr-contracts",
            "version": "0.0.0",
            "description": "Canonical models for Climate Policy Radar. Versioned by git tag, not info.version.",
        },
        "paths": {},
        "components": {"schemas": defs["$defs"]},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        yaml.dump(
            openapi,
            Dumper=_IndentDumper,
            sort_keys=False,
            default_flow_style=False,
            width=100,
        )
    )
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
