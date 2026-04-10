from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from src.claims.domain.document import Document
from src.claims.domain.employer_response import EmployerResponse


class LeaveType(str, Enum):
    BONDING = "BONDING"
    MEDICAL = "MEDICAL"


class ClaimStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    ELIGIBILITY_CHECK = "ELIGIBILITY_CHECK"
    AWAITING_EMPLOYER = "AWAITING_EMPLOYER"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    ESCALATED = "ESCALATED"


class Claim(BaseModel):
    claim_id: UUID
    employee_ssn: str
    employer_fein: str
    leave_type: LeaveType
    leave_start_date: datetime
    leave_end_date: datetime
    status: ClaimStatus = ClaimStatus.SUBMITTED
    documents: list[Document] = []
    employer_response: EmployerResponse | None = None
    denial_reason: str | None = None
    submitted_at: datetime | None = None
    updated_at: datetime | None = None

    def begin_eligibility_check(self) -> None:
        raise NotImplementedError

    def mark_awaiting_employer(self) -> None:
        raise NotImplementedError

    def approve(self) -> None:
        raise NotImplementedError

    def deny(self, reason: str) -> None:
        raise NotImplementedError

    def escalate(self) -> None:
        raise NotImplementedError

    def record_employer_response(self, response: EmployerResponse) -> None:
        raise NotImplementedError

    def attach_document(self, document: Document) -> None:
        raise NotImplementedError
