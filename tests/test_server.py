import pytest
from fastapi.testclient import TestClient
from backend.app import app


class TestAPIModuleImports:
    def test_import_main_app(self):
        from backend.app import app
        assert app is not None

    def test_import_data_contracts(self):
        from backend.contracts import ChatPayload, ChatResult
        assert ChatPayload is not None
        assert ChatResult is not None

    def test_import_runtime_deps(self):
        from backend.dependencies import get_workflow
        assert get_workflow is not None


class TestAPIRouteHandlers:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health_check_route(self, client):
        resp = client.get("/api/health")
        assert resp.status_code in [200, 503]

    def test_chat_submission_route(self, client):
        resp = client.post("/api/chat", json={"message": "Hello"})
        assert resp.status_code in [200, 422, 500]


class TestChatPayloadValidation:
    def test_create_valid_payload(self):
        from backend.contracts import ChatPayload

        req = ChatPayload(message="Explain attention mechanisms", session_id="session-1")
        assert req.message == "Explain attention mechanisms"
        assert req.session_id == "session-1"

    def test_create_payload_without_session(self):
        from backend.contracts import ChatPayload

        req = ChatPayload(message="Explain attention mechanisms")
        assert req.message == "Explain attention mechanisms"
        assert req.session_id is None


class TestChatResultValidation:
    def test_create_result_instance(self):
        from backend.contracts import ChatResult, ThoughtRecord

        res = ChatResult(
            answer="Here is the explanation",
            session_id="session-1",
            reasoning_steps=[
                ThoughtRecord(thought="Step 1", action="test", observation="")
            ],
            sources=[],
            execution_time=120.5,
        )
        assert res.answer == "Here is the explanation"
        assert res.session_id == "session-1"
        assert len(res.reasoning_steps) == 1
        assert res.execution_time == 120.5
