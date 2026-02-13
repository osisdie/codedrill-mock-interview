<script setup lang="ts">
import type { SubmissionResult } from '../../types'

defineProps<{
  results: SubmissionResult[]
  loading: boolean
}>()
</script>

<template>
  <div class="bg-surface-light rounded-lg border border-surface-lighter p-4">
    <h3 class="text-sm font-semibold text-gray-300 mb-3">Test Results</h3>

    <div v-if="loading" class="text-gray-400 text-sm">Running tests...</div>

    <div v-else-if="results.length === 0" class="text-gray-500 text-sm">
      Click "Run" to test your code with visible test cases.
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="r in results"
        :key="r.test_index"
        class="rounded-lg p-3 text-sm"
        :class="r.passed ? 'bg-green-900/20 border border-green-800/30' : 'bg-red-900/20 border border-red-800/30'"
      >
        <div class="flex items-center gap-2 mb-1">
          <span v-if="r.passed" class="text-green-400 font-bold">PASS</span>
          <span v-else class="text-red-400 font-bold">FAIL</span>
          <span class="text-gray-400">Test {{ r.test_index + 1 }}</span>
        </div>
        <div class="font-mono text-xs space-y-0.5 text-gray-400">
          <div><span class="text-gray-500">Input:</span> {{ r.input }}</div>
          <div><span class="text-gray-500">Expected:</span> {{ r.expected }}</div>
          <div v-if="!r.passed">
            <span class="text-gray-500">Actual:</span>
            <span class="text-red-300">{{ r.actual || 'N/A' }}</span>
          </div>
          <div v-if="r.error" class="text-red-300">Error: {{ r.error }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
