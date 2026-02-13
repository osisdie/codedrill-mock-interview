<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '../composables/useApi'
import ScoreCard from '../components/scoring/ScoreCard.vue'
import type { EvaluationResult } from '../types'

const route = useRoute()
const router = useRouter()
const api = useApi()

const sessionId = route.params.sessionId as string
const result = ref<EvaluationResult | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    result.value = await api.post<EvaluationResult>('/scoring/evaluate', { session_id: sessionId })
  } catch (e: any) {
    error.value = e.message || 'Failed to evaluate'
  } finally {
    loading.value = false
  }
})

function overallColor(score: number): string {
  if (score >= 80) return 'text-green-400'
  if (score >= 60) return 'text-yellow-400'
  return 'text-red-400'
}

function overallRing(score: number): string {
  if (score >= 80) return 'border-green-500'
  if (score >= 60) return 'border-yellow-500'
  return 'border-red-500'
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Loading -->
    <div v-if="loading" class="text-center py-20">
      <div class="text-gray-400 text-lg">Evaluating your performance...</div>
      <p class="text-gray-500 text-sm mt-2">AI is analyzing your code and interview responses</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-20">
      <div class="text-red-400 text-lg">{{ error }}</div>
    </div>

    <!-- Results -->
    <template v-else-if="result">
      <!-- Overall Score -->
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-white mb-6">Your Score</h1>
        <div
          class="w-32 h-32 mx-auto rounded-full border-4 flex items-center justify-center"
          :class="overallRing(result.overall_score)"
        >
          <span class="text-4xl font-bold" :class="overallColor(result.overall_score)">
            {{ result.overall_score }}
          </span>
        </div>
        <p class="text-gray-400 mt-4 max-w-xl mx-auto">{{ result.summary }}</p>
      </div>

      <!-- Category Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
        <ScoreCard
          v-for="cat in result.categories"
          :key="cat.name"
          :category="cat"
        />
      </div>

      <!-- Strengths & Improvements -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <div class="bg-surface-light rounded-xl border border-surface-lighter p-5">
          <h3 class="text-lg font-semibold text-green-400 mb-3">Strengths</h3>
          <ul class="space-y-2">
            <li v-for="s in result.strengths" :key="s" class="flex items-start gap-2 text-sm text-gray-300">
              <span class="text-green-400 mt-0.5">+</span>
              {{ s }}
            </li>
          </ul>
        </div>
        <div class="bg-surface-light rounded-xl border border-surface-lighter p-5">
          <h3 class="text-lg font-semibold text-yellow-400 mb-3">Areas to Improve</h3>
          <ul class="space-y-2">
            <li v-for="imp in result.improvements" :key="imp" class="flex items-start gap-2 text-sm text-gray-300">
              <span class="text-yellow-400 mt-0.5">-</span>
              {{ imp }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-center gap-4">
        <button
          @click="router.push({ name: 'problems' })"
          class="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors"
        >
          Try Another Problem
        </button>
        <button
          @click="router.push({ name: 'history' })"
          class="px-6 py-2.5 bg-surface-lighter hover:bg-surface-lighter/80 text-gray-300 text-sm font-medium rounded-lg transition-colors"
        >
          View History
        </button>
      </div>
    </template>
  </div>
</template>
