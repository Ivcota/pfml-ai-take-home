from __future__ import annotations

from uuid import UUID

from src.adjudication.domain.adjudication_case import CaseDecision
from src.adjudication.domain.events import AdjudicationCompleted
from src.adjudication.ports.case_repository import AdjudicationCaseRepository
from src.shared.event_bus import EventBus


class DecideAdjudicationUseCase:
    def __init__(self, case_repo: AdjudicationCaseRepository, event_bus: EventBus) -> None:
        self._case_repo = case_repo
        self._event_bus = event_bus

    def execute(self, case_id: UUID, decision: CaseDecision, notes: str) -> None:
        case = self._case_repo.get_by_id(case_id)
        if case is None:
            raise ValueError(f"Adjudication case {case_id} not found")
        case.begin_review()
        case.decide(decision, notes)
        self._case_repo.save(case)
        self._event_bus.publish(
            AdjudicationCompleted(
                case_id=case.case_id,
                claim_id=case.claim_id,
                decision=decision.value,
            )
        )
