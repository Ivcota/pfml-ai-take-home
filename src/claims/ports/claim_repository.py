from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.claims.domain.claim import Claim


class ClaimRepository(Protocol):
    def save(self, claim: Claim) -> None: ...

    def get_by_id(self, claim_id: UUID) -> Claim | None: ...

    def get_approved_weeks_in_year(self, employee_ssn: str, year: int) -> int: ...
