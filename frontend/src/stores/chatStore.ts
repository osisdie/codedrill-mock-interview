import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/useApi'
import type { ChatMessage } from '../types'

export const useChatStore = defineStore('chat', () => {
  const api = useApi()
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const isComplete = ref(false)

  async function startInterview(sessionId: string) {
    loading.value = true
    messages.value = []
    isComplete.value = false
    try {
      const res = await api.post<{ message: string; is_complete: boolean }>('/interview/start', { session_id: sessionId })
      messages.value.push({ role: 'assistant', content: res.message })
    } finally {
      loading.value = false
    }
  }

  async function sendMessage(sessionId: string, message: string) {
    messages.value.push({ role: 'user', content: message })
    loading.value = true
    try {
      const res = await api.post<{ message: string; is_complete: boolean }>('/interview/chat', {
        session_id: sessionId,
        message,
      })
      messages.value.push({ role: 'assistant', content: res.message })
      isComplete.value = res.is_complete
    } finally {
      loading.value = false
    }
  }

  function reset() {
    messages.value = []
    isComplete.value = false
  }

  return { messages, loading, isComplete, startInterview, sendMessage, reset }
})
