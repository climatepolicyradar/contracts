from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class Label(BaseModel):
    """A classification label that can be applied to a Document."""

    id: str = Field(description="Unique identifier for the label")
    name: str = Field(description="Human-readable label name")
    type: str = Field(
        description="Label category, e.g. 'sector', 'geography', 'instrument'"
    )

    model_config = {"json_schema_extra": {"examples": [{"id": "l1", "name": "Energy", "type": "sector"}]}}


class Document(BaseModel):
    """A document in the Climate Policy Radar corpus."""

    id: str = Field(description="Unique identifier for the document")
    title: str = Field(description="Document title")
    source_url: str | None = Field(default=None, description="URL of the source document")
    publication_date: date | None = Field(
        default=None, description="Date the document was published"
    )
    content: str | None = Field(default=None, description="Full text content of the document")
    labels: list[Label] = Field(
        default_factory=list, description="Labels applied to this document"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary additional metadata",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "doc1",
                    "title": "UK Climate Change Act 2008",
                    "source_url": "https://example.com/doc.pdf",
                    "publication_date": "2008-11-26",
                    "content": None,
                    "labels": [{"id": "l1", "name": "Energy", "type": "sector"}],
                    "metadata": {},
                }
            ]
        }
    }
