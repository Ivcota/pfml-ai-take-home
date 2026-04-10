from decimal import Decimal

from src.claims.application.check_eligibility import CheckEligibilityUseCase
from src.claims.domain.claim import ClaimStatus
from src.claims.domain.events import ClaimDenied, EmployerNotified
from tests.conftest import make_claim


class TestCheckEligibilityEligible:
    def test_eligible_transitions_to_awaiting_employer(self, claim_repo, wage_gateway, event_bus):
        claim = make_claim(status=ClaimStatus.SUBMITTED)
        claim_repo.save(claim)
        wage_gateway.set_wages(claim.employee_ssn, [Decimal("10000")] * 4)

        use_case = CheckEligibilityUseCase(claim_repo, wage_gateway, event_bus)
        use_case.execute(claim.claim_id)

        updated = claim_repo.get_by_id(claim.claim_id)
        assert updated.status == ClaimStatus.AWAITING_EMPLOYER

    def test_eligible_publishes_employer_notified(self, claim_repo, wage_gateway, event_bus):
        claim = make_claim(status=ClaimStatus.SUBMITTED)
        claim_repo.save(claim)
        wage_gateway.set_wages(claim.employee_ssn, [Decimal("10000")] * 4)

        use_case = CheckEligibilityUseCase(claim_repo, wage_gateway, event_bus)
        use_case.execute(claim.claim_id)

        notified_events = [e for e in event_bus.published if isinstance(e, EmployerNotified)]
        assert len(notified_events) == 1
        assert notified_events[0].claim_id == claim.claim_id


class TestCheckEligibilityIneligibleNoWages:
    def test_no_wages_denies_claim(self, claim_repo, wage_gateway, event_bus):
        claim = make_claim(status=ClaimStatus.SUBMITTED)
        claim_repo.save(claim)
        wage_gateway.set_wages(claim.employee_ssn, [])

        use_case = CheckEligibilityUseCase(claim_repo, wage_gateway, event_bus)
        use_case.execute(claim.claim_id)

        updated = claim_repo.get_by_id(claim.claim_id)
        assert updated.status == ClaimStatus.DENIED
        assert updated.denial_reason == "no qualifying wages"

    def test_no_wages_publishes_claim_denied(self, claim_repo, wage_gateway, event_bus):
        claim = make_claim(status=ClaimStatus.SUBMITTED)
        claim_repo.save(claim)
        wage_gateway.set_wages(claim.employee_ssn, [])

        use_case = CheckEligibilityUseCase(claim_repo, wage_gateway, event_bus)
        use_case.execute(claim.claim_id)

        denied_events = [e for e in event_bus.published if isinstance(e, ClaimDenied)]
        assert len(denied_events) == 1
        assert denied_events[0].denial_reason == "no qualifying wages"


class TestCheckEligibilityIneligible20Weeks:
    def test_20_weeks_exhausted_denies_claim(self, claim_repo, wage_gateway, event_bus):
        # Pre-seed an approved claim consuming 20 weeks
        from datetime import datetime, timedelta
        existing = make_claim(
            employee_ssn="123-45-6789",
            status=ClaimStatus.APPROVED,
            leave_start_date=datetime(2026, 1, 5),
            leave_end_date=datetime(2026, 1, 5) + timedelta(weeks=20),
        )
        claim_repo.save(existing)

        claim = make_claim(employee_ssn="123-45-6789", status=ClaimStatus.SUBMITTED)
        claim_repo.save(claim)
        wage_gateway.set_wages(claim.employee_ssn, [Decimal("10000")] * 4)

        use_case = CheckEligibilityUseCase(claim_repo, wage_gateway, event_bus)
        use_case.execute(claim.claim_id)

        updated = claim_repo.get_by_id(claim.claim_id)
        assert updated.status == ClaimStatus.DENIED
        assert updated.denial_reason == "annual leave exhausted"
