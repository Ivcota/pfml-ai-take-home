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
    raise NotImplementedError
