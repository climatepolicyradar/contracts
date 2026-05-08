#!/usr/bin/env python3
"""Generate dbt schema.yml files from registered contracts for Snowflake consumers.

One file is written per contract (e.g. dbt/documents.yml). Consuming dbt projects
drop the file into their `models/published/` directory — dbt merges every *.yml
automatically, no include directive needed.
"""

import sys
import types
from datetime import date, datetime
from pathlib import Path
from typing import Any, Union, get_args, get_origin

import yaml
from pydantic import BaseModel
from pydantic.fields import FieldInfo

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from cpr_contracts.registry import CONTRACTS  # noqa: E402

OUT_DIR = ROOT / "dbt"


def pydantic_type_to_dbt(annotation: Any) -> str:
    origin = get_origin(annotation)

    if origin is Union or origin is types.UnionType:
        non_none = [a for a in get_args(annotation) if a is not type(None)]
        if len(non_none) == 1:
            return pydantic_type_to_dbt(non_none[0])
        return "VARIANT"

    if origin is list:
        return "ARRAY"
    if origin is dict:
        return "OBJECT"
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return "OBJECT"

    if annotation is str:
        return "STRING"
    if annotation is int:
        return "NUMBER"
    if annotation is float:
        return "FLOAT"
    if annotation is bool:
        return "BOOLEAN"
    if annotation is datetime:
        return "TIMESTAMP"
    if annotation is date:
        return "DATE"

    return "VARIANT"


def build_column(name: str, field: FieldInfo) -> dict[str, Any]:
    col: dict[str, Any] = {"name": name}
    if field.description:
        col["description"] = field.description
    col["data_type"] = pydantic_type_to_dbt(field.annotation)
    if field.is_required():
        col["data_tests"] = ["not_null"]
    return col


def build_model_yaml(model_cls: type[BaseModel], dbt_name: str) -> dict[str, Any]:
    description = (model_cls.__doc__ or "").strip() or f"Canonical {model_cls.__name__}"
    columns = [
        build_column(name, field) for name, field in model_cls.model_fields.items()
    ]
    return {"name": dbt_name, "description": description, "columns": columns}


class _IndentDumper(yaml.SafeDumper):
    """Indent sequence items under their parent key — matches the dbt convention."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow=flow, indentless=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for contract in CONTRACTS:
        models_yaml = [
            build_model_yaml(model_cls, f"{model_cls.__name__.lower()}_v{version}")
            for model_cls, version in contract.dbt_tables
        ]
        body = {"version": 2, "models": models_yaml}
        path = OUT_DIR / f"{contract.name}.yml"
        path.write_text(
            yaml.dump(
                body,
                Dumper=_IndentDumper,
                sort_keys=False,
                default_flow_style=False,
                width=100,
            )
        )
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
