from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class Contract:
    """A named group of related models forming one contract domain.

    Adding a new contract:
      1. Define models in models.py
      2. Add a Contract entry here
      3. Export the new models in __init__.py
    """

    name: str  # drives dbt filename, e.g. "documents" → dbt/documents.yml
    schema_models: list[type[BaseModel]]  # all types included in the OpenAPI schema
    dbt_tables: list[tuple[type[BaseModel], int]]  # (model, version) for dbt table output


from cpr_contracts.models import Document, Label  # noqa: E402

CONTRACTS: list[Contract] = [
    Contract(
        name="documents",
        schema_models=[Document, Label],
        dbt_tables=[(Document, 1)],
    ),
]
