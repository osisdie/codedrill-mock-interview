/**
 * Mock API layer for demo mode.
 * Returns data from the bundled problems JSON and uses localStorage for sessions.
 */
import bundleData from './problems-bundle.json'
import type { Problem, ProblemSummary, Session, ExecutionResult, EvaluationResult } from '../types'

const problems: Problem[] = (bundleData as any).problems

// ── localStorage session helpers ──────────────────────────────

const STORAGE_KEY = 'codedrill-demo-sessions'

function loadSessions(): Session[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

function saveSessions(sessions: Session[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
}

// ── Mock API (same shape as useApi()) ─────────────────────────

function parsePath(path: string) {
  return { path, params: path.split('/').filter(Boolean) }
}

async function mockGet<T>(path: string): Promise<T> {
  const { params } = parsePath(path)

  // GET /problems?category=X&difficulty=Y
  if (params[0] === 'problems' && params.length === 1) {
    const url = new URL(path, 'http://localhost')
    const category = url.searchParams.get('category')
    const difficulty = url.searchParams.get('difficulty')
    let result = problems.map(
      (p): ProblemSummary => ({
        id: p.id,
        title: p.title,
        category: p.category,
        difficulty: p.difficulty,
        tags: p.tags,
        time_limit_minutes: p.time_limit_minutes,
      }),
    )
    if (category) result = result.filter((p) => p.category === category)
    if (difficulty) result = result.filter((p) => p.difficulty === difficulty)
    return result as T
  }

  // GET /problems/:id
  if (params[0] === 'problems' && params.length === 2) {
    const problem = problems.find((p) => p.id === params[1])
    if (!problem) throw new Error('Problem not found')
    return problem as T
  }

  // GET /sessions
  if (params[0] === 'sessions' && params.length === 1) {
    return loadSessions() as T
  }

  // GET /sessions/:id
  if (params[0] === 'sessions' && params.length === 2) {
    const session = loadSessions().find((s) => s.id === params[1])
    if (!session) throw new Error('Session not found')
    return session as T
  }

  throw new Error(`Mock API: unhandled GET ${path}`)
}

async function mockPost<T>(path: string, body?: unknown): Promise<T> {
  const { params } = parsePath(path)

  // POST /sessions
  if (params[0] === 'sessions' && params.length === 1) {
    const { problem_id } = body as { problem_id: string }
    const problem = problems.find((p) => p.id === problem_id)
    if (!problem) throw new Error('Problem not found')
    const session: Session = {
      id: `demo-${Date.now()}`,
      problem_id,
      code: problem.starter_code,
      started_at: new Date().toISOString(),
      submitted_at: null,
      time_remaining_seconds: problem.time_limit_minutes * 60,
      test_results: [],
      interview_messages: [],
      score: null,
      status: 'in_progress',
    }
    const sessions = loadSessions()
    sessions.push(session)
    saveSessions(sessions)
    return session as T
  }

  // POST /execute/run or /execute/submit
  if (params[0] === 'execute') {
    return {
      results: [],
      all_passed: false,
      error: 'Code execution is not available in demo mode. Clone the repo and run locally for full features.',
    } as ExecutionResult as T
  }

  // POST /interview/*
  if (params[0] === 'interview') {
    return { message: 'AI interviews require the full version. Clone the repo to use this feature.' } as T
  }

  // POST /scoring/*
  if (params[0] === 'scoring') {
    return {
      session_id: '',
      overall_score: 0,
      categories: [],
      summary: 'Scoring is not available in demo mode.',
      strengths: [],
      improvements: [],
    } as EvaluationResult as T
  }

  // POST /code-chat
  if (params[0] === 'code-chat') {
    return { message: 'AI chat requires the full version. Clone the repo to use this feature.' } as T
  }

  throw new Error(`Mock API: unhandled POST ${path}`)
}

async function mockPut<T>(path: string, body?: unknown): Promise<T> {
  const { params } = parsePath(path)

  // PUT /sessions/:id
  if (params[0] === 'sessions' && params.length === 2) {
    const sessions = loadSessions()
    const idx = sessions.findIndex((s) => s.id === params[1])
    if (idx === -1) throw new Error('Session not found')
    Object.assign(sessions[idx], body)
    saveSessions(sessions)
    return sessions[idx] as T
  }

  throw new Error(`Mock API: unhandled PUT ${path}`)
}

export function useMockApi() {
  return {
    get: <T>(path: string, _options?: { timeout?: number }) => mockGet<T>(path),
    post: <T>(path: string, body?: unknown, _options?: { timeout?: number }) => mockPost<T>(path, body),
    put: <T>(path: string, body?: unknown, _options?: { timeout?: number }) => mockPut<T>(path, body),
  }
}
