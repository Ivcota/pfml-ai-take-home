from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.payments.domain.payment import Payment
from src.payments.domain.payment_method import PaymentMethod


class PaymentSchedule(BaseModel):
    schedule_id: UUID
    claim_id: UUID
    weekly_benefit_amount: Decimal
    payment_method: PaymentMethod
    start_date: datetime
    end_date: datetime
    payments: list[Payment] = []
    created_at: datetime | None = None

    def generate_payments(self) -> None:
        raise NotImplementedError
