import pytest


class TestCreateSession:
    def test_create_session_returns_201_fields(self, client, sample_problem_id):
        res = client.post("/api/sessions", json={"problem_id": sample_problem_id})
        assert res.status_code == 200
        data = res.json()
        assert data["problem_id"] == sample_problem_id
        assert data["status"] == "in_progress"
        assert data["code"]  # should have starter code
        assert data["id"]

    def test_create_session_invalid_problem(self, client):
        res = client.post("/api/sessions", json={"problem_id": "nonexistent-xyz"})
        assert res.status_code == 404

    @pytest.mark.parametrize("problem_id", ["two-sum", "valid-parentheses", "crud-endpoint"])
    def test_create_session_for_various_problems(self, client, problem_id):
        res = client.post("/api/sessions", json={"problem_id": problem_id})
        assert res.status_code == 200
        data = res.json()
        assert data["problem_id"] == problem_id
        assert data["time_remaining_seconds"] > 0

    def test_session_has_starter_code_from_problem(self, client, sample_problem_id):
        # Get the problem's starter code
        prob_res = client.get(f"/api/problems/{sample_problem_id}")
        starter_code = prob_res.json()["starter_code"]

        # Create session and verify code matches
        sess_res = client.post("/api/sessions", json={"problem_id": sample_problem_id})
        assert sess_res.json()["code"] == starter_code


class TestGetSession:
    def test_get_session_by_id(self, client, sample_problem_id):
        create_res = client.post("/api/sessions", json={"problem_id": sample_problem_id})
        session_id = create_res.json()["id"]

        res = client.get(f"/api/sessions/{session_id}")
        assert res.status_code == 200
        assert res.json()["id"] == session_id

    def test_get_nonexistent_session(self, client):
        res = client.get("/api/sessions/nonexistent-session-id")
        assert res.status_code == 404


class TestUpdateSession:
    @pytest.mark.parametrize(
        "update_field, update_value",
        [
            ("code", "print('updated')"),
            ("status", "submitted"),
            ("time_remaining_seconds", 600),
        ],
    )
    def test_update_single_field(self, client, sample_problem_id, update_field, update_value):
        create_res = client.post("/api/sessions", json={"problem_id": sample_problem_id})
        session_id = create_res.json()["id"]

        res = client.put(f"/api/sessions/{session_id}", json={update_field: update_value})
        assert res.status_code == 200
        assert res.json()[update_field] == update_value

    def test_update_preserves_other_fields(self, client, sample_problem_id):
        create_res = client.post("/api/sessions", json={"problem_id": sample_problem_id})
        data = create_res.json()
        session_id = data["id"]
        original_code = data["code"]

        # Update only status
        res = client.put(f"/api/sessions/{session_id}", json={"status": "submitted"})
        assert res.json()["code"] == original_code  # code unchanged
        assert res.json()["status"] == "submitted"

    def test_update_nonexistent_session(self, client):
        res = client.put("/api/sessions/nonexistent-id", json={"code": "x"})
        assert res.status_code == 404

    def test_update_multiple_fields(self, client, sample_problem_id):
        create_res = client.post("/api/sessions", json={"problem_id": sample_problem_id})
        session_id = create_res.json()["id"]

        res = client.put(
            f"/api/sessions/{session_id}",
            json={"code": "def solve(): pass", "status": "submitted", "time_remaining_seconds": 0},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == "def solve(): pass"
        assert data["status"] == "submitted"
        assert data["time_remaining_seconds"] == 0


class TestListSessions:
    def test_list_sessions_empty(self, client):
        res = client.get("/api/sessions")
        assert res.status_code == 200
        assert res.json() == []

    def test_list_sessions_after_create(self, client, sample_problem_id):
        client.post("/api/sessions", json={"problem_id": sample_problem_id})
        client.post("/api/sessions", json={"problem_id": sample_problem_id})

        res = client.get("/api/sessions")
        assert res.status_code == 200
        assert len(res.json()) == 2
