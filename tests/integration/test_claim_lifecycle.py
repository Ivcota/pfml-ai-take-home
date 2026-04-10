from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import pytest

from src.shared.in_memory_event_bus import InMemoryEventBus
from tests.fakes.fake_claim_repository import FakeClaimRepository
from tests.fakes.fake_case_repository import FakeAdjudicationCaseRepository
from tests.fakes.fake_schedule_repository import FakePaymentScheduleRepository
from tests.fakes.fake_wage_gateway import FakeWageReportingGateway

from src.claims.domain.claim import LeaveType, ClaimStatus
from src.claims.domain.employer_response import EmployerDecision
from src.claims.domain.events import ClaimApproved, ClaimEscalated
from src.adjudication.domain.adjudication_case import CaseDecision
from src.adjudication.domain.events import AdjudicationCompleted
from src.payments.domain.benefit_config import BenefitConfig

from src.claims.application.submit_claim import SubmitClaimUseCase
from src.claims.application.check_eligibility import CheckEligibilityUseCase
from src.claims.application.record_employer_response import RecordEmployerResponseUseCase
from src.claims.application.apply_adjudication_result import ApplyAdjudicationResultUseCase
from src.adjudication.application.create_case import CreateAdjudicationCaseUseCase
from src.adjudication.application.decide_case import DecideAdjudicationUseCase
from src.payments.application.create_payment_schedule import CreatePaymentScheduleUseCase

from src.adjudication.application.event_handlers import ClaimEscalatedHandler
from src.claims.application.event_handlers import AdjudicationCompletedHandler
from src.payments.application.event_handlers import ClaimApprovedHandler


@dataclass
class WiredSystem:
    event_bus: InMemoryEventBus
    claim_repo: FakeClaimRepository
    case_repo: FakeAdjudicationCaseRepository
    schedule_repo: FakePaymentScheduleRepository
    wage_gateway: FakeWageReportingGateway
    submit_claim: SubmitClaimUseCase
    check_eligibility: CheckEligibilityUseCase
    record_employer_response: RecordEmployerResponseUseCase
    decide_adjudication: DecideAdjudicationUseCase


@pytest.fixture
def system() -> WiredSystem:
    event_bus = InMemoryEventBus()
    claim_repo = FakeClaimRepository()
    case_repo = FakeAdjudicationCaseRepository()
    schedule_repo = FakePaymentScheduleRepository()
    wage_gateway = FakeWageReportingGateway()
    benefit_config = BenefitConfig(state_ceiling=Decimal("1200.00"))

    # Use cases
    submit_claim = SubmitClaimUseCase(claim_repo, event_bus)
    check_eligibility = CheckEligibilityUseCase(claim_repo, wage_gateway, event_bus)
    record_employer_response = RecordEmployerResponseUseCase(claim_repo, event_bus)
    apply_adjudication_result = ApplyAdjudicationResultUseCase(claim_repo, event_bus)
    create_case = CreateAdjudicationCaseUseCase(case_repo)
    decide_adjudication = DecideAdjudicationUseCase(case_repo, event_bus)
    create_payment_schedule = CreatePaymentScheduleUseCase(
        schedule_repo, wage_gateway, benefit_config, event_bus,
    )

    # Wire cross-context event handlers
    escalated_handler = ClaimEscalatedHandler(create_case)
    event_bus.subscribe(ClaimEscalated, escalated_handler.handle)

    completed_handler = AdjudicationCompletedHandler(apply_adjudication_result)
    event_bus.subscribe(AdjudicationCompleted, completed_handler.handle)

    approved_handler = ClaimApprovedHandler(create_payment_schedule)
    event_bus.subscribe(ClaimApproved, approved_handler.handle)

    return WiredSystem(
        event_bus=event_bus,
        claim_repo=claim_repo,
        case_repo=case_repo,
        schedule_repo=schedule_repo,
        wage_gateway=wage_gateway,
        submit_claim=submit_claim,
        check_eligibility=check_eligibility,
        record_employer_response=record_employer_response,
        decide_adjudication=decide_adjudication,
    )


SSN = "123-45-6789"
FEIN = "12-3456789"
START = datetime(2026, 5, 1)
END = datetime(2026, 5, 22)  # 3 weeks
QUARTERLY_WAGES = [Decimal("15000"), Decimal("15000"), Decimal("15000"), Decimal("15000")]


class TestHappyPath:
    def test_approved_claim_creates_payment_schedule(self, system: WiredSystem):
        system.wage_gateway.set_wages(SSN, QUARTERLY_WAGES)

        claim_id = system.submit_claim.execute(SSN, FEIN, LeaveType.BONDING, START, END)
        system.check_eligibility.execute(claim_id)
        system.record_employer_response.execute(claim_id, EmployerDecision.NO_OBJECTION)

        claim = system.claim_repo.get_by_id(claim_id)
        assert claim.status == ClaimStatus.APPROVED

        schedule = system.schedule_repo.get_by_claim_id(claim_id)
        assert schedule is not None
        assert schedule.weekly_benefit_amount == min(
            sum(QUARTERLY_WAGES) / 4 / 13, Decimal("1200.00")
        )
        assert len(schedule.payments) == 3


class TestEscalationPath:
    def test_escalated_claim_approved_by_adjudicator_creates_payment_schedule(self, system: WiredSystem):
        system.wage_gateway.set_wages(SSN, QUARTERLY_WAGES)

        claim_id = system.submit_claim.execute(SSN, FEIN, LeaveType.BONDING, START, END)
        system.check_eligibility.execute(claim_id)
        system.record_employer_response.execute(
            claim_id, EmployerDecision.OBJECTED, reason="disputed dates",
        )

        # Escalation should have auto-created an adjudication case
        case = system.case_repo.get_by_claim_id(claim_id)
        assert case is not None

        # Adjudicator approves — should cascade back through Claims → Payments
        system.decide_adjudication.execute(case.case_id, CaseDecision.APPROVED, "dates verified")

        claim = system.claim_repo.get_by_id(claim_id)
        assert claim.status == ClaimStatus.APPROVED

        schedule = system.schedule_repo.get_by_claim_id(claim_id)
        assert schedule is not None
        assert len(schedule.payments) == 3


class TestDenialPaths:
    def test_ineligible_claim_is_denied_with_no_payment_schedule(self, system: WiredSystem):
        # No wages → ineligible
        system.wage_gateway.set_wages(SSN, [Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0")])

        claim_id = system.submit_claim.execute(SSN, FEIN, LeaveType.MEDICAL, START, END)
        system.check_eligibility.execute(claim_id)

        claim = system.claim_repo.get_by_id(claim_id)
        assert claim.status == ClaimStatus.DENIED

        assert system.schedule_repo.get_by_claim_id(claim_id) is None

    def test_adjudicator_denies_escalated_claim_with_no_payment_schedule(self, system: WiredSystem):
        system.wage_gateway.set_wages(SSN, QUARTERLY_WAGES)

        claim_id = system.submit_claim.execute(SSN, FEIN, LeaveType.BONDING, START, END)
        system.check_eligibility.execute(claim_id)
        system.record_employer_response.execute(
            claim_id, EmployerDecision.OBJECTED, reason="fraudulent",
        )

        case = system.case_repo.get_by_claim_id(claim_id)
        system.decide_adjudication.execute(case.case_id, CaseDecision.DENIED, "claim is fraudulent")

        claim = system.claim_repo.get_by_id(claim_id)
        assert claim.status == ClaimStatus.DENIED

        assert system.schedule_repo.get_by_claim_id(claim_id) is None
