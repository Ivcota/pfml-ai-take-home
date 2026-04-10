from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.claims.domain.employer_response import EmployerDecision, EmployerResponse
from src.claims.domain.events import ClaimApproved, ClaimEscalated
from src.claims.ports.claim_repository import ClaimRepository
from src.shared.event_bus import EventBus


class RecordEmployerResponseUseCase:
    def __init__(self, claim_repo: ClaimRepository, event_bus: EventBus) -> None:
        self._claim_repo = claim_repo
        self._event_bus = event_bus

    def execute(
        self, claim_id: UUID, decision: EmployerDecision, reason: str | None = None
    ) -> None:
        claim = self._claim_repo.get_by_id(claim_id)
        claim.record_employer_response(
            EmployerResponse(decision=decision, responded_at=datetime.now(), reason=reason)
        )

        if decision == EmployerDecision.NO_OBJECTION:
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
        elif decision == EmployerDecision.OBJECTED:
            claim.escalate()
            self._claim_repo.save(claim)
            self._event_bus.publish(
                ClaimEscalated(
                    claim_id=claim.claim_id,
                    escalation_reason=reason or "employer objection",
                )
            )
