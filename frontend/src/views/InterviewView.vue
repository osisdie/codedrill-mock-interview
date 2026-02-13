<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '../stores/chatStore'
import ChatMessageComponent from '../components/interview/ChatMessage.vue'
import ChatInput from '../components/interview/ChatInput.vue'

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()
const messagesContainer = ref<HTMLElement | null>(null)

const sessionId = route.params.sessionId as string

onMounted(async () => {
  await chatStore.startInterview(sessionId)
})

watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  },
)

async function handleSend(message: string) {
  await chatStore.sendMessage(sessionId, message)
}

function goToScoring() {
  router.push({ name: 'score', params: { sessionId } })
}
</script>

<template>
  <div class="h-[calc(100vh-4rem)] flex flex-col max-w-4xl mx-auto">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-surface-lighter">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-white">AI Mock Interview</h1>
          <p class="text-sm text-gray-400">Answer the interviewer's questions about your solution</p>
        </div>
        <button
          v-if="chatStore.isComplete"
          @click="goToScoring"
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
        >
          View Score
        </button>
      </div>
    </div>

    <!-- Messages -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto px-6 py-4 space-y-4">
      <ChatMessageComponent
        v-for="(msg, i) in chatStore.messages"
        :key="i"
        :role="msg.role as 'user' | 'assistant'"
        :content="msg.content"
      />
      <div v-if="chatStore.loading" class="flex gap-3">
        <div class="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-bold text-white shrink-0">AI</div>
        <div class="bg-surface-lighter rounded-xl px-4 py-3 text-sm text-gray-400">
          Thinking...
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="px-6 py-4 border-t border-surface-lighter">
      <div v-if="chatStore.isComplete" class="text-center text-sm text-gray-400 py-2">
        Interview complete. Click "View Score" to see your evaluation.
      </div>
      <ChatInput
        v-else
        :disabled="chatStore.loading"
        @send="handleSend"
      />
    </div>
  </div>
</template>
