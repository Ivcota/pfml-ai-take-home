from __future__ import annotations

from src.adjudication.domain.events import AdjudicationCompleted
from src.claims.application.apply_adjudication_result import ApplyAdjudicationResultUseCase


class AdjudicationCompletedHandler:
    def __init__(self, apply_result: ApplyAdjudicationResultUseCase) -> None:
        self._apply_result = apply_result

    def handle(self, event: AdjudicationCompleted) -> None:
        self._apply_result.execute(event.claim_id, event.decision)
