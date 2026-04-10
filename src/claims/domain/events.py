from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.shared.domain_event import DomainEvent


class ClaimSubmitted(DomainEvent):
    claim_id: UUID
    employee_ssn: str
    employer_fein: str
    leave_type: str
    leave_start_date: datetime
    leave_end_date: datetime


class EmployerNotified(DomainEvent):
    claim_id: UUID
    employer_fein: str
    deadline_at: datetime


class ClaimApproved(DomainEvent):
    claim_id: UUID
    employee_ssn: str
    employer_fein: str
    leave_start_date: datetime
    leave_end_date: datetime


class ClaimDenied(DomainEvent):
    claim_id: UUID
    denial_reason: str


class ClaimEscalated(DomainEvent):
    claim_id: UUID
    escalation_reason: str
