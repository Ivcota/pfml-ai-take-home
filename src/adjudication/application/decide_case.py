from __future__ import annotations

from uuid import UUID

from src.adjudication.domain.adjudication_case import CaseDecision
from src.adjudication.ports.case_repository import AdjudicationCaseRepository
from src.shared.event_bus import EventBus


class DecideAdjudicationUseCase:
    def __init__(self, case_repo: AdjudicationCaseRepository, event_bus: EventBus) -> None:
        self._case_repo = case_repo
        self._event_bus = event_bus

    def execute(self, case_id: UUID, decision: CaseDecision, notes: str) -> None:
        raise NotImplementedError
