from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.claims.domain.claim import LeaveType
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
        raise NotImplementedError
