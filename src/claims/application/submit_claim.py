from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from src.claims.domain.claim import Claim, LeaveType
from src.claims.domain.events import ClaimSubmitted
from src.claims.ports.claim_repository import ClaimRepository
from src.shared.event_bus import EventBus


class SubmitClaimUseCase:
    def __init__(self, claim_repo: ClaimRepository, event_bus: EventBus) -> None:
        self._claim_repo = claim_repo
        self._event_bus = event_bus

    def execute(
        self,
        employee_ssn: str,
        employer_fein: str,
        leave_type: LeaveType,
        leave_start_date: datetime,
        leave_end_date: datetime,
    ) -> UUID:
        claim = Claim(
            claim_id=uuid4(),
            employee_ssn=employee_ssn,
            employer_fein=employer_fein,
            leave_type=leave_type,
            leave_start_date=leave_start_date,
            leave_end_date=leave_end_date,
            submitted_at=datetime.now(),
        )
        self._claim_repo.save(claim)
        self._event_bus.publish(
            ClaimSubmitted(
                claim_id=claim.claim_id,
                employee_ssn=employee_ssn,
                employer_fein=employer_fein,
                leave_type=leave_type.value,
                leave_start_date=leave_start_date,
                leave_end_date=leave_end_date,
            )
        )
        return claim.claim_id
