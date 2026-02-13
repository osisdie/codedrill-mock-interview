<script setup lang="ts">
import { useTimerStore } from '../../stores/timerStore'

const timer = useTimerStore()
</script>

<template>
  <div
    class="flex items-center gap-2 px-3 py-1.5 rounded-lg font-mono text-sm font-bold"
    :class="{
      'bg-red-900/50 text-red-400 animate-pulse': timer.isLow,
      'bg-surface-lighter text-gray-300': !timer.isLow && timer.isRunning,
      'bg-surface-lighter text-gray-500': !timer.isRunning,
    }"
  >
    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    {{ timer.formatted }}
  </div>
</template>
