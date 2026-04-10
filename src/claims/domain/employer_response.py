from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class EmployerDecision(str, Enum):
    OBJECTED = "OBJECTED"
    NO_OBJECTION = "NO_OBJECTION"
    WINDOW_EXPIRED = "WINDOW_EXPIRED"


class EmployerResponse(BaseModel):
    model_config = {"frozen": True}

    decision: EmployerDecision
    responded_at: datetime
    reason: str | None = None
