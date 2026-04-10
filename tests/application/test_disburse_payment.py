from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.payments.application.disburse_payment import DisbursePaymentUseCase
from src.payments.domain.events import PaymentDisbursed, PaymentFailed
from src.payments.domain.payment import Payment, PaymentStatus
from src.payments.domain.payment_method import PaymentMethod, PaymentType
from src.payments.domain.payment_schedule import PaymentSchedule


def make_schedule_with_payment(payment_status=PaymentStatus.SCHEDULED):
    payment_id = uuid4()
    schedule = PaymentSchedule(
        schedule_id=uuid4(),
        claim_id=uuid4(),
        weekly_benefit_amount=Decimal("800.00"),
        payment_method=PaymentMethod(
            type=PaymentType.DIRECT_DEPOSIT,
            bank_routing_number="021000021",
            bank_account_number="123456789",
        ),
        start_date=datetime(2026, 5, 5),
        end_date=datetime(2026, 5, 12),
        payments=[
            Payment(
                payment_id=payment_id,
                week_start_date=datetime(2026, 5, 5),
                amount=Decimal("800.00"),
                status=payment_status,
            )
        ],
    )
    return schedule, payment_id


class TestDisbursePaymentSuccess:
    def test_payment_transitions_to_disbursed(self, schedule_repo, payment_gateway, event_bus):
        schedule, payment_id = make_schedule_with_payment()
        schedule_repo.save(schedule)

        use_case = DisbursePaymentUseCase(schedule_repo, payment_gateway, event_bus)
        use_case.execute(schedule.schedule_id, payment_id)

        updated = schedule_repo.get_by_id(schedule.schedule_id)
        payment = next(p for p in updated.payments if p.payment_id == payment_id)
        assert payment.status == PaymentStatus.DISBURSED
        assert payment.gateway_reference is not None

    def test_publishes_payment_disbursed_event(self, schedule_repo, payment_gateway, event_bus):
        schedule, payment_id = make_schedule_with_payment()
        schedule_repo.save(schedule)

        use_case = DisbursePaymentUseCase(schedule_repo, payment_gateway, event_bus)
        use_case.execute(schedule.schedule_id, payment_id)

        disbursed_events = [e for e in event_bus.published if isinstance(e, PaymentDisbursed)]
        assert len(disbursed_events) == 1
        assert disbursed_events[0].payment_id == payment_id


class TestDisbursePaymentFailure:
    def test_payment_transitions_to_failed(self, schedule_repo, payment_gateway, event_bus):
        schedule, payment_id = make_schedule_with_payment()
        schedule_repo.save(schedule)
        payment_gateway.set_should_fail(True, reason="insufficient funds")

        use_case = DisbursePaymentUseCase(schedule_repo, payment_gateway, event_bus)
        use_case.execute(schedule.schedule_id, payment_id)

        updated = schedule_repo.get_by_id(schedule.schedule_id)
        payment = next(p for p in updated.payments if p.payment_id == payment_id)
        assert payment.status == PaymentStatus.FAILED

    def test_publishes_payment_failed_event(self, schedule_repo, payment_gateway, event_bus):
        schedule, payment_id = make_schedule_with_payment()
        schedule_repo.save(schedule)
        payment_gateway.set_should_fail(True, reason="insufficient funds")

        use_case = DisbursePaymentUseCase(schedule_repo, payment_gateway, event_bus)
        use_case.execute(schedule.schedule_id, payment_id)

        failed_events = [e for e in event_bus.published if isinstance(e, PaymentFailed)]
        assert len(failed_events) == 1
        assert failed_events[0].reason == "insufficient funds"
