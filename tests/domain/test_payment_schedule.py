from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.payments.domain.payment_schedule import PaymentSchedule
from src.payments.domain.payment import PaymentStatus
from src.payments.domain.payment_method import PaymentMethod, PaymentType


def make_schedule(**overrides) -> PaymentSchedule:
    defaults = dict(
        schedule_id=uuid4(),
        claim_id=uuid4(),
        weekly_benefit_amount=Decimal("800.00"),
        payment_method=PaymentMethod(type=PaymentType.DIRECT_DEPOSIT, bank_routing_number="021000021", bank_account_number="123456789"),
        start_date=datetime(2026, 5, 5),
        end_date=datetime(2026, 7, 20),  # ~11 weeks
        created_at=datetime(2026, 5, 1),
    )
    defaults.update(overrides)
    return PaymentSchedule(**defaults)


class TestPaymentScheduleGeneration:
    def test_generates_correct_number_of_payments(self):
        schedule = make_schedule(
            start_date=datetime(2026, 5, 5),
            end_date=datetime(2026, 7, 20),  # 11 weeks - May 5 to Jul 20
        )
        schedule.generate_payments()
        assert len(schedule.payments) == 11

    def test_all_payments_are_scheduled(self):
        schedule = make_schedule()
        schedule.generate_payments()
        assert all(p.status == PaymentStatus.SCHEDULED for p in schedule.payments)

    def test_all_payments_have_correct_amount(self):
        schedule = make_schedule(weekly_benefit_amount=Decimal("950.00"))
        schedule.generate_payments()
        assert all(p.amount == Decimal("950.00") for p in schedule.payments)

    def test_payments_have_sequential_week_start_dates(self):
        schedule = make_schedule(
            start_date=datetime(2026, 5, 5),
            end_date=datetime(2026, 5, 26),  # 3 weeks
        )
        schedule.generate_payments()
        assert len(schedule.payments) == 3
        dates = [p.week_start_date for p in schedule.payments]
        assert dates[0] == datetime(2026, 5, 5)
        assert dates[1] == datetime(2026, 5, 12)
        assert dates[2] == datetime(2026, 5, 19)
