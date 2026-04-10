from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class BenefitConfig(BaseModel):
    model_config = {"frozen": True}

    state_ceiling: Decimal
