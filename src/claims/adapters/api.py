from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.claims.application.submit_claim import SubmitClaimUseCase
from src.claims.application.check_eligibility import CheckEligibilityUseCase
from src.claims.application.record_employer_response import RecordEmployerResponseUseCase
from src.claims.domain.claim import LeaveType
from src.claims.domain.employer_response import EmployerDecision
from src.payments.domain.payment_method import PaymentMethod

router = APIRouter(prefix="/claims", tags=["claims"])


class SubmitClaimRequest(BaseModel):
    employee_ssn: str
    employer_fein: str
    leave_type: LeaveType
    leave_start_date: datetime
    leave_end_date: datetime
    payment_method: PaymentMethod


class EmployerResponseRequest(BaseModel):
    decision: EmployerDecision
    reason: str | None = None


@router.post("", status_code=201)
def submit_claim(body: SubmitClaimRequest, request: Request):
    submit_uc = SubmitClaimUseCase(request.app.state.claim_repo, request.app.state.event_bus)
    claim_id = submit_uc.execute(
        employee_ssn=body.employee_ssn,
        employer_fein=body.employer_fein,
        leave_type=body.leave_type,
        leave_start_date=body.leave_start_date,
        leave_end_date=body.leave_end_date,
    )

    # Auto-trigger eligibility check
    check_uc = CheckEligibilityUseCase(
        request.app.state.claim_repo, request.app.state.wage_gateway, request.app.state.event_bus
    )
    check_uc.execute(claim_id)

    return {"claim_id": claim_id}


@router.post("/{claim_id}/documents")
def upload_document(claim_id: str):
    raise NotImplementedError


@router.post("/{claim_id}/employer-response")
def record_employer_response(claim_id: UUID, body: EmployerResponseRequest, request: Request):
    use_case = RecordEmployerResponseUseCase(request.app.state.claim_repo, request.app.state.event_bus)
    use_case.execute(claim_id, body.decision, body.reason)
    return {"status": "ok"}
