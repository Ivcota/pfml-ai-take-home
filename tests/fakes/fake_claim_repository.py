from __future__ import annotations

from uuid import UUID

from src.claims.domain.claim import Claim, ClaimStatus


class FakeClaimRepository:
    def __init__(self) -> None:
        self._claims: dict[UUID, Claim] = {}

    def save(self, claim: Claim) -> None:
        self._claims[claim.claim_id] = claim

    def get_by_id(self, claim_id: UUID) -> Claim | None:
        return self._claims.get(claim_id)

    def get_approved_weeks_in_year(self, employee_ssn: str, year: int) -> int:
        weeks = 0
        for claim in self._claims.values():
            if claim.employee_ssn == employee_ssn and claim.status == ClaimStatus.APPROVED:
                if claim.leave_start_date.year == year:
                    delta = claim.leave_end_date - claim.leave_start_date
                    weeks += delta.days // 7
        return weeks
