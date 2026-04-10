from src.claims.application.record_employer_response import RecordEmployerResponseUseCase
from src.claims.domain.claim import ClaimStatus
from src.claims.domain.employer_response import EmployerDecision
from src.claims.domain.events import ClaimApproved, ClaimEscalated
from tests.conftest import make_claim


class TestRecordEmployerResponseNoObjection:
    def test_no_objection_approves_claim(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.AWAITING_EMPLOYER)
        claim_repo.save(claim)

        use_case = RecordEmployerResponseUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id, EmployerDecision.NO_OBJECTION)

        updated = claim_repo.get_by_id(claim.claim_id)
        assert updated.status == ClaimStatus.APPROVED
        assert updated.employer_response.decision == EmployerDecision.NO_OBJECTION

    def test_no_objection_publishes_claim_approved(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.AWAITING_EMPLOYER)
        claim_repo.save(claim)

        use_case = RecordEmployerResponseUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id, EmployerDecision.NO_OBJECTION)

        approved_events = [e for e in event_bus.published if isinstance(e, ClaimApproved)]
        assert len(approved_events) == 1


class TestRecordEmployerResponseObjection:
    def test_objection_escalates_claim(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.AWAITING_EMPLOYER)
        claim_repo.save(claim)

        use_case = RecordEmployerResponseUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id, EmployerDecision.OBJECTED, reason="staffing concerns")

        updated = claim_repo.get_by_id(claim.claim_id)
        assert updated.status == ClaimStatus.ESCALATED
        assert updated.employer_response.decision == EmployerDecision.OBJECTED

    def test_objection_publishes_claim_escalated(self, claim_repo, event_bus):
        claim = make_claim(status=ClaimStatus.AWAITING_EMPLOYER)
        claim_repo.save(claim)

        use_case = RecordEmployerResponseUseCase(claim_repo, event_bus)
        use_case.execute(claim.claim_id, EmployerDecision.OBJECTED, reason="staffing concerns")

        escalated_events = [e for e in event_bus.published if isinstance(e, ClaimEscalated)]
        assert len(escalated_events) == 1
