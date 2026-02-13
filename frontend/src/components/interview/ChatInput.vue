<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{ send: [message: string] }>()

const message = ref('')

function handleSend() {
  const text = message.value.trim()
  if (!text || props.disabled) return
  emit('send', text)
  message.value = ''
}
</script>

<template>
  <div class="flex gap-3">
    <textarea
      v-model="message"
      @keydown.enter.exact.prevent="handleSend"
      :disabled="disabled"
      placeholder="Type your answer..."
      rows="2"
      class="flex-1 bg-surface-lighter border border-surface-lighter rounded-lg px-4 py-3 text-sm text-gray-200 placeholder-gray-500 resize-none focus:outline-none focus:border-primary-500 disabled:opacity-50"
    />
    <button
      @click="handleSend"
      :disabled="disabled || !message.trim()"
      class="self-end px-5 py-3 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
    >
      Send
    </button>
  </div>
</template>
