from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    model_config = {"frozen": True}

    event_id: UUID
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
