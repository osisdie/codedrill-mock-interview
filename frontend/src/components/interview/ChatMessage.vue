<script setup lang="ts">
defineProps<{
  role: 'user' | 'assistant'
  content: string
}>()
</script>

<template>
  <div class="flex gap-3" :class="role === 'user' ? 'flex-row-reverse' : ''">
    <div
      class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
      :class="role === 'assistant' ? 'bg-primary-600 text-white' : 'bg-surface-lighter text-gray-300'"
    >
      {{ role === 'assistant' ? 'AI' : 'You' }}
    </div>
    <div
      class="max-w-[75%] rounded-xl px-4 py-3 text-sm leading-relaxed"
      :class="role === 'assistant'
        ? 'bg-surface-lighter text-gray-200'
        : 'bg-primary-600 text-white'"
    >
      <p class="whitespace-pre-wrap">{{ content }}</p>
    </div>
  </div>
</template>
