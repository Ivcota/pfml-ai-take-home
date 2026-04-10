from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class PaymentType(str, Enum):
    CHECK = "CHECK"
    DIRECT_DEPOSIT = "DIRECT_DEPOSIT"


class PaymentMethod(BaseModel):
    model_config = {"frozen": True}

    type: PaymentType
    mailing_address: str | None = None
    bank_routing_number: str | None = None
    bank_account_number: str | None = None
