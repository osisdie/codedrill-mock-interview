<script setup lang="ts">
defineProps<{ executing: boolean; submitted: boolean }>()
defineEmits<{ run: []; submit: [] }>()
</script>

<template>
  <div class="flex items-center gap-3">
    <button
      @click="$emit('run')"
      :disabled="executing"
      class="px-4 py-2 bg-surface-lighter hover:bg-surface-lighter/80 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
    >
      {{ executing ? 'Running...' : 'Run' }}
    </button>
    <button
      @click="$emit('submit')"
      :disabled="executing || submitted"
      class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
    >
      {{ submitted ? 'Submitted' : executing ? 'Submitting...' : 'Submit' }}
    </button>
  </div>
</template>
