from __future__ import annotations

from uuid import UUID

from src.adjudication.ports.case_repository import AdjudicationCaseRepository


class CreateAdjudicationCaseUseCase:
    def __init__(self, case_repo: AdjudicationCaseRepository) -> None:
        self._case_repo = case_repo

    def execute(self, claim_id: UUID, escalation_reason: str) -> UUID:
        raise NotImplementedError
