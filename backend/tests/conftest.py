import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    """TestClient scoped to the entire test session — avoids re-creating the app per test."""
    from main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _clear_sessions(tmp_path, monkeypatch):
    """Redirect session storage to a temp dir so tests don't pollute each other."""
    monkeypatch.setattr("app.config.settings.sessions_dir", str(tmp_path))


@pytest.fixture(scope="session")
def all_problem_ids(client) -> list[str]:
    """Load all problem IDs once for the session."""
    res = client.get("/api/problems")
    return [p["id"] for p in res.json()]


@pytest.fixture(scope="session")
def sample_problem_id(all_problem_ids) -> str:
    """Return a single known problem ID for tests that just need one."""
    return all_problem_ids[0]
