from __future__ import annotations

from decimal import Decimal

from fastapi import FastAPI

from src.adjudication.adapters.api import router as adjudication_router
from src.claims.adapters.api import router as claims_router
from src.payments.domain.benefit_config import BenefitConfig
from src.shared.in_memory_event_bus import InMemoryEventBus
from tests.fakes.fake_case_repository import FakeAdjudicationCaseRepository
from tests.fakes.fake_claim_repository import FakeClaimRepository
from tests.fakes.fake_payment_gateway import FakePaymentGateway
from tests.fakes.fake_schedule_repository import FakePaymentScheduleRepository
from tests.fakes.fake_wage_gateway import FakeWageReportingGateway


def create_app() -> FastAPI:
    app = FastAPI(title="PFML")

    # Wire up in-memory dependencies
    event_bus = InMemoryEventBus()
    claim_repo = FakeClaimRepository()
    case_repo = FakeAdjudicationCaseRepository()
    schedule_repo = FakePaymentScheduleRepository()
    wage_gateway = FakeWageReportingGateway()
    payment_gateway = FakePaymentGateway()
    benefit_config = BenefitConfig(state_ceiling=Decimal("1200.00"))

    # Pre-seed wage data for test SSNs
    wage_gateway.set_wages("123-45-6789", [Decimal("10000")] * 4)

    # Store dependencies on app state for access in route handlers
    app.state.event_bus = event_bus
    app.state.claim_repo = claim_repo
    app.state.case_repo = case_repo
    app.state.schedule_repo = schedule_repo
    app.state.wage_gateway = wage_gateway
    app.state.payment_gateway = payment_gateway
    app.state.benefit_config = benefit_config

    app.include_router(claims_router)
    app.include_router(adjudication_router)
    return app


app = create_app()
