from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.adjudication.domain.adjudication_case import AdjudicationCase


class AdjudicationCaseRepository(Protocol):
    def save(self, case: AdjudicationCase) -> None: ...

    def get_by_id(self, case_id: UUID) -> AdjudicationCase | None: ...

    def get_by_claim_id(self, claim_id: UUID) -> AdjudicationCase | None: ...
