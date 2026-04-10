from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class DocumentType(str, Enum):
    BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE"
    DOCTORS_NOTE = "DOCTORS_NOTE"
    OTHER = "OTHER"


class Document(BaseModel):
    document_id: UUID
    type: DocumentType
    storage_reference: str
    uploaded_at: datetime
