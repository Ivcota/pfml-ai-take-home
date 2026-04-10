from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


MAX_LEAVE_WEEKS_PER_YEAR = 20


@dataclass(frozen=True)
class EligibilityResult:
    eligible: bool
    reason: str | None = None


def check_eligibility(
    quarterly_wages: list[Decimal],
    weeks_used_this_year: int,
) -> EligibilityResult:
    if weeks_used_this_year >= MAX_LEAVE_WEEKS_PER_YEAR:
        return EligibilityResult(eligible=False, reason="annual leave exhausted")

    has_qualifying_wages = any(w > 0 for w in quarterly_wages)
    if not has_qualifying_wages:
        return EligibilityResult(eligible=False, reason="no qualifying wages")

    return EligibilityResult(eligible=True)
