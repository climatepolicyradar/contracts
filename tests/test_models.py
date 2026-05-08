from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic.json_schema import JsonSchemaMode, models_json_schema

from cpr_contracts import Document, Label, LabelRelationship, LabelWithoutLabelRelationships
from cpr_contracts.registry import CONTRACTS

ROOT = Path(__file__).parent.parent


def test_label_roundtrip():
    label = Label(value="Energy", attributes={}, labels=[])
    assert Label.model_validate(label.model_dump()) == label


def test_document_roundtrip():
    rel = LabelRelationship(type="sector", value=LabelWithoutLabelRelationships(value="Energy"))
    doc = Document(id="doc1", title="UK Climate Change Act 2008", labels=[rel], documents=[])
    assert Document.model_validate(doc.model_dump()) == doc


def test_document_optional_fields():
    rel = LabelRelationship(type="sector", value=LabelWithoutLabelRelationships(value="Energy"))
    doc = Document(id="doc1", title="Minimal", labels=[rel], documents=[])
    assert doc.description is None
    assert doc.items == []
    assert doc.attributes == {}


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
