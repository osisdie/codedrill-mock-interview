# CodeDrill — AI Mock Interview Platform

Practice coding problems, get AI-powered mock interviews, and receive scored feedback — all in one platform.

## Preview

Screenshots of the main workflow: home → problems → coding arena → test results → session history. API docs available at `/docs`.

| Home — Pick a category | Problems — Browse & filter |
|:---:|:---:|
| ![Home](docs/screenshots/mock-interview-home.png) | ![Problems](docs/screenshots/mock-interview-problems.png) |

| Coding Arena — Write & run code | Test Results — Submit & start interview |
|:---:|:---:|
| ![Coding Arena](docs/screenshots/mock-interview-exam.png) | ![Test Results](docs/screenshots/mock-interview-platform.png) |

| Session History | API Documentation |
|:---:|:---:|
| ![History](docs/screenshots/mock-interview-history.png) | ![API](docs/screenshots/mock-interview-api.png) |

## Features

- **33 Coding Problems** — Algorithms, FastAPI, Django, and Pytest problems with automated test cases
- **Python Sandbox** — Secure, isolated code execution for your solutions
- **AI Mock Interview** — Senior technical interviewer powered by LLM (OpenRouter)
- **Scored Feedback** — Detailed evaluation of your code and interview performance

## Tech Stack

| Layer   | Stack                          |
|---------|---------------------------------|
| Backend | FastAPI, Python 3.x             |
| Frontend| Vue 3, Vite, Tailwind CSS, Monaco Editor |
| AI      | OpenRouter (Claude)             |
| E2E Test| Playwright                     |

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ with [pnpm](https://pnpm.io/) (`corepack enable && corepack prepare pnpm@latest --activate`)
- [OpenRouter](https://openrouter.ai/) API key

### Installation

```bash
# Clone the repo
git clone https://github.com/your-org/ai-mock-interview.git
cd ai-mock-interview

# Install dependencies
make install
```

### Configuration

1. Copy the example env file and add your API key:

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Edit `backend/.env`:

   ```
   OPENROUTER_API_KEY=your-openrouter-api-key-here
   ```

3. (Optional) Frontend API base URL — edit `frontend/.env.example` if needed:

   ```
   VITE_API_BASE_URL=http://localhost:8001
   ```

### Run

```bash
# Terminal 1 — backend
make dev-backend

# Terminal 2 — frontend
make dev-frontend
```

- Backend: http://localhost:8001
- Frontend: http://localhost:5573
- API docs: http://localhost:8001/docs

**Docker** (`make up`): Same URLs — backend 8001, frontend 5573.

## Project Structure

```
ai-mock-interview/
├── backend/           # FastAPI app
│   ├── app/
│   │   ├── routers/   # API routes (problems, sessions, execution, interview, scoring)
│   │   ├── services/  # AI, executor, scoring, session logic
│   │   ├── sandbox/   # Code execution sandbox
│   │   └── data/      # Problem definitions (JSON)
│   └── main.py
├── frontend/          # Vue 3 SPA
│   ├── src/
│   └── e2e/           # Playwright E2E tests
├── scripts/           # Start scripts
└── docs/
```

## Ports

| Service  | Host  | Container (Docker) |
|----------|-------|--------------------|
| Backend  | 8001  | 8000               |
| Frontend | 5573  | 5173               |

## Environment Variables

| Variable           | Description                          | Default |
|--------------------|--------------------------------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key (required for AI) | —       |
| `OPENROUTER_MODEL` | Model to use                         | `anthropic/claude-sonnet-4-20250514` |
| `CORS_ORIGINS`     | Allowed CORS origins (frontend URL)   | `["http://localhost:5573"]` |
| `SANDBOX_TIMEOUT`  | Code execution timeout (seconds)    | `10`    |
| `SANDBOX_MAX_MEMORY_MB` | Max memory per run (MB)         | `256`   |

## License

MIT
