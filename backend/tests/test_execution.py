import pytest


class TestExecution:
    @pytest.mark.parametrize("endpoint", ["/api/execute/run", "/api/execute/submit"])
    def test_execute_nonexistent_session(self, client, endpoint):
        res = client.post(endpoint, json={"session_id": "nonexistent"})
        assert res.status_code == 404

    @pytest.mark.parametrize("endpoint", ["/api/execute/run", "/api/execute/submit"])
    def test_execute_missing_body(self, client, endpoint):
        res = client.post(endpoint)
        assert res.status_code == 422  # validation error

    @pytest.mark.parametrize(
        "endpoint, method",
        [
            ("/api/execute/run", "GET"),
            ("/api/execute/submit", "GET"),
        ],
    )
    def test_execute_wrong_method(self, client, endpoint, method):
        res = client.request(method, endpoint)
        assert res.status_code == 405
