from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class CaseStatus(StrEnum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    COMPLETED = "COMPLETED"


class CaseDecision(StrEnum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"


class AdjudicationCase(BaseModel):
    case_id: UUID
    claim_id: UUID
    escalation_reason: str
    status: CaseStatus = CaseStatus.PENDING
    decision: CaseDecision | None = None
    adjudicator_notes: str | None = None
    decided_at: datetime | None = None
    created_at: datetime | None = None

    def begin_review(self) -> None:
        if self.status != CaseStatus.PENDING:
            raise ValueError(f"Cannot begin review from {self.status}")
        self.status = CaseStatus.IN_REVIEW

    def decide(self, decision: CaseDecision, notes: str) -> None:
        if self.status != CaseStatus.IN_REVIEW:
            raise ValueError(f"Cannot decide from {self.status}")
        self.status = CaseStatus.COMPLETED
        self.decision = decision
        self.adjudicator_notes = notes
        self.decided_at = datetime.now()
