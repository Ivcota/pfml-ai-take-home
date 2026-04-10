from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class PaymentType(StrEnum):
    CHECK = "CHECK"
    DIRECT_DEPOSIT = "DIRECT_DEPOSIT"


class PaymentMethod(BaseModel):
    model_config = {"frozen": True}

    type: PaymentType
    mailing_address: str | None = None
    bank_routing_number: str | None = None
    bank_account_number: str | None = None
