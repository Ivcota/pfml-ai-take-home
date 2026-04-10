from __future__ import annotations

from src.adjudication.domain.events import AdjudicationCompleted
from src.claims.application.apply_adjudication_result import ApplyAdjudicationResultUseCase
from src.claims.domain.events import EmployerNotified
from src.shared.scheduler import Scheduler


class AdjudicationCompletedHandler:
    def __init__(self, apply_result: ApplyAdjudicationResultUseCase) -> None:
        self._apply_result = apply_result

    def handle(self, event: AdjudicationCompleted) -> None:
        self._apply_result.execute(event.claim_id, event.decision)


class EmployerNotifiedHandler:
    def __init__(self, scheduler: Scheduler) -> None:
        self._scheduler = scheduler

    def handle(self, event: EmployerNotified) -> None:
        self._scheduler.schedule(
            event_type="EmployerResponseDeadline",
            payload={"claim_id": str(event.claim_id)},
            fire_at=event.deadline_at,
        )
