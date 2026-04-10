from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("")
def submit_claim():
    raise NotImplementedError


@router.post("/{claim_id}/documents")
def upload_document(claim_id: str):
    raise NotImplementedError


@router.post("/{claim_id}/employer-response")
def record_employer_response(claim_id: str):
    raise NotImplementedError
