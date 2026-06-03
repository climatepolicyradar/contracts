from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LabelLabelRelationship(BaseModel):
    type: str
    value: LabelWithoutLabelRelationships
    timestamp: datetime | None = None

class BaseLabel(BaseModel):
    id: str
    type: str
    value: str
    attributes: dict[str, str | float | bool] = {}

class Label(BaseLabel):
    labels: list[LabelLabelRelationship]

class LabelWithoutLabelRelationships(BaseLabel):
    pass


class Item(BaseModel):
    url: str | None = None
    type: str
    content_type: str | None = None

class DocumentRelationship(BaseModel):
    type: str
    value: DocumentWithoutDocumentRelationships
    timestamp: datetime | None = None

class BaseDocument(BaseModel):
    id: str
    title: str
    description: str | None = None
    items: list[Item] = []
    attributes: dict[str, str | float | bool] = {}

class DocumentLabelRelationship(BaseModel):
    type: str
    value: Label
    timestamp: datetime | None = None

class Document(BaseDocument):
    labels: list[DocumentLabelRelationship]
    documents: list[DocumentRelationship]

class DocumentWithoutDocumentRelationships(BaseDocument):
    labels: list[DocumentLabelRelationship] = []


# As `LabelRelationship`` and `DocumentRelationship`` reference classes
# defined later than they are used, `model_rebuild()` resolves those forward
# references now that all classes exist.
# > "Annotations that fail to resolve are kept as strings for later rebuilding."
# @see: https://pydantic.dev/docs/validation/latest/internals/resolving_annotations/
LabelLabelRelationship.model_rebuild()
DocumentRelationship.model_rebuild()
