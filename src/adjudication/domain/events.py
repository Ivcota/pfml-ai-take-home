from __future__ import annotations

from uuid import UUID

from src.shared.domain_event import DomainEvent


class AdjudicationCompleted(DomainEvent):
    case_id: UUID
    claim_id: UUID
    decision: str  # "APPROVED" or "DENIED"
