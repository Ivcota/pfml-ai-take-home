from __future__ import annotations

import pytest
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from src.shared.in_memory_event_bus import InMemoryEventBus
from tests.fakes.fake_claim_repository import FakeClaimRepository
from tests.fakes.fake_case_repository import FakeAdjudicationCaseRepository
from tests.fakes.fake_schedule_repository import FakePaymentScheduleRepository
from tests.fakes.fake_wage_gateway import FakeWageReportingGateway
from tests.fakes.fake_payment_gateway import FakePaymentGateway
from src.claims.domain.claim import Claim, LeaveType, ClaimStatus
from src.payments.domain.benefit_config import BenefitConfig


@pytest.fixture
def event_bus():
    return InMemoryEventBus()


@pytest.fixture
def claim_repo():
    return FakeClaimRepository()


@pytest.fixture
def case_repo():
    return FakeAdjudicationCaseRepository()


@pytest.fixture
def schedule_repo():
    return FakePaymentScheduleRepository()


@pytest.fixture
def wage_gateway():
    return FakeWageReportingGateway()


@pytest.fixture
def payment_gateway():
    return FakePaymentGateway()


@pytest.fixture
def benefit_config():
    return BenefitConfig(state_ceiling=Decimal("1200.00"))


def make_claim(**overrides) -> Claim:
    defaults = dict(
        claim_id=uuid4(),
        employee_ssn="123-45-6789",
        employer_fein="12-3456789",
        leave_type=LeaveType.BONDING,
        leave_start_date=datetime(2026, 5, 1),
        leave_end_date=datetime(2026, 7, 24),
        status=ClaimStatus.SUBMITTED,
        submitted_at=datetime(2026, 4, 15),
    )
    defaults.update(overrides)
    return Claim(**defaults)
