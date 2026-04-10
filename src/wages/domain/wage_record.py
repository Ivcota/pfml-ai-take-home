from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class EmployeeWageRecord(BaseModel):
    record_id: UUID
    employee_ssn: str
    wages_reported: Decimal
