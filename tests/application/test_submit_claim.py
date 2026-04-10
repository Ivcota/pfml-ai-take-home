from datetime import datetime

from src.claims.application.submit_claim import SubmitClaimUseCase
from src.claims.domain.claim import ClaimStatus, LeaveType
from src.claims.domain.events import ClaimSubmitted


class TestSubmitClaim:
    def test_creates_claim_with_submitted_status(self, claim_repo, event_bus):
        use_case = SubmitClaimUseCase(claim_repo, event_bus)
        claim_id = use_case.execute(
            employee_ssn="123-45-6789",
            employer_fein="12-3456789",
            leave_type=LeaveType.BONDING,
            leave_start_date=datetime(2026, 5, 1),
            leave_end_date=datetime(2026, 7, 24),
        )
        claim = claim_repo.get_by_id(claim_id)
        assert claim is not None
        assert claim.status == ClaimStatus.SUBMITTED

    def test_publishes_claim_submitted_event(self, claim_repo, event_bus):
        use_case = SubmitClaimUseCase(claim_repo, event_bus)
        claim_id = use_case.execute(
            employee_ssn="123-45-6789",
            employer_fein="12-3456789",
            leave_type=LeaveType.BONDING,
            leave_start_date=datetime(2026, 5, 1),
            leave_end_date=datetime(2026, 7, 24),
        )
        assert len(event_bus.published) == 1
        event = event_bus.published[0]
        assert isinstance(event, ClaimSubmitted)
        assert event.claim_id == claim_id
