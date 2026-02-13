import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/useApi'
import type { ProblemSummary, Problem } from '../types'

export const useProblemStore = defineStore('problem', () => {
  const api = useApi()
  const problems = ref<ProblemSummary[]>([])
  const currentProblem = ref<Problem | null>(null)
  const loading = ref(false)

  async function fetchProblems(category?: string, difficulty?: string) {
    loading.value = true
    try {
      const params = new URLSearchParams()
      if (category) params.set('category', category)
      if (difficulty) params.set('difficulty', difficulty)
      const query = params.toString()
      problems.value = await api.get<ProblemSummary[]>(`/problems${query ? `?${query}` : ''}`)
    } finally {
      loading.value = false
    }
  }

  async function fetchProblem(id: string) {
    loading.value = true
    try {
      currentProblem.value = await api.get<Problem>(`/problems/${id}`)
    } finally {
      loading.value = false
    }
  }

  return { problems, currentProblem, loading, fetchProblems, fetchProblem }
})
