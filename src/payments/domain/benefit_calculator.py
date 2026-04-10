from __future__ import annotations

from decimal import Decimal


def calculate_weekly_benefit(quarterly_wages: list[Decimal], state_ceiling: Decimal) -> Decimal:
    """min(avg_quarterly_wages / 13, state_ceiling)"""
    raise NotImplementedError
