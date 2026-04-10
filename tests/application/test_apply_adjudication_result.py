from src.claims.application.apply_adjudication_result import ApplyAdjudicationResultUseCase
from src.claims.domain.claim import ClaimStatus
from src.claims.domain.events import ClaimApproved, ClaimDenied
from tests.conftest import make_claim


class TestApplyAdjudicationResultApproved:
    def test_approved_transitions_claim(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.ESCALATED)
        claim_repo.save(claim)

        use_case = ApplyAdjudicationResultUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id, "APPROVED")

        updated = claim_repo.get_by_id(claim.claim_id)
        assert updated.status == ClaimStatus.APPROVED

    def test_approved_publishes_claim_approved(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.ESCALATED)
        claim_repo.save(claim)

        use_case = ApplyAdjudicationResultUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id, "APPROVED")

        approved_events = [e for e in event_bus.published if isinstance(e, ClaimApproved)]
        assert len(approved_events) == 1


class TestApplyAdjudicationResultDenied:
    def test_denied_transitions_claim(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.ESCALATED)
        claim_repo.save(claim)

        use_case = ApplyAdjudicationResultUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id, "DENIED")

        updated = claim_repo.get_by_id(claim.claim_id)
        assert updated.status == ClaimStatus.DENIED

    def test_denied_publishes_claim_denied(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.ESCALATED)
        claim_repo.save(claim)

        use_case = ApplyAdjudicationResultUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id, "DENIED")

        denied_events = [e for e in event_bus.published if isinstance(e, ClaimDenied)]
        assert len(denied_events) == 1
