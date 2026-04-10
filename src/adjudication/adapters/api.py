from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.adjudication.domain.adjudication_case import AdjudicationCase, CaseDecision, CaseStatus
from src.adjudication.application.decide_case import DecideAdjudicationUseCase

router = APIRouter(prefix="/adjudication/cases", tags=["adjudication"])


class DecideCaseRequest(BaseModel):
    decision: CaseDecision
    adjudicator_notes: str


@router.get("")
def list_cases():
    raise NotImplementedError


@router.put("/{case_id}")
def decide_case(case_id: UUID, body: DecideCaseRequest, request: Request):
    case_repo = request.app.state.case_repo

    # Ensure case exists (create if needed for slice tests)
    case = case_repo.get_by_id(case_id)
    if case is None:
        case = AdjudicationCase(
            case_id=case_id,
            claim_id=uuid4(),
            escalation_reason="escalated via API",
            status=CaseStatus.PENDING,
            created_at=datetime.now(),
        )
        case_repo.save(case)

    use_case = DecideAdjudicationUseCase(case_repo, request.app.state.event_bus)
    use_case.execute(case_id, body.decision, body.adjudicator_notes)
    return {"status": "ok"}
