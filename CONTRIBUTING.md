# Contributing to CodeDrill

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

1. Fork and clone the repo:
   ```bash
   git clone https://github.com/<your-username>/codedrill-mock-interview.git
   cd codedrill-mock-interview
   ```

2. Install dependencies:
   ```bash
   make install
   ```

3. Copy and configure the backend env file:
   ```bash
   cp backend/.env.example backend/.env
   # Add your OpenRouter API key
   ```

4. Run the dev servers:
   ```bash
   make dev-backend   # Terminal 1
   make dev-frontend   # Terminal 2
   ```

## Code Style

- **Python**: Formatted with [Ruff](https://docs.astral.sh/ruff/) (line-length 120)
- **TypeScript**: Standard Vue 3 + TypeScript conventions; checked with `tsc --noEmit`
- **Pre-commit hooks** are configured — install them with `pre-commit install`

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new problem category
fix: correct test case validation
docs: update README badges
refactor: simplify session store logic
```

This is enforced by a pre-commit hook.

## Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```

2. Make your changes and commit using conventional commit messages.

3. Ensure your changes pass:
   - `tsc --noEmit` (frontend type check)
   - `make test-e2e` (E2E tests, requires running backend + frontend)

4. Open a PR against `main` with a clear description of what and why.

## Adding New Problems

Problem definitions live in `backend/data/problems/<category>/`. Each problem is a JSON file following the schema in existing problems (see `two-sum.json` for reference). Make sure to include:

- `id`, `title`, `category`, `difficulty`
- `description` with markdown formatting
- At least 2 visible examples and 3 hidden test cases
- `starter_code` with type hints
- `tags` and `time_limit_minutes`

## Questions?

Open an [issue](https://github.com/osisdie/codedrill-mock-interview/issues) with the "question" template.
