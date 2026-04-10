from datetime import datetime
from uuid import uuid4

import pytest

from src.adjudication.domain.adjudication_case import (
    AdjudicationCase,
    CaseDecision,
    CaseStatus,
)


def make_case(
    case_id=None,
    claim_id=None,
    escalation_reason="employer objection",
    status=CaseStatus.PENDING,
    created_at=None,
) -> AdjudicationCase:
    return AdjudicationCase(
        case_id=case_id or uuid4(),
        claim_id=claim_id or uuid4(),
        escalation_reason=escalation_reason,
        status=status,
        created_at=created_at or datetime(2026, 5, 1),
    )


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
