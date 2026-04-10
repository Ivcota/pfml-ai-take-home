from __future__ import annotations

from uuid import UUID

from src.payments.domain.payment_schedule import PaymentSchedule


class FakePaymentScheduleRepository:
    def __init__(self) -> None:
        self._schedules: dict[UUID, PaymentSchedule] = {}

    def save(self, schedule: PaymentSchedule) -> None:
        self._schedules[schedule.schedule_id] = schedule

    def get_by_id(self, schedule_id: UUID) -> PaymentSchedule | None:
        return self._schedules.get(schedule_id)

    def get_by_claim_id(self, claim_id: UUID) -> PaymentSchedule | None:
        for schedule in self._schedules.values():
            if schedule.claim_id == claim_id:
                return schedule
        return None
