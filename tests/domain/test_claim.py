from datetime import datetime
from uuid import uuid4

import pytest

from src.claims.domain.claim import ClaimStatus
from src.claims.domain.document import Document, DocumentType
from src.claims.domain.employer_response import EmployerDecision, EmployerResponse
from tests.conftest import make_claim


class TestClaimTransitions:
    def test_submit_to_eligibility_check(self):
        claim = make_claim(status=ClaimStatus.SUBMITTED)
        claim.begin_eligibility_check()
        assert claim.status == ClaimStatus.ELIGIBILITY_CHECK

    def test_eligibility_check_to_awaiting_employer(self):
        claim = make_claim(status=ClaimStatus.ELIGIBILITY_CHECK)
        claim.mark_awaiting_employer()
        assert claim.status == ClaimStatus.AWAITING_EMPLOYER

    def test_awaiting_employer_to_approved(self):
        claim = make_claim(status=ClaimStatus.AWAITING_EMPLOYER)
        claim.approve()
        assert claim.status == ClaimStatus.APPROVED

    def test_awaiting_employer_to_escalated(self):
        claim = make_claim(status=ClaimStatus.AWAITING_EMPLOYER)
        claim.escalate()
        assert claim.status == ClaimStatus.ESCALATED

    def test_eligibility_check_to_denied(self):
        claim = make_claim(status=ClaimStatus.ELIGIBILITY_CHECK)
        claim.deny("no qualifying wages")
        assert claim.status == ClaimStatus.DENIED
        assert claim.denial_reason == "no qualifying wages"

    def test_escalated_to_approved(self):
        claim = make_claim(status=ClaimStatus.ESCALATED)
        claim.approve()
        assert claim.status == ClaimStatus.APPROVED

    def test_escalated_to_denied(self):
        claim = make_claim(status=ClaimStatus.ESCALATED)
        claim.deny("adjudicator denied")
        assert claim.status == ClaimStatus.DENIED

    def test_invalid_transition_raises(self):
        claim = make_claim(status=ClaimStatus.SUBMITTED)
        with pytest.raises(ValueError):
            claim.approve()

    def test_record_employer_response(self):
        claim = make_claim(status=ClaimStatus.AWAITING_EMPLOYER)
        response = EmployerResponse(
            decision=EmployerDecision.NO_OBJECTION,
            responded_at=datetime(2026, 5, 5),
        )
        claim.record_employer_response(response)
        assert claim.employer_response == response

    def test_attach_document(self):
        claim = make_claim()
        doc = Document(
            document_id=uuid4(),
            type=DocumentType.BIRTH_CERTIFICATE,
            storage_reference="s3://bucket/doc.pdf",
            uploaded_at=datetime(2026, 4, 15),
        )
        claim.attach_document(doc)
        assert len(claim.documents) == 1
        assert claim.documents[0].document_id == doc.document_id
