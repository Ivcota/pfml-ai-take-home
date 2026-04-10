from datetime import datetime, timedelta
from decimal import Decimal

from src.claims.application.check_eligibility import CheckEligibilityUseCase
from src.claims.application.event_handlers import EmployerNotifiedHandler
from src.claims.application.handle_employer_timeout import HandleEmployerTimeoutUseCase
from src.claims.domain.claim import ClaimStatus
from src.claims.domain.events import EmployerNotified
from src.shared.in_memory_scheduler import InMemoryScheduler
from tests.conftest import make_claim


class TestEmployerNotifiedHandler:
    def test_schedules_deadline_on_employer_notified(self, event_bus, claim_repo, wage_gateway):
        scheduler = InMemoryScheduler()
        handler = EmployerNotifiedHandler(scheduler)
        event_bus.subscribe(EmployerNotified, handler.handle)

        claim = make_claim(status=ClaimStatus.SUBMITTED)
        claim_repo.save(claim)
        wage_gateway.set_wages(claim.employee_ssn, [Decimal("10000")] * 4)

        uc = CheckEligibilityUseCase(claim_repo, wage_gateway, event_bus)
        uc.execute(claim.claim_id)

        assert len(scheduler.pending) == 1
        item = scheduler.pending[0]
        assert item.event_type == "EmployerResponseDeadline"
        assert item.payload["claim_id"] == str(claim.claim_id)

    def test_trigger_due_fires_employer_timeout(self, event_bus, claim_repo, wage_gateway):
        scheduler = InMemoryScheduler()
        handler = EmployerNotifiedHandler(scheduler)
        event_bus.subscribe(EmployerNotified, handler.handle)

        timeout_uc = HandleEmployerTimeoutUseCase(claim_repo, event_bus)
        scheduler.on(
            "EmployerResponseDeadline",
            lambda payload: timeout_uc.execute(__import__("uuid").UUID(payload["claim_id"])),
        )

        claim = make_claim(status=ClaimStatus.SUBMITTED)
        claim_repo.save(claim)
        wage_gateway.set_wages(claim.employee_ssn, [Decimal("10000")] * 4)

        uc = CheckEligibilityUseCase(claim_repo, wage_gateway, event_bus)
        uc.execute(claim.claim_id)

        # Simulate time passing beyond the deadline
        scheduler.trigger_due(as_of=datetime.now() + timedelta(days=11))

        updated = claim_repo.get_by_id(claim.claim_id)
        assert updated.status == ClaimStatus.APPROVED
