from __future__ import annotations

from src.adjudication.application.create_case import CreateAdjudicationCaseUseCase
from src.claims.domain.events import ClaimEscalated


class ClaimEscalatedHandler:
    def __init__(self, create_case: CreateAdjudicationCaseUseCase) -> None:
        self._create_case = create_case

    def handle(self, event: ClaimEscalated) -> None:
        self._create_case.execute(event.claim_id, event.escalation_reason)
