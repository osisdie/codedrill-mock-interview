<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useApi } from '../../composables/useApi'

const props = defineProps<{
  problemId: string
  code: string
  selectedText: string | null
}>()

const api = useApi()
const messages = ref<{ role: 'user' | 'assistant'; content: string }[]>([])
const input = ref('')
const loading = ref(false)
const messagesEl = ref<HTMLElement | null>(null)

watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  },
)

async function sendMessage() {
  const text = input.value.trim()
  if (!text || loading.value) return

  // If there's selected text, prepend context to the displayed message
  const displayMsg = props.selectedText
    ? `[Selected: \`${props.selectedText.slice(0, 60)}${props.selectedText.length > 60 ? '...' : ''}\`]\n${text}`
    : text

  messages.value.push({ role: 'user', content: displayMsg })
  input.value = ''
  loading.value = true

  try {
    const res = await api.post<{ reply: string }>('/code-chat', {
      problem_id: props.problemId,
      code: props.code,
      message: text,
      selected_text: props.selectedText,
    })
    messages.value.push({ role: 'assistant', content: res.reply })
  } catch (e: any) {
    messages.value.push({ role: 'assistant', content: `Error: ${e.message}` })
  } finally {
    loading.value = false
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <div class="flex flex-col h-full bg-surface-dark">
    <!-- Header -->
    <div class="px-3 py-2 border-b border-surface-lighter text-xs text-gray-400 flex items-center justify-between shrink-0">
      <span class="font-medium text-gray-300">Ask AI</span>
      <span v-if="selectedText" class="text-primary-400 truncate max-w-[180px] ml-2">
        Selected: {{ selectedText.slice(0, 40) }}{{ selectedText.length > 40 ? '...' : '' }}
      </span>
    </div>

    <!-- Messages -->
    <div ref="messagesEl" class="flex-1 overflow-y-auto px-3 py-2 space-y-3 min-h-0">
      <div v-if="messages.length === 0" class="text-xs text-gray-500 text-center py-4">
        Ask questions about the code, or select code in the editor and ask for an explanation.
      </div>
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="text-xs leading-relaxed"
      >
        <div class="flex items-start gap-2">
          <span
            class="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold mt-0.5"
            :class="msg.role === 'user' ? 'bg-surface-lighter text-gray-300' : 'bg-primary-600 text-white'"
          >
            {{ msg.role === 'user' ? 'U' : 'AI' }}
          </span>
          <p class="whitespace-pre-wrap text-gray-300 min-w-0">{{ msg.content }}</p>
        </div>
      </div>
      <div v-if="loading" class="flex items-center gap-2 text-xs text-gray-400">
        <span class="w-5 h-5 rounded-full bg-primary-600 flex items-center justify-center text-[10px] font-bold text-white shrink-0">AI</span>
        <span class="animate-pulse">Thinking...</span>
      </div>
    </div>

    <!-- Input -->
    <div class="px-3 py-2 border-t border-surface-lighter shrink-0">
      <div class="flex gap-2">
        <textarea
          v-model="input"
          @keydown="handleKeydown"
          :disabled="loading"
          rows="2"
          placeholder="Ask about the code... (Enter to send)"
          class="flex-1 bg-surface-lighter text-gray-200 text-xs rounded-md px-2 py-1.5 resize-none focus:outline-none focus:ring-1 focus:ring-primary-500 placeholder-gray-500"
        />
        <button
          @click="sendMessage"
          :disabled="!input.trim() || loading"
          class="self-end px-3 py-1.5 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-700 disabled:text-gray-500 text-white text-xs font-medium rounded-md transition-colors shrink-0"
        >
          Send
        </button>
      </div>
    </div>
  </div>
</template>
