from __future__ import annotations

from uuid import UUID

from src.payments.domain.events import PaymentDisbursed, PaymentFailed
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
        schedule = self._schedule_repo.get_by_id(schedule_id)
        payment = next(p for p in schedule.payments if p.payment_id == payment_id)

        payment.mark_processing()
        result = self._payment_gateway.initiate_disbursement(
            str(payment.payment_id), payment.amount, schedule.payment_method
        )

        if result.success:
            payment.mark_disbursed(result.reference)
            self._schedule_repo.save(schedule)
            self._event_bus.publish(
                PaymentDisbursed(
                    payment_id=payment.payment_id,
                    schedule_id=schedule.schedule_id,
                    amount=payment.amount,
                )
            )
        else:
            payment.mark_failed()
            self._schedule_repo.save(schedule)
            self._event_bus.publish(
                PaymentFailed(
                    payment_id=payment.payment_id,
                    schedule_id=schedule.schedule_id,
                    reason=result.error,
                )
            )
