export interface TestCase {
  input: string
  expected: string
  is_hidden: boolean
}

export interface Problem {
  id: string
  title: string
  category: 'algorithms' | 'fastapi' | 'django'
  difficulty: 'easy' | 'medium' | 'hard'
  description: string
  examples: { input: string; output: string; explanation?: string }[]
  constraints: string[]
  starter_code: string
  test_cases: TestCase[]
  time_limit_minutes: number
  tags: string[]
}

export interface ProblemSummary {
  id: string
  title: string
  category: string
  difficulty: string
  tags: string[]
  time_limit_minutes: number
}

export interface SubmissionResult {
  test_index: number
  passed: boolean
  input: string
  expected: string
  actual: string
  error: string | null
}

export interface Session {
  id: string
  problem_id: string
  code: string
  started_at: string
  submitted_at: string | null
  time_remaining_seconds: number | null
  test_results: SubmissionResult[]
  interview_messages: ChatMessage[]
  score: EvaluationResult | null
  status: 'in_progress' | 'submitted' | 'scored'
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ScoreCategory {
  name: string
  score: number
  feedback: string
}

export interface EvaluationResult {
  session_id: string
  overall_score: number
  categories: ScoreCategory[]
  summary: string
  strengths: string[]
  improvements: string[]
}

export interface ExecutionResult {
  results: SubmissionResult[]
  all_passed: boolean
  error: string | null
}
