<script setup lang="ts">
defineProps<{ difficulty: string }>()

const colorMap: Record<string, string> = {
  easy: 'bg-easy/20 text-easy',
  medium: 'bg-medium/20 text-medium',
  hard: 'bg-hard/20 text-hard',
}
</script>

<template>
  <span
    class="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize"
    :class="colorMap[difficulty] ?? 'bg-gray-600 text-gray-300'"
  >
    {{ difficulty }}
  </span>
</template>
