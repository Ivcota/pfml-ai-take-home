from __future__ import annotations

from decimal import Decimal


class FakeWageReportingGateway:
    def __init__(self) -> None:
        self._wages: dict[str, list[Decimal]] = {}

    def set_wages(self, employee_ssn: str, quarterly_wages: list[Decimal]) -> None:
        self._wages[employee_ssn] = quarterly_wages

    def get_quarterly_wages(self, employee_ssn: str, num_quarters: int) -> list[Decimal]:
        wages = self._wages.get(employee_ssn, [])
        return wages[:num_quarters]
