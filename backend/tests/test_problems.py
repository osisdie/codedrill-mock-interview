import pytest


# ── List problems ────────────────────────────────────────────


class TestListProblems:
    def test_returns_all_problems(self, client):
        res = client.get("/api/problems")
        assert res.status_code == 200
        problems = res.json()
        assert len(problems) >= 70  # we have 73 at time of writing

    def test_each_problem_has_required_fields(self, client):
        res = client.get("/api/problems")
        for p in res.json():
            assert "id" in p
            assert "title" in p
            assert "category" in p
            assert "difficulty" in p

    @pytest.mark.parametrize("category", ["algorithms", "fastapi", "django", "pytest", "python"])
    def test_filter_by_category(self, client, category):
        res = client.get(f"/api/problems?category={category}")
        assert res.status_code == 200
        problems = res.json()
        # Every returned problem must match the category
        for p in problems:
            assert p["category"] == category

    @pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
    def test_filter_by_difficulty(self, client, difficulty):
        res = client.get(f"/api/problems?difficulty={difficulty}")
        assert res.status_code == 200
        for p in res.json():
            assert p["difficulty"] == difficulty

    @pytest.mark.parametrize(
        "category, difficulty",
        [
            ("algorithms", "easy"),
            ("algorithms", "medium"),
            ("fastapi", "medium"),
            ("fastapi", "hard"),
        ],
    )
    def test_filter_by_category_and_difficulty(self, client, category, difficulty):
        res = client.get(f"/api/problems?category={category}&difficulty={difficulty}")
        assert res.status_code == 200
        for p in res.json():
            assert p["category"] == category
            assert p["difficulty"] == difficulty

    def test_filter_nonexistent_category_returns_empty(self, client):
        res = client.get("/api/problems?category=nonexistent")
        assert res.status_code == 200
        assert res.json() == []


# ── Problem detail ───────────────────────────────────────────


class TestProblemDetail:
    @pytest.mark.parametrize("problem_id", ["two-sum", "valid-parentheses", "crud-endpoint"])
    def test_get_known_problems(self, client, problem_id):
        res = client.get(f"/api/problems/{problem_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == problem_id
        assert "description" in data
        assert "starter_code" in data
        assert "test_cases" in data
        assert "examples" in data

    def test_problem_not_found(self, client):
        res = client.get("/api/problems/nonexistent-problem-xyz")
        assert res.status_code == 404

    @pytest.mark.parametrize(
        "field, expected_type",
        [
            ("id", str),
            ("title", str),
            ("category", str),
            ("difficulty", str),
            ("description", str),
            ("starter_code", str),
            ("constraints", list),
            ("examples", list),
            ("test_cases", list),
            ("tags", list),
            ("time_limit_minutes", int),
        ],
    )
    def test_problem_field_types(self, client, sample_problem_id, field, expected_type):
        res = client.get(f"/api/problems/{sample_problem_id}")
        data = res.json()
        assert isinstance(data[field], expected_type), f"{field} should be {expected_type.__name__}"

    def test_problem_has_at_least_one_test_case(self, client, sample_problem_id):
        res = client.get(f"/api/problems/{sample_problem_id}")
        assert len(res.json()["test_cases"]) >= 1

    def test_problem_has_at_least_one_example(self, client, sample_problem_id):
        res = client.get(f"/api/problems/{sample_problem_id}")
        assert len(res.json()["examples"]) >= 1


# ── Validate all problem data integrity ──────────────────────


class TestProblemDataIntegrity:
    @pytest.mark.parametrize("field", ["id", "title", "category", "difficulty"])
    def test_all_summaries_have_field(self, client, field):
        res = client.get("/api/problems")
        for p in res.json():
            assert p.get(field), f"Problem missing {field}: {p}"

    def test_all_problem_ids_are_unique(self, client, all_problem_ids):
        assert len(all_problem_ids) == len(set(all_problem_ids))

    def test_all_problems_have_valid_difficulty(self, client):
        res = client.get("/api/problems")
        valid = {"easy", "medium", "hard"}
        for p in res.json():
            assert p["difficulty"] in valid, f"{p['id']} has invalid difficulty: {p['difficulty']}"

    def test_all_problems_have_valid_category(self, client):
        res = client.get("/api/problems")
        valid = {"algorithms", "fastapi", "django", "pytest", "python"}
        for p in res.json():
            assert p["category"] in valid, f"{p['id']} has invalid category: {p['category']}"
