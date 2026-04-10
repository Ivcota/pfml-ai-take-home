from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/adjudication/cases", tags=["adjudication"])


@router.get("")
def list_cases():
    raise NotImplementedError


@router.put("/{case_id}")
def decide_case(case_id: str):
    raise NotImplementedError
