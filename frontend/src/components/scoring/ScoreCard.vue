<script setup lang="ts">
import type { ScoreCategory } from '../../types'

defineProps<{ category: ScoreCategory }>()

function scoreColor(score: number): string {
  if (score >= 80) return 'text-green-400'
  if (score >= 60) return 'text-yellow-400'
  return 'text-red-400'
}

function progressColor(score: number): string {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-yellow-500'
  return 'bg-red-500'
}
</script>

<template>
  <div class="bg-surface-light rounded-xl border border-surface-lighter p-5">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-lg font-semibold text-white">{{ category.name }}</h3>
      <span class="text-2xl font-bold" :class="scoreColor(category.score)">
        {{ category.score }}
      </span>
    </div>
    <div class="w-full bg-surface-lighter rounded-full h-2 mb-3">
      <div
        class="h-2 rounded-full transition-all duration-500"
        :class="progressColor(category.score)"
        :style="{ width: `${category.score}%` }"
      ></div>
    </div>
    <p class="text-sm text-gray-400 leading-relaxed">{{ category.feedback }}</p>
  </div>
</template>
