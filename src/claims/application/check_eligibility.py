from __future__ import annotations

from uuid import UUID

from src.claims.ports.claim_repository import ClaimRepository
from src.claims.ports.wage_reporting_gateway import WageReportingGateway
from src.shared.event_bus import EventBus


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
        raise NotImplementedError
