from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from src.shared.domain_event import DomainEvent


class PaymentDisbursed(DomainEvent):
    payment_id: UUID
    schedule_id: UUID
    amount: Decimal


class PaymentFailed(DomainEvent):
    payment_id: UUID
    schedule_id: UUID
    reason: str
