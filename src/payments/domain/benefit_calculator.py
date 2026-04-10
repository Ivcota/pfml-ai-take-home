from __future__ import annotations

from decimal import Decimal


def calculate_weekly_benefit(quarterly_wages: list[Decimal], state_ceiling: Decimal) -> Decimal:
    """min(avg_quarterly_wages / 13, state_ceiling)"""
    avg_quarterly = sum(quarterly_wages) / len(quarterly_wages)
    weekly = avg_quarterly / 13
    return Decimal(min(weekly, state_ceiling))
