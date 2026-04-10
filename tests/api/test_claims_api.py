import pytest
from fastapi.testclient import TestClient

from src.app import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestSubmitClaimAPI:
    def test_submit_claim_returns_201(self, client):
        response = client.post("/claims", json={
            "employee_ssn": "123-45-6789",
            "employer_fein": "12-3456789",
            "leave_type": "BONDING",
            "leave_start_date": "2026-05-01",
            "leave_end_date": "2026-07-24",
            "payment_method": {
                "type": "DIRECT_DEPOSIT",
                "bank_routing_number": "021000021",
                "bank_account_number": "123456789",
            },
        })
        assert response.status_code == 201
        assert "claim_id" in response.json()


class TestEmployerResponseAPI:
    def test_no_objection_returns_200(self, client):
        # First submit a claim, then respond
        submit_resp = client.post("/claims", json={
            "employee_ssn": "123-45-6789",
            "employer_fein": "12-3456789",
            "leave_type": "BONDING",
            "leave_start_date": "2026-05-01",
            "leave_end_date": "2026-07-24",
            "payment_method": {
                "type": "CHECK",
                "mailing_address": "123 Main St",
            },
        })
        claim_id = submit_resp.json()["claim_id"]

        response = client.post(f"/claims/{claim_id}/employer-response", json={
            "decision": "NO_OBJECTION",
        })
        assert response.status_code == 200

    def test_objection_returns_200(self, client):
        submit_resp = client.post("/claims", json={
            "employee_ssn": "123-45-6789",
            "employer_fein": "12-3456789",
            "leave_type": "MEDICAL",
            "leave_start_date": "2026-05-01",
            "leave_end_date": "2026-07-24",
            "payment_method": {
                "type": "CHECK",
                "mailing_address": "123 Main St",
            },
        })
        claim_id = submit_resp.json()["claim_id"]

        response = client.post(f"/claims/{claim_id}/employer-response", json={
            "decision": "OBJECTED",
            "reason": "staffing concerns",
        })
        assert response.status_code == 200
