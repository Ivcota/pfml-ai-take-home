import pytest
from datetime import datetime
from uuid import uuid4

from src.adjudication.domain.adjudication_case import (
    AdjudicationCase,
    CaseStatus,
    CaseDecision,
)


def make_case(**overrides) -> AdjudicationCase:
    defaults = dict(
        case_id=uuid4(),
        claim_id=uuid4(),
        escalation_reason="employer objection",
        status=CaseStatus.PENDING,
        created_at=datetime(2026, 5, 1),
    )
    defaults.update(overrides)
    return AdjudicationCase(**defaults)


class TestAdjudicationCaseTransitions:
    def test_pending_to_in_review(self):
        case = make_case(status=CaseStatus.PENDING)
        case.begin_review()
        assert case.status == CaseStatus.IN_REVIEW

    def test_in_review_to_completed_approved(self):
        case = make_case(status=CaseStatus.IN_REVIEW)
        case.decide(CaseDecision.APPROVED, "claimant meets all requirements")
        assert case.status == CaseStatus.COMPLETED
        assert case.decision == CaseDecision.APPROVED
        assert case.adjudicator_notes == "claimant meets all requirements"
        assert case.decided_at is not None

    def test_in_review_to_completed_denied(self):
        case = make_case(status=CaseStatus.IN_REVIEW)
        case.decide(CaseDecision.DENIED, "insufficient documentation")
        assert case.status == CaseStatus.COMPLETED
        assert case.decision == CaseDecision.DENIED

    def test_cannot_decide_from_pending(self):
        case = make_case(status=CaseStatus.PENDING)
        with pytest.raises(ValueError):
            case.decide(CaseDecision.APPROVED, "notes")

    def test_cannot_decide_from_completed(self):
        case = make_case(status=CaseStatus.COMPLETED)
        with pytest.raises(ValueError):
            case.decide(CaseDecision.DENIED, "notes")
