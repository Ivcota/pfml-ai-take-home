from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from src.adjudication.domain.adjudication_case import AdjudicationCase
from src.adjudication.ports.case_repository import AdjudicationCaseRepository


class CreateAdjudicationCaseUseCase:
    def __init__(self, case_repo: AdjudicationCaseRepository) -> None:
        self._case_repo = case_repo

    def execute(self, claim_id: UUID, escalation_reason: str) -> UUID:
        case = AdjudicationCase(
            case_id=uuid4(),
            claim_id=claim_id,
            escalation_reason=escalation_reason,
            created_at=datetime.now(),
        )
        self._case_repo.save(case)
        return case.case_id
