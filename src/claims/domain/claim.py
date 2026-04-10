from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel

from src.claims.domain.document import Document
from src.claims.domain.employer_response import EmployerResponse


class LeaveType(StrEnum):
    BONDING = "BONDING"
    MEDICAL = "MEDICAL"


class ClaimStatus(StrEnum):
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
        self._require_status(ClaimStatus.SUBMITTED)
        self.status = ClaimStatus.ELIGIBILITY_CHECK

    def mark_awaiting_employer(self) -> None:
        self._require_status(ClaimStatus.ELIGIBILITY_CHECK)
        self.status = ClaimStatus.AWAITING_EMPLOYER

    def approve(self) -> None:
        self._require_status(ClaimStatus.AWAITING_EMPLOYER, ClaimStatus.ESCALATED)
        self.status = ClaimStatus.APPROVED

    def deny(self, reason: str) -> None:
        self._require_status(ClaimStatus.ELIGIBILITY_CHECK, ClaimStatus.ESCALATED)
        self.status = ClaimStatus.DENIED
        self.denial_reason = reason

    def escalate(self) -> None:
        self._require_status(ClaimStatus.AWAITING_EMPLOYER)
        self.status = ClaimStatus.ESCALATED

    def record_employer_response(self, response: EmployerResponse) -> None:
        self.employer_response = response

    def attach_document(self, document: Document) -> None:
        self.documents.append(document)

    def _require_status(self, *allowed: ClaimStatus) -> None:
        if self.status not in allowed:
            raise ValueError(
                f"Cannot transition from {self.status}; expected one of {allowed}"
            )
