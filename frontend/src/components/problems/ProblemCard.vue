<script setup lang="ts">
import type { ProblemSummary } from '../../types'
import DifficultyBadge from './DifficultyBadge.vue'

defineProps<{ problem: ProblemSummary }>()
defineEmits<{ start: [problemId: string] }>()
</script>

<template>
  <div class="bg-surface-light rounded-lg border border-surface-lighter p-5 hover:border-primary-500/50 transition-colors">
    <div class="flex items-start justify-between mb-3">
      <h3 class="text-lg font-semibold text-white">{{ problem.title }}</h3>
      <DifficultyBadge :difficulty="problem.difficulty" />
    </div>
    <div class="flex flex-wrap gap-1.5 mb-4">
      <span
        v-for="tag in problem.tags"
        :key="tag"
        class="px-2 py-0.5 bg-surface-lighter rounded text-xs text-gray-400"
      >
        {{ tag }}
      </span>
    </div>
    <div class="flex items-center justify-between">
      <span class="text-xs text-gray-500">{{ problem.time_limit_minutes }} min</span>
      <button
        @click="$emit('start', problem.id)"
        class="px-4 py-1.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors"
      >
        Start
      </button>
    </div>
  </div>
</template>
