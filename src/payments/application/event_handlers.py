from __future__ import annotations

from src.claims.domain.events import ClaimApproved
from src.payments.application.create_payment_schedule import CreatePaymentScheduleUseCase
from src.payments.domain.payment_method import PaymentMethod, PaymentType


class ClaimApprovedHandler:
    def __init__(self, create_schedule: CreatePaymentScheduleUseCase) -> None:
        self._create_schedule = create_schedule

    def handle(self, event: ClaimApproved) -> None:
        # TODO: resolve payment method from employee preferences
        default_method = PaymentMethod(type=PaymentType.DIRECT_DEPOSIT)

        self._create_schedule.execute(
            claim_id=event.claim_id,
            employee_ssn=event.employee_ssn,
            payment_method=default_method,
            start_date=event.leave_start_date,
            end_date=event.leave_end_date,
        )
