from __future__ import annotations

from decimal import Decimal

from src.payments.domain.payment_method import PaymentMethod
from src.payments.ports.payment_gateway import DisbursementResult


class FakePaymentGateway:
    def __init__(self) -> None:
        self._should_fail = False
        self._fail_reason = "gateway error"
        self._reference_counter = 0

    def set_should_fail(self, fail: bool, reason: str = "gateway error") -> None:
        self._should_fail = fail
        self._fail_reason = reason

    def initiate_disbursement(
        self, payment_id: str, amount: Decimal, payment_method: PaymentMethod
    ) -> DisbursementResult:
        if self._should_fail:
            return DisbursementResult(success=False, error=self._fail_reason)
        self._reference_counter += 1
        return DisbursementResult(success=True, reference=f"REF-{self._reference_counter}")
