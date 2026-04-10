from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.payments.application.create_payment_schedule import CreatePaymentScheduleUseCase
from src.payments.domain.payment import PaymentStatus
from src.payments.domain.payment_method import PaymentMethod, PaymentType


class TestCreatePaymentSchedule:
    def test_creates_schedule_with_calculated_benefit(
        self, schedule_repo, wage_gateway, benefit_config, event_bus
    ):
        claim_id = uuid4()
        wage_gateway.set_wages("123-45-6789", [Decimal("10000")] * 4)
        method = PaymentMethod(type=PaymentType.DIRECT_DEPOSIT, bank_routing_number="021000021", bank_account_number="123456789")

        use_case = CreatePaymentScheduleUseCase(schedule_repo, wage_gateway, benefit_config, event_bus)
        schedule_id = use_case.execute(
            claim_id=claim_id,
            employee_ssn="123-45-6789",
            payment_method=method,
            start_date=datetime(2026, 5, 5),
            end_date=datetime(2026, 7, 20),
        )

        schedule = schedule_repo.get_by_id(schedule_id)
        assert schedule is not None
        expected_benefit = Decimal("10000") / 13
        assert schedule.weekly_benefit_amount == expected_benefit

    def test_benefit_capped_at_state_ceiling(
        self, schedule_repo, wage_gateway, benefit_config, event_bus
    ):
        claim_id = uuid4()
        wage_gateway.set_wages("123-45-6789", [Decimal("50000")] * 4)
        method = PaymentMethod(type=PaymentType.CHECK, mailing_address="123 Main St")

        use_case = CreatePaymentScheduleUseCase(schedule_repo, wage_gateway, benefit_config, event_bus)
        schedule_id = use_case.execute(
            claim_id=claim_id,
            employee_ssn="123-45-6789",
            payment_method=method,
            start_date=datetime(2026, 5, 5),
            end_date=datetime(2026, 7, 20),
        )

        schedule = schedule_repo.get_by_id(schedule_id)
        assert schedule.weekly_benefit_amount == Decimal("1200.00")

    def test_generates_weekly_payments(
        self, schedule_repo, wage_gateway, benefit_config, event_bus
    ):
        claim_id = uuid4()
        wage_gateway.set_wages("123-45-6789", [Decimal("10000")] * 4)
        method = PaymentMethod(type=PaymentType.DIRECT_DEPOSIT, bank_routing_number="021000021", bank_account_number="123456789")

        use_case = CreatePaymentScheduleUseCase(schedule_repo, wage_gateway, benefit_config, event_bus)
        schedule_id = use_case.execute(
            claim_id=claim_id,
            employee_ssn="123-45-6789",
            payment_method=method,
            start_date=datetime(2026, 5, 5),
            end_date=datetime(2026, 5, 26),  # 3 weeks
        )

        schedule = schedule_repo.get_by_id(schedule_id)
        assert len(schedule.payments) == 3
        assert all(p.status == PaymentStatus.SCHEDULED for p in schedule.payments)
