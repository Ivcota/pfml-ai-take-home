from __future__ import annotations

from uuid import UUID

from src.payments.ports.payment_gateway import PaymentGateway
from src.payments.ports.schedule_repository import PaymentScheduleRepository
from src.shared.event_bus import EventBus


class DisbursePaymentUseCase:
    def __init__(
        self,
        schedule_repo: PaymentScheduleRepository,
        payment_gateway: PaymentGateway,
        event_bus: EventBus,
    ) -> None:
        self._schedule_repo = schedule_repo
        self._payment_gateway = payment_gateway
        self._event_bus = event_bus

    def execute(self, schedule_id: UUID, payment_id: UUID) -> None:
        raise NotImplementedError
