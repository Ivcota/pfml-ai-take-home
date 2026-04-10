import pytest
from fastapi.testclient import TestClient

from src.app import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestDecideCaseAPI:
    def test_approve_case_returns_200(self, client):
        # This test requires a case to exist — full wiring needed
        response = client.put("/adjudication/cases/00000000-0000-0000-0000-000000000001", json={
            "decision": "APPROVED",
            "adjudicator_notes": "all documentation verified",
        })
        assert response.status_code == 200

    def test_deny_case_returns_200(self, client):
        response = client.put("/adjudication/cases/00000000-0000-0000-0000-000000000001", json={
            "decision": "DENIED",
            "adjudicator_notes": "insufficient documentation",
        })
        assert response.status_code == 200
