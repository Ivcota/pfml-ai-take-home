from __future__ import annotations

from uuid import UUID

from src.claims.ports.claim_repository import ClaimRepository
from src.shared.event_bus import EventBus


class HandleEmployerTimeoutUseCase:
    def __init__(self, claim_repo: ClaimRepository, event_bus: EventBus) -> None:
        self._claim_repo = claim_repo
        self._event_bus = event_bus

    def execute(self, claim_id: UUID) -> None:
        raise NotImplementedError
