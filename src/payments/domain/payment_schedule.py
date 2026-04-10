from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel

from src.payments.domain.payment import Payment, PaymentStatus
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
        days = (self.end_date - self.start_date).days
        num_weeks = (days + 6) // 7
        self.payments = [
            Payment(
                payment_id=uuid4(),
                week_start_date=self.start_date + timedelta(weeks=i),
                amount=self.weekly_benefit_amount,
                status=PaymentStatus.SCHEDULED,
            )
            for i in range(num_weeks)
        ]
