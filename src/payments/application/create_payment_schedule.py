from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.claims.ports.wage_reporting_gateway import WageReportingGateway
from src.payments.domain.benefit_config import BenefitConfig
from src.payments.domain.payment_method import PaymentMethod
from src.payments.ports.schedule_repository import PaymentScheduleRepository
from src.shared.event_bus import EventBus


class CreatePaymentScheduleUseCase:
    def __init__(
        self,
        schedule_repo: PaymentScheduleRepository,
        wage_gateway: WageReportingGateway,
        benefit_config: BenefitConfig,
        event_bus: EventBus,
    ) -> None:
        self._schedule_repo = schedule_repo
        self._wage_gateway = wage_gateway
        self._benefit_config = benefit_config
        self._event_bus = event_bus

    def execute(
        self,
        claim_id: UUID,
        employee_ssn: str,
        payment_method: PaymentMethod,
        start_date: datetime,
        end_date: datetime,
    ) -> UUID:
        from uuid import uuid4

        from src.payments.domain.benefit_calculator import calculate_weekly_benefit
        from src.payments.domain.payment_schedule import PaymentSchedule

        quarterly_wages = self._wage_gateway.get_quarterly_wages(employee_ssn, 4)
        weekly_benefit = calculate_weekly_benefit(
            quarterly_wages, self._benefit_config.state_ceiling
        )

        schedule = PaymentSchedule(
            schedule_id=uuid4(),
            claim_id=claim_id,
            weekly_benefit_amount=weekly_benefit,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date,
            created_at=datetime.now(),
        )
        schedule.generate_payments()
        self._schedule_repo.save(schedule)
        return schedule.schedule_id
