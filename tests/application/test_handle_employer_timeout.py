from src.claims.application.handle_employer_timeout import HandleEmployerTimeoutUseCase
from src.claims.domain.claim import ClaimStatus
from src.claims.domain.employer_response import EmployerDecision
from src.claims.domain.events import ClaimApproved
from tests.conftest import make_claim


class TestHandleEmployerTimeout:
    def test_timeout_records_window_expired(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.AWAITING_EMPLOYER)
        claim_repo.save(claim)

        use_case = HandleEmployerTimeoutUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id)

        updated = claim_repo.get_by_id(claim.claim_id)
        assert updated.employer_response.decision == EmployerDecision.WINDOW_EXPIRED

    def test_timeout_approves_claim(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.AWAITING_EMPLOYER)
        claim_repo.save(claim)

        use_case = HandleEmployerTimeoutUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id)

        updated = claim_repo.get_by_id(claim.claim_id)
        assert updated.status == ClaimStatus.APPROVED

    def test_timeout_publishes_claim_approved(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.AWAITING_EMPLOYER)
        claim_repo.save(claim)

        use_case = HandleEmployerTimeoutUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id)

        approved_events = [e for e in event_bus.published if isinstance(e, ClaimApproved)]
        assert len(approved_events) == 1
