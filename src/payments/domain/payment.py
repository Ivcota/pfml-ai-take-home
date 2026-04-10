from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class PaymentStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    PROCESSING = "PROCESSING"
    DISBURSED = "DISBURSED"
    FAILED = "FAILED"


class Payment(BaseModel):
    payment_id: UUID
    week_start_date: datetime
    amount: Decimal
    status: PaymentStatus = PaymentStatus.SCHEDULED
    disbursed_at: datetime | None = None
    gateway_reference: str | None = None

    def mark_processing(self) -> None:
        self.status = PaymentStatus.PROCESSING

    def mark_disbursed(self, gateway_reference: str) -> None:
        self.status = PaymentStatus.DISBURSED
        self.disbursed_at = datetime.now()
        self.gateway_reference = gateway_reference

    def mark_failed(self) -> None:
        self.status = PaymentStatus.FAILED
