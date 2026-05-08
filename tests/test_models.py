from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic.json_schema import JsonSchemaMode, models_json_schema

from cpr_contracts import Document, Label
from cpr_contracts.registry import CONTRACTS

ROOT = Path(__file__).parent.parent


def test_label_roundtrip():
    l = Label(id="l1", name="Energy", type="sector")
    assert Label.model_validate(l.model_dump()) == l


def test_document_roundtrip():
    doc = Document(
        id="doc1",
        title="UK Climate Change Act 2008",
        labels=[Label(id="l1", name="Energy", type="sector")],
    )
    assert Document.model_validate(doc.model_dump()) == doc


def test_document_optional_fields():
    doc = Document(id="doc1", title="Minimal")
    assert doc.source_url is None
    assert doc.labels == []
    assert doc.metadata == {}


def test_openapi_in_sync():
    """The committed openapi.yaml must match what Pydantic generates."""
    committed = yaml.safe_load((ROOT / "schemas" / "openapi.yaml").read_text())
    all_models: list[tuple[type[BaseModel], JsonSchemaMode]] = [
        (model, "validation")
        for contract in CONTRACTS
        for model in contract.schema_models
    ]
    _, defs = models_json_schema(all_models, ref_template="#/components/schemas/{model}")
    assert committed["components"]["schemas"] == defs["$defs"], (
        "schemas/openapi.yaml is out of sync. Run 'just generate' to update."
    )
