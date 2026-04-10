from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from src.claims.domain.eligibility_policy import check_eligibility
from src.claims.domain.events import ClaimDenied, EmployerNotified
from src.claims.ports.claim_repository import ClaimRepository
from src.claims.ports.wage_reporting_gateway import WageReportingGateway
from src.shared.event_bus import EventBus

EMPLOYER_RESPONSE_DAYS = 10


class CheckEligibilityUseCase:
    def __init__(
        self,
        claim_repo: ClaimRepository,
        wage_gateway: WageReportingGateway,
        event_bus: EventBus,
    ) -> None:
        self._claim_repo = claim_repo
        self._wage_gateway = wage_gateway
        self._event_bus = event_bus

    def execute(self, claim_id: UUID) -> None:
        claim = self._claim_repo.get_by_id(claim_id)
        claim.begin_eligibility_check()

        quarterly_wages = self._wage_gateway.get_quarterly_wages(claim.employee_ssn, 4)
        weeks_used = self._claim_repo.get_approved_weeks_in_year(
            claim.employee_ssn, claim.leave_start_date.year
        )

        result = check_eligibility(quarterly_wages, weeks_used)

        if result.eligible:
            claim.mark_awaiting_employer()
            self._claim_repo.save(claim)
            self._event_bus.publish(
                EmployerNotified(
                    claim_id=claim.claim_id,
                    employer_fein=claim.employer_fein,
                    deadline_at=datetime.now() + timedelta(days=EMPLOYER_RESPONSE_DAYS),
                )
            )
        else:
            claim.deny(result.reason)
            self._claim_repo.save(claim)
            self._event_bus.publish(
                ClaimDenied(
                    claim_id=claim.claim_id,
                    denial_reason=result.reason,
                )
            )
