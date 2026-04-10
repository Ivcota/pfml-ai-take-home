from __future__ import annotations

from uuid import UUID

from src.adjudication.domain.adjudication_case import AdjudicationCase


class FakeAdjudicationCaseRepository:
    def __init__(self) -> None:
        self._cases: dict[UUID, AdjudicationCase] = {}

    def save(self, case: AdjudicationCase) -> None:
        self._cases[case.case_id] = case

    def get_by_id(self, case_id: UUID) -> AdjudicationCase | None:
        return self._cases.get(case_id)

    def get_by_claim_id(self, claim_id: UUID) -> AdjudicationCase | None:
        for case in self._cases.values():
            if case.claim_id == claim_id:
                return case
        return None
