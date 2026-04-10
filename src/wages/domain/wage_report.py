from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.wages.domain.wage_record import EmployeeWageRecord


class EmployerWageReport(BaseModel):
    report_id: UUID
    employer_fein: str
    quarter: str  # e.g. "2025-Q3"
    submitted_at: datetime
    employee_wage_records: list[EmployeeWageRecord] = []
