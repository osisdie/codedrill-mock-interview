import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/useApi'
import type { Session, ExecutionResult } from '../types'

export const useSessionStore = defineStore('session', () => {
  const api = useApi()
  const currentSession = ref<Session | null>(null)
  const sessions = ref<Session[]>([])
  const loading = ref(false)
  const executing = ref(false)

  async function createSession(problemId: string): Promise<Session> {
    loading.value = true
    try {
      const session = await api.post<Session>('/sessions', { problem_id: problemId })
      currentSession.value = session
      return session
    } finally {
      loading.value = false
    }
  }

  async function fetchSession(sessionId: string) {
    loading.value = true
    try {
      currentSession.value = await api.get<Session>(`/sessions/${sessionId}`)
    } finally {
      loading.value = false
    }
  }

  async function updateSession(sessionId: string, data: { code?: string; time_remaining_seconds?: number; status?: string }) {
    currentSession.value = await api.put<Session>(`/sessions/${sessionId}`, data)
  }

  async function fetchSessions() {
    loading.value = true
    try {
      sessions.value = await api.get<Session[]>('/sessions')
    } finally {
      loading.value = false
    }
  }

  async function runCode(sessionId: string): Promise<ExecutionResult> {
    executing.value = true
    try {
      return await api.post<ExecutionResult>('/execute/run', { session_id: sessionId })
    } finally {
      executing.value = false
    }
  }

  async function submitCode(sessionId: string): Promise<ExecutionResult> {
    executing.value = true
    try {
      const result = await api.post<ExecutionResult>('/execute/submit', { session_id: sessionId })
      if (currentSession.value) {
        currentSession.value.test_results = result.results
        currentSession.value.status = 'submitted'
      }
      return result
    } finally {
      executing.value = false
    }
  }

  return { currentSession, sessions, loading, executing, createSession, fetchSession, updateSession, fetchSessions, runCode, submitCode }
})
