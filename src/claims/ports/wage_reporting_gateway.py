from __future__ import annotations

from decimal import Decimal
from typing import Protocol


class WageReportingGateway(Protocol):
    def get_quarterly_wages(self, employee_ssn: str, num_quarters: int) -> list[Decimal]: ...
