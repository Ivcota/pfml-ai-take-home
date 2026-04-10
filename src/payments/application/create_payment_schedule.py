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
        raise NotImplementedError
