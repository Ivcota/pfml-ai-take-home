from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from src.payments.domain.payment_method import PaymentMethod


@dataclass(frozen=True)
class DisbursementResult:
    success: bool
    reference: str | None = None
    error: str | None = None


class PaymentGateway(Protocol):
    def initiate_disbursement(
        self, payment_id: str, amount: Decimal, payment_method: PaymentMethod
    ) -> DisbursementResult: ...
