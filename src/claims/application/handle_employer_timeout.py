from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.claims.domain.employer_response import EmployerDecision, EmployerResponse
from src.claims.domain.events import ClaimApproved
from src.claims.ports.claim_repository import ClaimRepository
from src.shared.event_bus import EventBus


class HandleEmployerTimeoutUseCase:
    def __init__(self, claim_repo: ClaimRepository, event_bus: EventBus) -> None:
        self._claim_repo = claim_repo
        self._event_bus = event_bus

    def execute(self, claim_id: UUID) -> None:
        claim = self._claim_repo.get_by_id(claim_id)
        if claim is None:
            raise ValueError(f"Claim {claim_id} not found")
        claim.record_employer_response(
            EmployerResponse(decision=EmployerDecision.WINDOW_EXPIRED, responded_at=datetime.now())
        )
        claim.approve()
        self._claim_repo.save(claim)
        self._event_bus.publish(
            ClaimApproved(
                claim_id=claim.claim_id,
                employee_ssn=claim.employee_ssn,
                employer_fein=claim.employer_fein,
                leave_start_date=claim.leave_start_date,
                leave_end_date=claim.leave_end_date,
            )
        )
