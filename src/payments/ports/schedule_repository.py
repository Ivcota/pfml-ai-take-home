from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.payments.domain.payment_schedule import PaymentSchedule


class PaymentScheduleRepository(Protocol):
    def save(self, schedule: PaymentSchedule) -> None: ...

    def get_by_id(self, schedule_id: UUID) -> PaymentSchedule | None: ...

    def get_by_claim_id(self, claim_id: UUID) -> PaymentSchedule | None: ...
